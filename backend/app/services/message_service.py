from uuid import UUID

from app.llm.factory import get_llm
from app.models.message import Message
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.services.memory_service import MemoryService


class MessageService:
    def __init__(
        self,
        repository: MessageRepository,
        conversation_repository: ConversationRepository,
        memory_service: MemoryService,
        llm=None,
    ):
        self.repository = repository
        self.conversation_repository = conversation_repository
        self.memory_service = memory_service
        self.llm = llm or get_llm()

    def create(
        self,
        conversation_id: UUID,
        current_user,
        content: str,
    ):
        # -------------------------------------------------
        # 1. Check conversation
        # -------------------------------------------------

        conversation = self.conversation_repository.get_by_id(
            conversation_id,
            current_user.id,
        )

        if conversation is None:
            raise ValueError("Conversation not found")

        # -------------------------------------------------
        # 2. Check ownership
        # -------------------------------------------------

        if conversation.user_id != current_user.id:
            raise ValueError("Conversation not found")

        # -------------------------------------------------
        # 3. Get previous conversation history
        # -------------------------------------------------

        previous_messages = self.repository.list_by_conversation(conversation_id)

        history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in previous_messages
            if message.role in ("user", "assistant")
        ]

        # -------------------------------------------------
        # 4. Save user message
        # -------------------------------------------------

        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=content,
        )

        user_message = self.repository.create(user_message)

        # -------------------------------------------------
        # 5. Extract long-term memories
        # -------------------------------------------------

        # -------------------------------------------------
        # 5. Extract long-term memories
        # -------------------------------------------------

        try:
            if hasattr(self.llm, "extract_memory"):
                extracted_memory = self.llm.extract_memory(content)

                extracted_memories = (
                    [extracted_memory] if extracted_memory is not None else []
                )
            else:
                extracted_memories = self.llm.extract_memories(content)
        except Exception:  # noqa: BLE001
            extracted_memories = []

        for memory in extracted_memories:
            self.memory_service.save_extracted_memory(
                user_id=current_user.id,
                memory=memory,
            )

        # -------------------------------------------------
        # 6. Get long-term memories
        # -------------------------------------------------

        user_memories = self.memory_service.list(current_user.id)

        memory_context = [
            {
                "memory_type": memory.memory_type,
                "key": memory.key,
                "value": memory.value,
            }
            for memory in user_memories
        ]

        # -------------------------------------------------
        # 7. Generate AI response
        # -------------------------------------------------

        ai_text = self.llm.generate(
            content,
            history=history,
            memories=memory_context,
        )

        # -------------------------------------------------
        # 8. Save assistant response
        # -------------------------------------------------

        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_text,
        )

        assistant_message = self.repository.create(assistant_message)

        return {
            "user_message": user_message,
            "assistant_message": assistant_message,
        }

    def list(
        self,
        conversation_id: UUID,
        current_user,
    ):
        conversation = self.conversation_repository.get_by_id(
            conversation_id,
            current_user.id,
        )

        if conversation is None:
            raise ValueError("Conversation not found")

        if conversation.user_id != current_user.id:
            raise ValueError("Conversation not found")

        return self.repository.list_by_conversation(conversation_id)

    def delete(
        self,
        message_id: UUID,
        current_user,
    ):
        message = self.repository.get_by_id(message_id)

        if message is None:
            raise ValueError("Message not found")

        conversation = self.conversation_repository.get_by_id(
            message.conversation_id,
            current_user.id,
        )

        if conversation is None:
            raise ValueError("Conversation not found")

        if conversation.user_id != current_user.id:
            raise ValueError("Message not found")

        self.repository.delete(message_id)
