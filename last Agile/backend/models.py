from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from agno.agent import Agent, RunResponse
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.vectordb.chroma import ChromaDb
from agno.embedder.ollama import OllamaEmbedder
from agno.models.ollama import Ollama
import tempfile
import os

app = FastAPI()

# Global store for agent
agent = None

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(await file.read())
            pdf_path = temp_file.name

        # Load PDF into knowledge base
        pdf_knowledge_base = PDFKnowledgeBase(
            path=pdf_path,
            vector_db=ChromaDb(
                collection="pdf_chatbot",
                embedder=OllamaEmbedder(id="openhermes"),
                persistent_client=True,
            ),
            reader=PDFReader(chunk=True),
        )
        pdf_knowledge_base.load(recreate=False)

        # Create global agent
        global agent
        agent = Agent(
            model=Ollama(id="llama3.2"),
            knowledge=pdf_knowledge_base,
            search_knowledge=True,
            markdown=True
        )

        return JSONResponse(content={"message": "PDF uploaded and processed successfully."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/ask/")
async def ask_question(question: str = Form(...)):
    if agent is None:
        return JSONResponse(status_code=400, content={"error": "No PDF uploaded yet."})

    run: RunResponse = agent.run(question)
    return {"response": run.content}