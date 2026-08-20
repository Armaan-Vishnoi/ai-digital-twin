from app.schemas.model import ModelResponse
from fastapi import APIRouter, HTTPException, status

from app.llm.registry import ModelRegistry

router = APIRouter(
    prefix="/models",
    tags=["Models"],
)


@router.get(
    "",
    response_model=list[ModelResponse],
)
def list_models():
    registry = ModelRegistry()
    return registry.list_models()


@router.get(
    "/{model_id:path}",
    response_model=ModelResponse,
)
def get_model(model_id: str):
    registry = ModelRegistry()

    try:
        return registry.get_model_info(model_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
