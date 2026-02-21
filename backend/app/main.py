"""
MediVault - Main FastAPI Application
Backend API only - serves frontend static files
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.config import config
from app.schemas import (
    LoginRequest, LoginResponse, 
    ChatbotRequest, ChatbotResponse, 
    SummaryResponse, RAGRebuildResponse
)
from app.services.rag_service import RAGService

# Initialize FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    debug=config.DEBUG
)

# CORS middleware to allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup frontend directory
frontend_dir = config.FRONTEND_DIR

# Create frontend directory if it doesn't exist
frontend_dir.mkdir(parents=True, exist_ok=True)

# Mount frontend static files directory (serves CSS, JS, and other assets)
# This allows files to be accessed as /css/styles.css, /js/auth.js, etc.
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# Initialize RAG service (lazy initialization on first use)
rag_service = None

def get_rag_service() -> RAGService:
    """Get or create RAG service instance"""
    global rag_service
    if rag_service is None:
        print("Initializing RAG service...")
        rag_service = RAGService()
        # Auto-ingest documents on first initialization
        try:
            result = rag_service.ingest_documents(rebuild=False)
            print(f"RAG initialization: {result['message']}")
        except Exception as e:
            print(f"Warning: Could not auto-ingest documents: {e}")
    return rag_service


@app.get("/")
async def index():
    """Serve frontend index.html"""
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Frontend not found. Please create frontend/index.html"}


@app.get("/dashboard")
async def dashboard():
    """Serve dashboard page"""
    dashboard_file = frontend_dir / "dashboard.html"
    if dashboard_file.exists():
        return FileResponse(str(dashboard_file))
    return {"message": "Dashboard not found"}


@app.get("/chatbot")
async def chatbot():
    """Serve chatbot page"""
    chatbot_file = frontend_dir / "chatbot.html"
    if chatbot_file.exists():
        return FileResponse(str(chatbot_file))
    return {"message": "Chatbot page not found"}


@app.post("/api/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Login endpoint - verifies credentials from config"""
    # Check credentials against config
    if login_data.user_id == config.USERNAME and login_data.password == config.PASSWORD:
        return LoginResponse(
            success=True,
            message="Login successful",
            redirect_url="/chatbot"
        )
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )


@app.post("/api/chatbot/query", response_model=ChatbotResponse)
async def chatbot_query(request: ChatbotRequest):
    """Handle chatbot questions using RAG and return answers (recommendations only when requested)"""
    try:
        # Get RAG service (initializes on first use)
        rag = get_rag_service()
        
        # Query using RAG
        result = rag.query(request.question)
        
        return ChatbotResponse(
            answer=result["answer"],
            recommendations=result.get("recommendations", []),
            sources=result.get("sources", []),
            needs_followup=result.get("needs_followup", False),
            has_records=result.get("has_records", False)
        )
    except ValueError as e:
        import traceback
        print(f"ValueError in chatbot_query: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        import traceback
        print(f"Exception in chatbot_query: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@app.post("/api/chatbot/recommendations", response_model=ChatbotResponse)
async def get_recommendations(request: ChatbotRequest):
    """Get recommendations for a question (only when user explicitly requests)"""
    try:
        rag = get_rag_service()
        
        # Get recommendations
        result = rag.get_recommendations(request.question, context_from_records=True)
        
        return ChatbotResponse(
            answer="",  # No answer, just recommendations
            recommendations=result.get("recommendations", []),
            sources=result.get("sources", []),
            needs_followup=False,
            has_records=len(result.get("sources", [])) > 0
        )
    except Exception as e:
        import traceback
        print(f"Exception in get_recommendations: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@app.get("/api/chatbot/summary", response_model=SummaryResponse)
async def get_summary():
    """Get summary of all medical records using RAG service"""
    try:
        # Get RAG service
        rag = get_rag_service()
        
        # Generate summary
        summary = rag.get_summary()
        
        return SummaryResponse(summary=summary)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@app.post("/api/rag/rebuild", response_model=RAGRebuildResponse)
async def rebuild_rag_index():
    """Rebuild the RAG vector index from all medical records"""
    try:
        # Get RAG service
        rag = get_rag_service()
        
        # Rebuild index
        result = rag.ingest_documents(rebuild=True)
        
        return RAGRebuildResponse(
            status=result["status"],
            message=result["message"],
            documents_processed=result.get("documents_processed", 0),
            chunks_created=result.get("chunks_created", 0)
        )
    except Exception as e:
        import traceback
        print(f"Exception in rebuild_rag_index: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error rebuilding RAG index: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "app": config.APP_NAME}
