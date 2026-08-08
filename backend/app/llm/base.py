from abc import ABC, abstractmethod


class BaseLLM(ABC):

    @abstractmethod
    def generate(
        self,
        prompt: str,
        history: list[dict] | None = None,
        memories: list[dict] | None = None,
    ) -> str:
        """
        Generate an assistant response using conversation
        history and long-term memories.
        """
        pass

    @abstractmethod
    def extract_memory(
        self,
        user_message: str,
    ) -> dict | None:
        """
        Extract an explicit user memory.

        Returns:
            {
                "memory_type": "...",
                "key": "...",
                "value": "..."
            }

        or None when there is nothing worth remembering.
        """
        pass