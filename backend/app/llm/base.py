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

    @abstractmethod
    def extract_memories(
        self,
        user_message: str,
    ) -> list[dict]:
        """
        Extract explicit long-term personal information.
        """
