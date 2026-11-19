<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-🦜-1C3C3C?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Mistral_AI-FF7000?style=for-the-badge&logo=data:image/svg+xml;base64,&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
</p>

<h1 align="center">🩺 CureSense AI</h1>
<h3 align="center"><em>Know Before You Go — AI-Powered Health Guidance</em></h3>

<p align="center">
  An intelligent health assistant that classifies symptom severity, recommends safe home remedies, and provides medicine information — while drawing a hard line when professional care is needed.
</p>

---

## ✨ What It Does

CureSense AI is a conversational health guidance tool with **two modes**:

| Mode | What It Does | Example |
|------|-------------|---------|
| 🌿 **Symptom Advisor** | Classifies symptoms as *mild*, *moderate*, or *severe* and responds accordingly | *"I have a dry cough since morning"* → **MILD** — Try warm water with honey & turmeric |
| 💊 **Medicine Info** | Explains what a medicine treats and its common side effects (never gives dosages) | *"Paracetamol"* → Used for fever/pain, may cause nausea |

### Key Design Principles

- 🟢 **Mild** → Safe home / ayurvedic remedy
- 🟡 **Moderate** → Advise seeing a doctor + interim home remedy
- 🔴 **Severe** → *"Seek immediate medical attention"* with emergency contacts (India-specific)
- 🚫 **Never** prescribes allopathic medicine names or dosages
- 🔄 **Multi-turn conversations** — ask follow-up questions just like talking to a person

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│                   Browser UI                      │
│         (HTML / CSS / Vanilla JS)                 │
│   ┌─────────────┐    ┌──────────────────┐        │
│   │  Symptom     │    │  Medicine Info   │        │
│   │  Advisor     │    │  Lookup          │        │
│   └──────┬───────┘    └────────┬─────────┘        │
└──────────┼─────────────────────┼──────────────────┘
           │     REST API        │
           ▼                     ▼
┌──────────────────────────────────────────────────┐
│              FastAPI Backend                      │
│                                                   │
│   /start     → First message (structured output) │
│   /followup  → Multi-turn chat with history      │
│                                                   │
│   ┌────────────────────────────────────────┐     │
│   │         LangChain Pipeline             │     │
│   │                                        │     │
│   │  ChatPromptTemplate                    │     │
│   │       ↓                                │     │
│   │  Mistral AI (mistral-small-2506)       │     │
│   │       ↓                                │     │
│   │  PydanticOutputParser                  │     │
│   │  (SymptomAssessment / MedicineInfo)    │     │
│   └────────────────────────────────────────┘     │
│                                                   │
│   In-Memory Session Store (chat history)          │
└──────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | [Mistral AI](https://mistral.ai/) (`mistral-small-2506`) |
| **Orchestration** | [LangChain](https://www.langchain.com/) — Prompts, Output Parsers, Message History |
| **Structured Output** | [Pydantic](https://docs.pydantic.dev/) — `SymptomAssessment` & `MedicineInfo` models |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) with Uvicorn |
| **Frontend** | Vanilla HTML/CSS/JS with Google Fonts (Inter + Fraunces) |
| **Env Management** | `python-dotenv` |

---

## 📁 Project Structure

```
CureSense-AI/
├── main.py                 # FastAPI app — routes, LLM chains, session management
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not committed)
├── .gitignore
│
├── chatmodels/
│   └── chat.py             # Standalone CLI version (terminal-based chat loop)
│
├── embeddingmodels/        # Reserved for future RAG / embedding features
│
└── static/
    ├── index.html          # Landing page + chat UI
    ├── style.css           # Fully custom design system (no framework)
    └── script.js           # Frontend logic — mode selection, API calls, chat rendering
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A [Mistral AI API key](https://console.mistral.ai/)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/CureSense-AI.git
cd CureSense-AI

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
#    Create a .env file in the root directory:
echo MISTRAL_API_KEY=your_mistral_api_key_here > .env
```

### Run the Web App

```bash
uvicorn main:app --reload
```

Then open **http://localhost:8000** in your browser.

### Run the CLI Version

```bash
python chatmodels/chat.py
```

---

## 🔑 API Endpoints

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `GET` | `/` | Serves the web UI | — |
| `POST` | `/start` | Initiates a new conversation | `{ session_id, mode, text }` |
| `POST` | `/followup` | Sends a follow-up message in an existing session | `{ session_id, mode, question }` |

### Example Request

```bash
curl -X POST http://localhost:8000/start \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo_01", "mode": "symptom", "text": "I have a sore throat and mild fever"}'
```

### Example Response

```json
{
  "reply": "Severity: mild\nAdvice: Gargle with warm salt water 2-3 times a day. Drink warm turmeric milk before bed.\nNote: This is general guidance. If symptoms persist beyond 3 days, please consult a doctor."
}
```

---

## 🎨 UI Highlights

- **Custom design system** — no CSS framework, hand-crafted tokens and components
- **Glassmorphic sticky navbar** with backdrop blur
- **Animated hero section** with a live chat mockup and SVG pulse-line drawing animation
- **Severity color-coding** — MILD (gold), MODERATE (amber), SEVERE (red) tags rendered inline
- **Responsive layout** — mobile-first grid that adapts from 1 to 2+ columns
- **Typing indicator** with CSS keyframe animation
- **Accessible** — semantic HTML, focus-visible states, `prefers-reduced-motion` support

---

## 🛡️ Safety by Design

CureSense AI is built with guardrails baked into the prompts themselves:

```
✅  Classifies severity before giving any advice
✅  Suggests home / ayurvedic remedies for mild symptoms
✅  Tells you to see a doctor for moderate cases
✅  Directs to emergency services for severe cases
❌  Never names a specific allopathic medicine to take
❌  Never suggests dosage amounts
❌  Never claims to replace a real medical diagnosis
```

---

## 🗺️ Roadmap

- [ ] Persistent session storage (database-backed)
- [ ] RAG pipeline with medical knowledge base (via FAISS embeddings)
- [ ] Multi-language support (Hindi, Tamil, Telugu)
- [ ] User authentication and chat history
- [ ] Deploy to cloud (Render / Railway / AWS)

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Varun Raj**  

---

<p align="center">
  <strong>⚠️ Disclaimer:</strong> CureSense AI is a guidance tool, not a medical diagnosis system.<br>
  Always consult a qualified healthcare professional for medical decisions.
</p>
