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

@app.post("/chat")
def chat_with_bot(request: ChatRequest):
    prompt = f"You are a helpful tutor for {request.target_lang}. Correct mistakes and explain errors.\n\nUser: {request.message}"
    
    response = client.text_generation(prompt=prompt, max_new_tokens=200)
    
    # Store mistake if correction is given
    if "Correction:" in response:
        mistake = request.message
        correction = response.split("Correction:")[1].strip()
        save_mistake(request.user_id, mistake, correction)

    return {"response": response}

# @app.get("/summary/{user_id}")
# def get_summary(user_id: str):
#     mistakes = get_mistakes(user_id)

#     if not mistakes:
#         return {"message": "No mistakes recorded. Great job!"}

#     summary = "Here's where you need improvement:\n"
#     for mistake, correction in mistakes:
#         summary += f"- ❌ {mistake}\n✅ {correction}\n"

#     return {"summary": summary}
@app.get("/summary/{user_id}")
def get_summary(user_id: str):
    mistakes = get_mistakes(user_id)

    if not mistakes:
        return {"message": "No mistakes recorded. Great job!"}

    return {"mistakes": mistakes}