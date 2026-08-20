from uuid import UUID

from app.llm.registry import ModelRegistry
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
        model_registry: ModelRegistry | None = None,
    ):
        self.repository = repository
        self.conversation_repository = conversation_repository
        self.memory_service = memory_service
        self.llm = llm
        self.model_registry = model_registry or ModelRegistry()

    def create(
        self,
        conversation_id: UUID,
        current_user,
        content: str,
        model: str = "auto",
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
        # 3. Resolve model
        # -------------------------------------------------

        selected_model = self.model_registry.resolve_model_id(model)
        # -------------------------------------------------
        # 4. Resolve LLM
        # -------------------------------------------------

        if self.llm is not None:
            llm = self.llm
        else:
            llm = self.model_registry.get_llm(selected_model)

        # -------------------------------------------------
        # 5. Get previous conversation history
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
        # 6. Save user message
        # -------------------------------------------------

        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=content,
            model=selected_model,
        )

        user_message = self.repository.create(user_message)

        # -------------------------------------------------
        # 7. Extract long-term memories
        # -------------------------------------------------

        try:
            extracted_memories = llm.extract_memories(content)
        except Exception:  # noqa: BLE001
            extracted_memories = []

        for memory in extracted_memories:
            self.memory_service.save_extracted_memory(
                user_id=current_user.id,
                memory=memory,
            )

        # -------------------------------------------------
        # 8. Get long-term memories
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
        # 9. Generate AI response
        # -------------------------------------------------

        ai_text = llm.generate(
            content,
            history=history,
            memories=memory_context,
        )

        # -------------------------------------------------
        # 10. Save assistant response
        # -------------------------------------------------

        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_text,
            model=selected_model,
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
