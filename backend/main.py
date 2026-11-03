
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from rag.conversational_retrieval import (
    create_retrievers,
    conversational_search
)

from retrieval.reranker import load_reranker

from rag.conversational_rag import update_chat_history


# -----------------------------------------
# GLOBAL APPLICATION RESOURCES
# -----------------------------------------

vector_store = None
bm25_retriever = None
reranker = None

# Store separate conversation histories by session ID
chat_histories = {}


# -----------------------------------------
# INITIALIZE RAG PIPELINE
# -----------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    global vector_store
    global bm25_retriever
    global reranker

    print("\nInitializing CyberShield AI...")

    vector_store, bm25_retriever = create_retrievers()

    print("\nLoading Cross-Encoder reranker...")

    reranker = load_reranker()

    print("\nCyberShield AI is ready!")

    yield

    print("\nCyberShield AI is shutting down...")


# -----------------------------------------
# FASTAPI APPLICATION
# -----------------------------------------

app = FastAPI(
    title="CyberShield AI API",
    description=(
        "Cybersecurity Threat Investigation "
        "and Intelligence Assistant"
    ),
    version="1.0.0",
    lifespan=lifespan
)


# -----------------------------------------
# REQUEST MODEL
# -----------------------------------------

class QuestionRequest(BaseModel):

    question: str = Field(min_length=1)

    session_id: str = Field(
        default="default",
        min_length=1,
        max_length=100
    )


# -----------------------------------------
# HOME ENDPOINT
# -----------------------------------------

@app.get("/")
def home():

    return {
        "message": "Welcome to CyberShield AI",
        "documentation": "/docs",
        "health": "/health"
    }


# -----------------------------------------
# HEALTH CHECK
# -----------------------------------------

@app.get("/health")
def health_check():

    if vector_store is None or reranker is None:

        return {
            "status": "initializing",
            "application": "CyberShield AI"
        }

    return {
        "status": "healthy",
        "application": "CyberShield AI"
    }


# -----------------------------------------
# ASK CYBERSHIELD AI
# -----------------------------------------

@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    if vector_store is None or reranker is None:

        raise HTTPException(
            status_code=503,
            detail="RAG pipeline is not ready."
        )

    try:

        # Get or create conversation history
        chat_history = chat_histories.setdefault(
            request.session_id,
            []
        )

        # Run the existing conversational RAG pipeline
        answer, retrieved_count = conversational_search(
            question,
            chat_history,
            vector_store,
            bm25_retriever,
            reranker
        )

        # Save the conversation
        update_chat_history(
            chat_history,
            question,
            answer
        )

        return {
            "session_id": request.session_id,
            "question": question,
            "answer": answer,
            "retrieved_documents": retrieved_count
        }

    except Exception as error:

        print("\nAPI Error:", str(error))

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question."
        )

