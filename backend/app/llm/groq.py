import json

from groq import Groq
from groq.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from app.core.config import settings
from app.llm.base import BaseLLM

type ChatMessage = (
    ChatCompletionSystemMessageParam
    | ChatCompletionUserMessageParam
    | ChatCompletionAssistantMessageParam
)


class GroqLLM(BaseLLM):
    """Groq implementation of the BaseLLM interface."""

    def __init__(self) -> None:
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not configured.")

        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
        )

        self.model = settings.GROQ_MODEL

    def generate(
        self,
        prompt: str,
        history: list[dict] | None = None,
        memories: list[dict] | None = None,
    ) -> str:
        """Generate an assistant response."""

        messages: list[ChatMessage] = [
            {
                "role": "system",
                "content": (
                    "You are an AI assistant for an AI Digital Twin.\n\n"
                    "Use the provided conversation history and long-term "
                    "memories to answer the user.\n\n"
                    "Long-term memories represent information explicitly "
                    "provided by the user in previous conversations.\n\n"
                    "Do not invent, guess, or exaggerate personal facts.\n\n"
                    "If a personal fact is present in the long-term "
                    "memories, you may use it even if it was mentioned "
                    "in another conversation.\n\n"
                    "If the information is not present in the conversation "
                    "history, long-term memories, or current user message, "
                    "say that you do not know.\n\n"
                    "When answering questions about the user's personal "
                    "information, prefer the most recent relevant memory."
                ),
            }
        ]

        # Add conversation history.
        if history:
            for message in history:
                role = message.get("role")
                content = message.get("content")

                if role == "user" and content:
                    messages.append(
                        {
                            "role": "user",
                            "content": content,
                        }
                    )
                elif role == "assistant" and content:
                    messages.append(
                        {
                            "role": "assistant",
                            "content": content,
                        }
                    )

        # Add current user message.
        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        # Add long-term memories.
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
                            f"Long-term memories about the user:\n{memory_text}"
                        ),
                    }
                )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("LLM returned an empty response.")

        return content.strip()

    def extract_memory(
        self,
        user_message: str,
    ) -> dict | None:
        """Extract explicit long-term personal information."""

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
            model=self.model,
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

        # Handle markdown code fences.
        if raw.startswith("```"):
            if raw.startswith("```json"):
                raw = raw[7:]
            else:
                raw = raw[3:]

            raw = raw.removesuffix("```")
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
            isinstance(result[field], str) and result[field].strip()
            for field in required_fields
        ):
            return None

        return {
            "memory_type": result["memory_type"].strip(),
            "key": result["key"].strip(),
            "value": result["value"].strip(),
        }
