import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from models import QuizOutput
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the Gemini model with increased token limit
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.7,
    max_output_tokens=8192,  # CRITICAL: Increased for complete output
)

# Initialize the JSON output parser
parser = JsonOutputParser(pydantic_object=QuizOutput)

# Simplified, more direct prompt
prompt_template_str = """You are a quiz generator. Create a quiz from this Wikipedia article.

STRICT REQUIREMENTS:
1. Generate EXACTLY 7 complete questions
2. Each question MUST have: question, options (4 choices), answer, difficulty (easy/medium/hard), explanation
3. Include 3-5 related_topics at the end
4. Output ONLY valid JSON, no markdown blocks

ARTICLE:
{article_text}

{format_instructions}

Generate the complete quiz now with all 7 questions and related_topics:"""

# Create the prompt template
prompt = PromptTemplate(
    template=prompt_template_str,
    input_variables=["article_text"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# Create the chain
chain = prompt | llm | parser

def generate_quiz_from_text(text: str, max_retries: int = 2) -> dict:
    """
    Generates a quiz by invoking the LangChain chain with validation and retry.
    """
    max_chars = 12000  # Reduced to give more room for output
    truncated_text = text[:max_chars]
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Invoking LLM chain (attempt {attempt + 1}/{max_retries})...")
            
            output_dict = chain.invoke({"article_text": truncated_text})
            
            # Validate completeness
            quiz_questions = output_dict.get('quiz', [])
            if len(quiz_questions) != 7:
                raise ValueError(f"Expected 7 questions, got {len(quiz_questions)}")
            
            # Check for required top-level fields
            if 'related_topics' not in output_dict:
                raise ValueError("Missing 'related_topics' field")
            
            # Validate each question has all required fields
            for idx, question in enumerate(quiz_questions):
                required = ['question', 'options', 'answer', 'difficulty', 'explanation']
                missing = [f for f in required if f not in question or not question[f]]
                if missing:
                    raise ValueError(f"Question {idx} missing: {missing}")
                
                # Validate options count
                if len(question.get('options', [])) != 4:
                    raise ValueError(f"Question {idx} must have exactly 4 options")
            
            logger.info("Successfully generated complete quiz from LLM.")
            return output_dict
            
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            
            if attempt == max_retries - 1:
                logger.error(f"All attempts exhausted. Last error: {e}")
                raise Exception(f"Failed to generate complete quiz: {e}")
    
    raise Exception("Unexpected error in quiz generation")
