🚀 AI-Powered Application Setup Guide

This project leverages Ollama, OpenHermes, and LLaMA 3.2, along with a backend powered by FastAPI and a frontend using Streamlit.

---

🛠️ Prerequisites

Before running the project, ensure the following are installed:

- Python 3.10+
- Ollama (https://ollama.com/)
- A code editor (like VS Code) or terminal with multi-tab support

---

🔧 Installation & Setup

## Step 1: Install and Start Ollama

Open a terminal and run:

ollama serve

In the same terminal, pull the required models:

ollama pull openhermes
ollama pull llama3:8b

> You only need to pull models once. Serving must be done every time you start the project.

---

## Step 2: Backend Setup

Open a second terminal:

cd backend
pip install -r requirements.txt
uvicorn models:app --reload

This starts the FastAPI backend on http://127.0.0.1:8000

---

## Step 3: Frontend Setup

Open a third terminal:

cd frontend
pip install -r requirements.txt
streamlit run main.py

This launches the Streamlit UI on http://localhost:8501

---

📁 Project Structure

project/
│
├── backend/
│ ├── models.py
│ └── requirements.txt
│
├── frontend/
│ ├── main.py
│ └── requirements.txt
│
└── README.md

---

✅ Summary

| Task         | Command                                                                      |
| ------------ | ---------------------------------------------------------------------------- |
| Start Ollama | ollama serve                                                                 |
| Pull models  | ollama pull openhermes<br>ollama pull llama3:8b                              |
| Run backend  | cd backend && pip install -r requirements.txt && uvicorn models:app --reload |
| Run frontend | cd frontend && pip install -r requirements.txt && streamlit run main.py      |

---

📣 Notes

- Keep all three terminals running for full functionality.
- Make sure your models are pulled before running backend/frontend.
- If you change model names or paths, update your backend code accordingly.
