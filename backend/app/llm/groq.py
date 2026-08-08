import json

from groq import Groq

from app.core.config import settings
from app.llm.base import BaseLLM


class GroqLLM(BaseLLM):

    def __init__(self):
        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )

    def generate(
        self,
        prompt: str,
        history: list[dict] | None = None,
        memories: list[dict] | None = None,
    ) -> str:

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI assistant for an AI Digital Twin.\n\n"

                    "Use the provided conversation history and long-term "
                    "memories to answer the user.\n\n"

                    "Long-term memories represent information explicitly "
                    "provided by the user in previous conversations.\n\n"

                    "Do not invent, guess, or exaggerate personal facts.\n"

                    "If a personal fact is present in the long-term memories, "
                    "you may use it even if it was mentioned in another conversation.\n\n"

                    "If the information is not present in either the conversation "
                    "history, long-term memories, or current user message, "
                    "say that you do not know.\n\n"

                    "When answering questions about the user's personal information, "
                    "prefer the most recent relevant memory."
                ),
            }
        ]

        if history:
            for message in history:
                role = message.get("role")
                content = message.get("content")

                if role in ("user", "assistant") and content:
                    messages.append(
                        {
                            "role": role,
                            "content": content,
                        }
                    )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        # Add long-term memories
        memory_text = ""

        if memories:
            memory_text = "\n".join(
                f"- {memory['key']}: {memory['value']}"
                for memory in memories
                if memory.get("key") and memory.get("value")
            )

        if memory_text:
            messages.append(
                {
                    "role": "system",
                    "content": (
                        "Long-term memories about the user:\n"
                        f"{memory_text}"
                    ),
                }
            )

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
        )

        return response.choices[0].message.content

    def extract_memory(
        self,
        user_message: str,
    ) -> dict | None:

        system_prompt = """
You are a memory extraction system for an AI Digital Twin.

Your job is to identify ONLY explicit, useful, long-term personal
information stated by the USER.

Do NOT infer information.

Do NOT create memories from questions.

Do NOT create memories from temporary requests.

Do NOT create memories from general knowledge.

Examples that SHOULD create memories:

User:
"My name is Prem."

Return:
{
    "memory_type": "identity",
    "key": "name",
    "value": "Prem"
}

User:
"My favorite programming language is Rust."

Return:
{
    "memory_type": "preference",
    "key": "favorite_programming_language",
    "value": "Rust"
}

User:
"I am studying BCA."

Return:
{
    "memory_type": "education",
    "key": "degree",
    "value": "BCA"
}

Examples that should NOT create memories:

User:
"What is Python?"

Return:
null

User:
"What is my favorite programming language?"

Return:
null

User:
"Explain binary search."

Return:
null

User:
"Write Python code for sorting."

Return:
null

Return ONLY valid JSON.

If there is no useful explicit memory, return:

null

If there is a memory, return exactly:

{
    "memory_type": "...",
    "key": "...",
    "value": "..."
}
"""

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            temperature=0,
        )

        raw = response.choices[0].message.content

        if not raw:
            return None

        raw = raw.strip()

        # Remove markdown code fences if the model returns them.
        if raw.startswith("```"):
            raw = raw.replace("```json", "", 1)
            raw = raw.replace("```", "", 1)
            raw = raw.strip()

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            return None

        if result is None:
            return None

        if not isinstance(result, dict):
            return None

        required_fields = (
            "memory_type",
            "key",
            "value",
        )

        if not all(field in result for field in required_fields):
            return None

        if not all(
            isinstance(result[field], str)
            and result[field].strip()
            for field in required_fields
        ):
            return None

        return {
            "memory_type": result["memory_type"].strip(),
            "key": result["key"].strip(),
            "value": result["value"].strip(),
        }
