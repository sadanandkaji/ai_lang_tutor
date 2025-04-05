import os
import difflib
from collections import Counter
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from langchain_core.prompts import PromptTemplate
from fastapi.middleware.cors import CORSMiddleware
from langchain_huggingface import HuggingFaceEndpoint
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from collections import Counter
from models.schema import get_db
from models.crud import add_mistake, get_mistakes_by_user
from dotenv import load_dotenv
load_dotenv()

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

llm = HuggingFaceEndpoint(
    repo_id="tiiuae/falcon-7b-instruct",
    task="text-generation",
    huggingfacehub_api_token=api_key,
)

class ChatRequest(BaseModel):
    user_id: str
    known_lang: str
    target_lang: str
    message: str
    proficiency: str

def find_incorrect_words(original: str, corrected: str):
    original_words = original.split()
    corrected_words = corrected.split()
    incorrect_words = []

    matcher = difflib.SequenceMatcher(None, original_words, corrected_words)
    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
        if opcode in ("replace", "delete"):
            wrong_word = " ".join(original_words[i1:i2])
            correct_word = " ".join(corrected_words[j1:j2]) if j1 < len(corrected_words) else ""
            if wrong_word != correct_word:
                incorrect_words.append((wrong_word, correct_word))
    return incorrect_words

template = """You are an expert {target_lang} tutor. 
The user is fluent in {known_lang}. {proficiency_instruction}
Correct the following sentence and return only the corrected version.

Sentence: {message}
Correction:
"""
prompt = PromptTemplate(
    input_variables=["target_lang", "known_lang", "proficiency_instruction", "message"],
    template=template,
)


chain = prompt | llm


@app.post("/chat")
async def chat_with_bot(request: ChatRequest, db: Session = Depends(get_db)):
    proficiency_instruction = {
        "basic": "Use simple language and explain the corrections.",
        "intermediate": "Provide corrections with brief explanations.",
        "expert": "Give only the corrected sentence.",
    }.get(request.proficiency, "Provide a structured correction.")

    response = chain.invoke({
       "target_lang": request.target_lang,
    "known_lang": request.known_lang,
    "proficiency_instruction": proficiency_instruction,
    "message": request.message
    }).strip()


    correction_text = response.split("Correction:")[-1].strip() if "Correction:" in response else response.strip()
    incorrect_words = find_incorrect_words(request.message, correction_text)

    if incorrect_words:
        for wrong_word, correct_word in incorrect_words:
           await add_mistake(db, request.user_id, wrong_word, correct_word)

    return {
        "response": correction_text,
        "proficiency": request.proficiency,
        "known_language": request.known_lang,
        "incorrect_words": incorrect_words,
    }

@app.get("/summary/{user_id}")
async def get_summary(user_id: str, db: AsyncSession = Depends(get_db)):
    mistakes = await get_mistakes_by_user(db, user_id)
    return {
        "mistakes": [{"wrong_word": m.mistake, "correction": m.correction} for m in mistakes]
    } if mistakes else {"mistakes": []}

@app.get("/review/{user_id}")
async def get_review(user_id: str, db: AsyncSession = Depends(get_db)):
    mistakes = await get_mistakes_by_user(db, user_id)
    if not mistakes:
        return {"message": "No mistakes found!", "summary": [], "focus_areas": []}

    mistake_counts = Counter([m.mistake for m in mistakes])
    summary = [{"mistake": mistake, "count": count} for mistake, count in mistake_counts.items()]
    focus_areas = list(mistake_counts.keys())[:5]

    return {
        "message": "Here’s an overview of your mistakes and areas to improve.",
        "summary": summary,
        "focus_areas": focus_areas,
    }
