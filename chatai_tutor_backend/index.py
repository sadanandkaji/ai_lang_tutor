import os
from fastapi import FastAPI
from pydantic import BaseModel
from huggingface_hub import InferenceClient
from db.models import create_tables
from db.crud import save_mistake, get_mistakes
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)


api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
if not api_key:
    raise ValueError("HUGGINGFACEHUB_API_TOKEN is missing from environment variables.")


model_id = "tiiuae/falcon-7b-instruct"  


client = InferenceClient(model=model_id, token=api_key)

# Create database tables
create_tables()

class ChatRequest(BaseModel):
    user_id: str
    known_lang: str
    target_lang: str
    message: str
import difflib

def find_incorrect_words(original: str, corrected: str):
    original_words = original.split()
    corrected_words = corrected.split()
    
    incorrect_words = []
    
    matcher = difflib.SequenceMatcher(None, original_words, corrected_words)
    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
        if opcode in ("replace", "delete"):  # Words that were changed or removed
            wrong_word = " ".join(original_words[i1:i2])
            correct_word = " ".join(corrected_words[j1:j2]) if j1 < len(corrected_words) else ""
            incorrect_words.append((wrong_word, correct_word))

    return incorrect_words

@app.post("/chat")
def chat_with_bot(request: ChatRequest):
    prompt = (
        f"You are an expert {request.target_lang} tutor. "
        f"Correct the following sentence and return only the corrected version.\n\n"
        f"Sentence: {request.message}\n"
        f"Correction:"
    )

    response = client.text_generation(prompt=prompt, max_new_tokens=200).strip()

    # Debugging: Print raw model response
    print(f"Raw Model Response: {response}")  

    # Ensure the response contains corrections
    if "Correction:" in response:
        correction_text = response.split("Correction:")[1].strip()
    else:
        correction_text = response.strip()

    print(f"Extracted Correction: {correction_text}")  # Debugging output

    # Find incorrect words
    incorrect_words = find_incorrect_words(request.message, correction_text)

    print(f"Incorrect Words Found: {incorrect_words}")  # Debugging output

    # Save incorrect words to database
    if incorrect_words:
        for wrong_word, correct_word in incorrect_words:
            print(f"Saving mistake: {wrong_word} -> {correct_word}")  # Debugging output
            save_mistake(request.user_id, wrong_word, correct_word)
    else:
        print("No mistakes detected.")

    return {"response": response}

@app.get("/summary/{user_id}")
def get_summary(user_id: str):
    mistakes = get_mistakes(user_id)
    print(f"Database Mistakes Retrieved: {mistakes}")  # Debugging

    if not mistakes:
        return {"mistakes": []}

    # Ensure correct keys for frontend
    return {"mistakes": [{"wrong_word": m["mistake"], "correction": m["correction"]} for m in mistakes]}

