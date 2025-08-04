import json
import re
from .llm import llm


def clean_and_parse_response(text):
    """
    Cleans and parses JSON response from Gemini which might be wrapped in markdown-style code blocks.
    """
    # Remove Markdown triple backticks and optional language hints like ```json
    cleaned = re.sub(r"^```json\s*|```$", "", text.strip(), flags=re.MULTILINE)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        return {
            "error": "Invalid JSON from LLM",
            "raw": cleaned,
            "message": str(e)
        }


def learning_agent(progress):
    prompt = f"""
    You are an AI tutor helping rural students.
    Score: {progress.get('score')}
    Last Topic: {progress.get('last_topic')}

    Based on the score, determine the student's level (Beginner/Intermediate/Advanced).
    Recommend the next topic and explain it in simple terms.
    Include a motivational message in easy-to-understand language.

    Respond ONLY in JSON like this:
    {{
        "level": "...",
        "focus": "...",
        "message": "...",
        "explanation": "..."
    }}
    """

    response = llm.generate_content(prompt)

    print("========== RAW LLM RESPONSE ==========")
    print(response.text)
    print("======================================")

    return clean_and_parse_response(response.text)



def translation_agent(text, target_language):
    prompt = f"Translate the following to {target_language}: {text} and give only response in a format 'Transalation followed by English for pronounciation' only that"
    response = llm.generate_content(prompt)
    return response.text.strip()


def quiz_agent(topic):
    prompt = f"""
    Generate 3 simple quiz questions on the topic '{topic}' for a school student.
    Each question must have 4 options and one correct answer.

    Respond ONLY in JSON (no markdown), like this:
    {{
        "quiz": [
            {{
                "question": "...",
                "options": ["...", "...", "...", "..."],
                "answer": "..."
            }},
            ...
        ]
    }}
    """
    response = llm.generate_content(prompt)

    print("========== RAW QUIZ RESPONSE ==========")
    print(response.text)
    print("======================================")

    result = clean_and_parse_response(response.text)
    return result.get("quiz", [])  

