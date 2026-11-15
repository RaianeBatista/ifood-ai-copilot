from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import DemoAccount, ensure_restaurant_access, get_current_account
from app.database import get_db
from app.schemas.assistant import AssistantAnswer, AssistantQuestion
from app.services.assistant import (
    LLMProviderError,
    MissingLLMConfigurationError,
    generate_grounded_answer,
    retrieve_operational_context,
)

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/ask", response_model=AssistantAnswer)
async def ask_assistant(
    payload: AssistantQuestion,
    account: DemoAccount = Depends(get_current_account),
    db: Session = Depends(get_db),
) -> AssistantAnswer:
    ensure_restaurant_access(payload.restaurant_id, account)
    context = retrieve_operational_context(db, payload.restaurant_id, payload.question)
    try:
        answer = await generate_grounded_answer(payload.question, context)
    except MissingLLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except LLMProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return AssistantAnswer(answer=answer, sources=[source for source, _ in context])
