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
                    "information, prefer the most recent relevant memory.\n\n"
                    "Be concise by default. Answer simple questions directly "
                    "without unnecessary introductions, summaries, tables, "
                    "or long explanations.\n\n"
                    "Provide detailed explanations only when the user explicitly "
                    "asks for detail, a deep explanation, examples, step-by-step "
                    "guidance, or a comprehensive answer.\n\n"
                    "Match the length and style of the response to the user's "
                    "question. Do not make a simple answer unnecessarily long."
                ),
            }
        ]

        # -------------------------------------------------
        # 1. Add long-term memories
        # -------------------------------------------------

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

        # -------------------------------------------------
        # 2. Add previous conversation history
        # -------------------------------------------------

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

        # -------------------------------------------------
        # 3. Add current user message
        # -------------------------------------------------

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        # -------------------------------------------------
        # 4. Generate response
        # -------------------------------------------------

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("LLM returned an empty response.")

        return content.strip()

    def extract_memories(
        self,
        user_message: str,
    ) -> list[dict]:
        """Extract all explicit long-term personal information."""

        system_prompt = """
You are a memory extraction system for an AI Digital Twin.

Your job is to identify ONLY explicit, useful, long-term personal
information stated by the USER.

A single user message can contain MULTIPLE independent memories.

Extract every useful explicit memory from the message.

Do NOT infer information.

Do NOT create memories from questions.

Do NOT create memories from temporary requests.

Do NOT create memories from general knowledge.

Examples that SHOULD create memories:

User:
"My name is Prem."

Return:
[
  {
    "memory_type": "identity",
    "key": "name",
    "value": "Prem"
  }
]

User:
"My favorite programming language is Rust."

Return:
[
  {
    "memory_type": "preference",
    "key": "favorite_programming_language",
    "value": "Rust"
  }
]

User:
"I am studying BCA."

Return:
[
  {
    "memory_type": "education",
    "key": "degree",
    "value": "BCA"
  }
]

User:
"My name is Prem and I am studying BCA."

Return:
[
  {
    "memory_type": "identity",
    "key": "name",
    "value": "Prem"
  },
  {
    "memory_type": "education",
    "key": "degree",
    "value": "BCA"
  }
]

Examples that should NOT create memories:

User:
"What is Python?"

Return:
[]

User:
"What is my favorite programming language?"

Return:
[]

User:
"Explain binary search."

Return:
[]

User:
"Write Python code for sorting."

Return:
[]

Return ONLY valid JSON.

If there is no useful explicit memory, return:

[]

If there are memories, return exactly an array of objects:

[
  {
    "memory_type": "...",
    "key": "...",
    "value": "..."
  }
]
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
            return []

        raw = raw.strip()

        # Remove Markdown code fences if the model returns them.
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
            return []

        if not isinstance(result, list):
            return []

        memories: list[dict] = []

        for item in result:
            if not isinstance(item, dict):
                continue

            required_fields = (
                "memory_type",
                "key",
                "value",
            )

            if not all(field in item for field in required_fields):
                continue

            if not all(
                isinstance(item[field], str) and item[field].strip()
                for field in required_fields
            ):
                continue

            memories.append(
                {
                    "memory_type": item["memory_type"].strip(),
                    "key": item["key"].strip(),
                    "value": item["value"].strip(),
                }
            )

        return memories
