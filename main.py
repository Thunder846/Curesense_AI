from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Literal, Dict, List
from dotenv import load_dotenv
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_mistralai import ChatMistralAI

load_dotenv()
model = ChatMistralAI(model='mistral-small-2506', api_key=os.getenv("MISTRAL_API_KEY"))

app = FastAPI()

# in-memory storage: session_id -> history list
sessions: Dict[str, List] = {}

# =========================================================
# Pydantic models for structured output
# =========================================================
class SymptomAssessment(BaseModel):
    severity: Literal["mild", "moderate", "severe"]
    remedy_or_action: str
    disclaimer: str

class MedicineInfo(BaseModel):
    medicine_name: str
    used_for: str
    common_side_effects: str
    disclaimer: str

symptom_parser = PydanticOutputParser(pydantic_object=SymptomAssessment)
medicine_parser = PydanticOutputParser(pydantic_object=MedicineInfo)

symptom_classify_prompt = ChatPromptTemplate.from_messages([
    ('system', """You are a cautious health-assistant. Classify the symptom severity.
- mild: suggest a safe home/ayurvedic remedy
- moderate: advise seeing a doctor, no remedy
- severe: say "seek immediate medical attention"
Never suggest allopathic medicine names or dosages.
{format_instructions}"""),
    ("human", "{symptom}")
])

symptom_chat_prompt = ChatPromptTemplate.from_messages([
    ('system', """You are continuing a symptom-advice conversation.
Use chat history to answer follow-ups consistently.
Never suggest allopathic medicine names or dosages."""),
    ("placeholder", "{chat_history}"),
    ("human", "{question}")
])

medicine_lookup_prompt = ChatPromptTemplate.from_messages([
    ('system', """You are a medicine information assistant.
Explain what the medicine is generally used for and common side effects.
Do NOT give dosage instructions. Add a disclaimer to confirm with a pharmacist/doctor.
{format_instructions}"""),
    ("human", "{medicine_name}")
])

medicine_chat_prompt = ChatPromptTemplate.from_messages([
    ('system', """You are continuing a medicine-information conversation.
Use chat history to answer follow-ups consistently.
Never give dosage instructions."""),
    ("placeholder", "{chat_history}"),
    ("human", "{question}")
])

# =========================================================
# Request schemas
# =========================================================
class StartRequest(BaseModel):
    session_id: str
    mode: Literal["symptom", "medicine"]
    text: str

class FollowUpRequest(BaseModel):
    session_id: str
    mode: Literal["symptom", "medicine"]
    question: str

# =========================================================
# Routes
# =========================================================
@app.post("/start")
def start(req: StartRequest):
    history = []
    if req.mode == "symptom":
        final_prompt = symptom_classify_prompt.invoke({
            "symptom": req.text,
            "format_instructions": symptom_parser.get_format_instructions()
        })
        response = model.invoke(final_prompt)
        result = symptom_parser.parse(response.content)
        reply = f"Severity: {result.severity}\nAdvice: {result.remedy_or_action}\nNote: {result.disclaimer}"
        history.append(HumanMessage(content=req.text))
        history.append(AIMessage(content=f"Severity: {result.severity}. Advice: {result.remedy_or_action}"))
    else:
        final_prompt = medicine_lookup_prompt.invoke({
            "medicine_name": req.text,
            "format_instructions": medicine_parser.get_format_instructions()
        })
        response = model.invoke(final_prompt)
        result = medicine_parser.parse(response.content)
        reply = f"Used for: {result.used_for}\nSide effects: {result.common_side_effects}\nNote: {result.disclaimer}"
        history.append(HumanMessage(content=req.text))
        history.append(AIMessage(content=f"Used for: {result.used_for}. Side effects: {result.common_side_effects}"))

    sessions[req.session_id] = history
    return {"reply": reply}

@app.post("/followup")
def followup(req: FollowUpRequest):
    history = sessions.get(req.session_id, [])
    prompt = symptom_chat_prompt if req.mode == "symptom" else medicine_chat_prompt

    final_prompt = prompt.invoke({"chat_history": history, "question": req.question})
    response = model.invoke(final_prompt)

    history.append(HumanMessage(content=req.question))
    history.append(AIMessage(content=response.content))
    sessions[req.session_id] = history

    return {"reply": response.content}

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")