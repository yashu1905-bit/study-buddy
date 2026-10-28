import os
from typing import TypedDict

from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field


class QuizQuestion(BaseModel):
    question: str = Field(description="A clear question about the video")
    options: list[str] = Field(description="Exactly four answer options")
    answer_index: int = Field(description="Index of the correct option, from 0 to 3")
    explanation: str = Field(description="A short explanation of the correct answer")


class StudyMaterial(BaseModel):
    title: str = Field(description="A short, useful title for this lesson")
    summary: list[str] = Field(description="Five to eight concise key points")
    quiz: list[QuizQuestion] = Field(description="Multiple-choice questions")


class StudyState(TypedDict, total=False):
    transcript: str
    quiz_count: int
    result: dict


def create_material(state: StudyState) -> StudyState:
    model = ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        temperature=0.2,
    )
    structured_model = model.with_structured_output(StudyMaterial)

    prompt = f"""
Create a useful study guide from the video transcript below.

Return:
- A short, accurate title.
- Five to eight concise summary points.
- Exactly {state["quiz_count"]} multiple-choice questions.
- Four answer options per question.
- The correct answer index (0 to 3).
- A brief explanation for each answer.

Use only information supported by the transcript. If a point is unclear,
do not invent details.

Transcript:
{state["transcript"]}
"""
    material = structured_model.invoke(prompt)
    return {"result": material.model_dump()}


def build_graph():
    builder = StateGraph(StudyState)
    builder.add_node("create_material", create_material)
    builder.add_edge(START, "create_material")
    builder.add_edge("create_material", END)
    return builder.compile()


study_graph = build_graph()


def make_study_material(transcript: str, quiz_count: int = 5) -> dict:
    result = study_graph.invoke({
        "transcript": transcript,
        "quiz_count": quiz_count,
    })
    return result["result"]