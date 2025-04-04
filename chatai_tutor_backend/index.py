import os
from fastapi import FastAPI
from pydantic import BaseModel
from huggingface_hub import InferenceClient
from db.models import create_tables
from db.crud import save_mistake, get_mistakes
from fastapi.middleware.cors import CORSMiddleware
import difflib
from dotenv import load_dotenv



app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Load environment variables manually
load_dotenv()

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
    proficiency: str 


def find_incorrect_words(original: str, corrected: str):
    """Identifies incorrect words by comparing the original and corrected text."""
    original_words = original.split()
    corrected_words = corrected.split()
    
    incorrect_words = []
    
    matcher = difflib.SequenceMatcher(None, original_words, corrected_words)
    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
        if opcode in ("replace", "delete"):  
            wrong_word = " ".join(original_words[i1:i2])
            correct_word = " ".join(corrected_words[j1:j2]) if j1 < len(corrected_words) else ""
            
            # Filter out cases where the correction is minor (e.g., punctuation changes)
            if wrong_word != correct_word:
                incorrect_words.append((wrong_word, correct_word))

    return incorrect_words

@app.post("/chat")
def chat_with_bot(request: ChatRequest):
   
    
   
    proficiency_instruction = {
        "basic": "Use simple language and explain the corrections.",
        "intermediate": "Provide corrections with brief explanations.",
        "expert": "Give only the corrected sentence."
    }.get(request.proficiency, "Provide a structured correction.")

    prompt = (
        f"You are an expert {request.target_lang} tutor. "
        f"The user is fluent in {request.known_lang}. {proficiency_instruction}\n"
        f"Correct the following sentence and return only the corrected version.\n\n"
        f"Sentence: {request.message}\n"
        f"Correction:"
    )

    response = client.text_generation(prompt=prompt, max_new_tokens=200).strip()

    # Debugging: Print raw model response
    print(f"Raw Model Response: {response}")  

    # Extract correction text properly
    correction_text = response.split("Correction:")[-1].strip() if "Correction:" in response else response.strip()

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

    return {
        "response": correction_text,
        "proficiency": request.proficiency,
        "known_language": request.known_lang,
        "incorrect_words": incorrect_words,
    }

@app.get("/summary/{user_id}")
def get_summary(user_id: str):
    mistakes = get_mistakes(user_id)
    print(f"Database Mistakes Retrieved: {mistakes}")  # Debugging

    if not mistakes:
        return {"mistakes": []}

    # Ensure correct keys for frontend
    return {"mistakes": [{"wrong_word": m["mistake"], "correction": m["correction"]} for m in mistakes]}

from collections import Counter

@app.get("/review/{user_id}")
def get_review(user_id: str):
    mistakes = get_mistakes(user_id)

    print(f"Database Mistakes Retrieved: {mistakes}")  # Debugging output

    if not mistakes:
        return {"message": "No mistakes found!", "summary": [], "focus_areas": []}

    try:
        mistake_counts = Counter([m["mistake"] for m in mistakes])  # Ensure consistency
    except KeyError as e:
        return {"error": f"Invalid data format: {e}"}

    # Generate review summary
    summary = [{"mistake": mistake, "count": count} for mistake, count in mistake_counts.items()]
    focus_areas = list(mistake_counts.keys())[:5]  # Top 5 focus areas

    return {
        "message": "Here’s an overview of your mistakes and areas to improve.",
        "summary": summary,
        "focus_areas": focus_areas,
    }
    

