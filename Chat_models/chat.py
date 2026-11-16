from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel
from typing import Literal
from langchain_core.output_parsers import PydanticOutputParser
from langchain_mistralai import ChatMistralAI

load_dotenv()
model = ChatMistralAI(model='mistral-small-2506')


# MODE 1: SYMPTOM ADVISOR

class SymptomAssessment(BaseModel):
    severity: Literal["mild", "moderate", "severe"]
    remedy_or_action: str
    disclaimer: str

symptom_parser = PydanticOutputParser(pydantic_object=SymptomAssessment)

symptom_classify_prompt = ChatPromptTemplate.from_messages([
    ('system', """
You are a cautious health-assistant. Classify the symptom severity.
- mild: suggest a safe home/ayurvedic remedy
- moderate: advise seeing a doctor, but also suggest a safe home/ayurvedic remedy that a person do while waiting for a consultation so the symptom doesn't worsen
- severe: say "seek immediate medical attention give emergency number of ambulance as my users are from india so give them number accordingly" 
Never suggest allopathic medicine names or dosages.
{format_instructions}
"""),
    ("human", "{symptom}")
])

symptom_chat_prompt = ChatPromptTemplate.from_messages([
    ('system', """
You are continuing a symptom-advice conversation.
Use chat history to answer follow-ups consistently.
Never suggest allopathic medicine names or dosages.
"""),
    ("placeholder", "{chat_history}"),
    ("human", "{question}")
])

# MODE 2: MEDICINE INFO

class MedicineInfo(BaseModel):
    medicine_name: str
    used_for: str
    common_side_effects: str
    disclaimer: str

medicine_parser = PydanticOutputParser(pydantic_object=MedicineInfo)

medicine_lookup_prompt = ChatPromptTemplate.from_messages([
    ('system', """
You are a medicine information assistant.
Given a medicine name, explain what it is generally used for and common side effects.
Do NOT give dosage instructions. Always add a disclaimer to confirm with a pharmacist/doctor.
{format_instructions}
"""),
    ("human", "{medicine_name}")
])

medicine_chat_prompt = ChatPromptTemplate.from_messages([
    ('system', """
You are continuing a medicine-information conversation.
Use chat history to answer follow-ups consistently.
Never give dosage instructions.
"""),
    ("placeholder", "{chat_history}"),
    ("human", "{question}")
])



# TERMINAL LOOP

def run_symtom_mode():
    history = []
    print("Welcome to Symptom Advisor Mode. Type 'exit' to quit.")

    symptom = input("Describe your symptom: ")
    final_prompt = symptom_classify_prompt.invoke({
        "symptom":symptom, 
        "format_instructions":symptom_parser.get_format_instructions()
        })
    response = model.invoke(final_prompt)
    result = symptom_parser.parse(response.content)

    print(f"Severity: {result.severity}")
    print(f"Remedy/Action: {result.remedy_or_action}")  
    print(f"Disclaimer: {result.disclaimer}")

    history.append(HumanMessage(content=symptom))
    history.append(AIMessage(content = f"Severity: {result.severity}. Remedy/Action: {result.remedy_or_action}"))

    while True:
        question = input("Anything else you want to ask about your symptom? (Type 'exit' to quit): ")
        if question.lower() == 'exit':
            break

        final_prompt = symptom_chat_prompt.invoke({
            "chat_history": history,
            "question": question
        })

        response = model.invoke(final_prompt)
        print(f"Response: {response.content}\n")

        history.append(HumanMessage(content=question))
        history.append(AIMessage(content=response.content))


def run_medicine_mode():
    history = []
    print("\n Welcome to Medicine Info Mode. Type 'exit' to quit.")
    medicine_name = input("Which medicine do you want to know about? ")
    final_prompt = medicine_lookup_prompt.invoke({
        "medicine_name": medicine_name, 
        "format_instructions":medicine_parser.get_format_instructions()
        })
    response = model.invoke(final_prompt)
    result = medicine_parser.parse(response.content)

    print(f"Medicine Name: {result.medicine_name}")
    print(f"Used For: {result.used_for}")  
    print(f"Common Side Effects: {result.common_side_effects}")
    print(f"Disclaimer: {result.disclaimer}\n")
    
    history.append(HumanMessage(content=medicine_name))
    history.append(AIMessage(content = f"Medicine Name: {result.medicine_name}. Used For: {result.used_for}. Common Side Effects: {result.common_side_effects}"))

    while True:
        question = input("Anything else you want to ask about this medicine? (Type 'exit' to quit): ")
        if question.lower() == 'exit':
            break

        final_prompt = medicine_chat_prompt.invoke({
            "chat_history": history,
            "question": question
        })

        response = model.invoke(final_prompt)
        print(f"Response: {response.content}\n")

        history.append(HumanMessage(content=question))
        history.append(AIMessage(content=response.content))


def main():
    while True:
        print("=" * 50)
        print("  CureSense AI — Choose an option")
        print("=" * 50)
        print("1. Symptom Advisor (remedy/consultation guidance)")
        print("2. Medicine Info")
        print("3. Exit")

        choice = input("\nEnter choice (1/2/3): ")

        if choice == "1":
            run_symtom_mode()
        elif choice == "2":
            run_medicine_mode()
        elif choice == "3":
            print("Goodbye! Take care !!")
            break
        else:
            print("Invalid choice, try again.\n")


if __name__ == "__main__":
    main()
