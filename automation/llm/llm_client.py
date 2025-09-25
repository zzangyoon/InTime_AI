import ollama

MODEL = "gemma3:4b"

def generate_report(system_prompt: str, user_prompt: str) -> str:
    """
    로컬 LLM을 이용해 보고서를 받아오는 함수
    """

    response = ollama.chat(
        model = MODEL,
        messages = [
            {"role" : "system", "content" : system_prompt},
            {"role" : "user", "content" : user_prompt}
        ]
    )

    return response
