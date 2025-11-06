from pydantic import BaseModel, Field
from typing import List, Literal


# This file defines the Pydantic models (schemas) for:
# 1. Validating the JSON structure returned by the LLM.
# 2. Validating the request body for the /generate_quiz endpoint.


# --- Pydantic Schemas for LLM Output ---


class QuizQuestion(BaseModel):
    question: str = Field(description="The text of the quiz question.")
    options: List[str] = Field(description="A list of four options (A, B, C, D).", min_length=4, max_length=4)
    answer: str = Field(description="The correct answer from the options list.")
    difficulty: Literal["easy", "medium", "hard"] = Field(description="Difficulty level: easy, medium, or hard.")
    explanation: str = Field(description="A brief explanation for the correct answer.")


class KeyEntities(BaseModel):
    people: List[str] = Field(default_factory=list, description="List of key people mentioned.")
    organizations: List[str] = Field(default_factory=list, description="List of key organizations or groups.")
    locations: List[str] = Field(default_factory=list, description="List of key locations mentioned.")


class QuizOutput(BaseModel):
    title: str = Field(description="The main title of the article.")
    summary: str = Field(description="A concise summary of the article (2-3 sentences).")
    key_entities: KeyEntities = Field(description="Key entities extracted from the article.")
    quiz: List[QuizQuestion] = Field(description="A list of exactly 7 quiz questions.", min_length=7, max_length=7)
    related_topics: List[str] = Field(description="A list of 3-5 related Wikipedia topics.", min_length=3, max_length=5)


# --- Pydantic Schema for API Input ---


class QuizRequest(BaseModel):
    url: str = Field(description="Wikipedia article URL to generate quiz from.")
