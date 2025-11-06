from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json
import logging
from datetime import datetime


# Import our custom modules
import database
import scraper
import llm_quiz_generator
from models import QuizRequest, QuizOutput  # Import Pydantic models
from database import Quiz, get_db


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Create all database tables on startup
try:
    database.create_db_and_tables()
    logger.info("Database tables created successfully.")
except Exception as e:
    logger.error(f"Failed to create database tables: {e}")
    raise


# Initialize FastAPI app
app = FastAPI(
    title="AI Wiki Quiz Generator",
    description="API for generating quizzes from Wikipedia articles using AI.",
    version="1.0.0"
)


# --- CORS Middleware ---
# This allows our React frontend to communicate with our backend
origins = [
    "http://localhost:5173",  # Default Vite (React) port
    "http://localhost:3000",  # Default Create-React-App port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],
)


# --- API Endpoints ---


@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to the AI Wiki Quiz Generator API",
        "version": "1.0.0",
        "endpoints": {
            "generate_quiz": "/generate_quiz [POST]",
            "history": "/history [GET]",
            "specific_quiz": "/quiz/{quiz_id} [GET]"
        }
    }


@app.post("/generate_quiz", response_model=QuizOutput)
async def generate_quiz_endpoint(request: QuizRequest, db: Session = Depends(get_db)):
    """
    Endpoint to generate a new quiz from a Wikipedia article.
    
    Steps:
    1. Validates and scrapes the Wikipedia URL
    2. Generates quiz data using LLM (Gemini)
    3. Saves quiz to database
    4. Returns the generated quiz data
    
    Args:
        request: QuizRequest containing the Wikipedia URL
        db: Database session dependency
        
    Returns:
        QuizOutput: Generated quiz with questions, summary, and metadata
    """
    try:
        # 1. Validate URL format
        if not request.url.startswith("https://en.wikipedia.org/wiki/"):
            raise HTTPException(
                status_code=400, 
                detail="Invalid Wikipedia URL. Must start with https://en.wikipedia.org/wiki/"
            )
        
        # 2. Scrape Wikipedia
        logger.info(f"Scraping URL: {request.url}")
        article_title, cleaned_text = scraper.scrape_wikipedia(request.url)
        
        if not cleaned_text or len(cleaned_text.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="Unable to extract sufficient content from the article."
            )
        
        logger.info(f"Successfully scraped article: {article_title} ({len(cleaned_text)} chars)")
        
        # 3. Generate Quiz using LLM
        logger.info("Generating quiz data via LLM...")
        quiz_data_dict = llm_quiz_generator.generate_quiz_from_text(cleaned_text)
        
        # 4. Override title from scraper (more accurate than LLM extraction)
        quiz_data_dict['title'] = article_title
        
        # 5. Validate the generated quiz matches our schema
        try:
            validated_quiz = QuizOutput(**quiz_data_dict)
        except Exception as validation_error:
            logger.error(f"Quiz validation failed: {validation_error}")
            raise HTTPException(
                status_code=500,
                detail=f"Generated quiz failed validation: {str(validation_error)}"
            )
        
        # 6. Save to Database
        logger.info("Saving quiz to database...")
        
        # Serialize the entire quiz dictionary into a JSON string
        json_data_string = json.dumps(quiz_data_dict, ensure_ascii=False, indent=2)
        
        db_entry = Quiz(
            url=request.url,
            title=article_title,
            full_quiz_data=json_data_string
        )
        
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        
        logger.info(f"Quiz saved successfully with ID: {db_entry.id}")
        
        # 7. Return the generated quiz data with database ID
        quiz_data_dict['id'] = db_entry.id
        quiz_data_dict['date_generated'] = db_entry.date_generated.isoformat()
        
        return quiz_data_dict

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error in /generate_quiz: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate quiz: {str(e)}"
        )


@app.get("/history")
def get_quiz_history(db: Session = Depends(get_db)):
    """
    Endpoint to get a list of all previously generated quizzes.
    
    Returns a simplified list with:
    - id: Database ID
    - url: Original Wikipedia URL
    - title: Article title
    - date_generated: Timestamp of generation
    
    Returns:
        List of quiz summaries ordered by most recent first
    """
    try:
        logger.info("Fetching quiz history...")
        
        # Query for specific columns to keep the payload light
        quizzes = db.query(Quiz).order_by(Quiz.date_generated.desc()).all()
        
        history = [
            {
                "id": quiz.id,
                "url": quiz.url,
                "title": quiz.title,
                "date_generated": quiz.date_generated.isoformat()
            }
            for quiz in quizzes
        ]
        
        logger.info(f"Retrieved {len(history)} quiz records")
        return history
        
    except Exception as e:
        logger.error(f"Error in /history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/quiz/{quiz_id}")
def get_specific_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to get the full data for a single quiz by its ID.
    
    Args:
        quiz_id: The database ID of the quiz
        db: Database session dependency
        
    Returns:
        Complete quiz data including all questions, answers, and metadata
    """
    try:
        logger.info(f"Fetching quiz with ID: {quiz_id}")
        
        db_quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        
        if not db_quiz:
            logger.warning(f"Quiz with ID {quiz_id} not found")
            raise HTTPException(status_code=404, detail=f"Quiz with ID {quiz_id} not found")
        
        # CRUCIAL: Deserialize the JSON string back into a dictionary
        try:
            quiz_data = json.loads(db_quiz.full_quiz_data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse quiz data for ID {quiz_id}: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Quiz data is corrupted in database"
            )
        
        # Add the ID and date to the response
        quiz_data['id'] = db_quiz.id
        quiz_data['url'] = db_quiz.url
        quiz_data['date_generated'] = db_quiz.date_generated.isoformat()
        
        logger.info(f"Successfully retrieved quiz ID: {quiz_id}")
        return quiz_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /quiz/{quiz_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "AI Wiki Quiz Generator"
    }


# --- Uvicorn server startup (for development) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
