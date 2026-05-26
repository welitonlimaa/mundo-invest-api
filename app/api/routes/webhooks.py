from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.get_db import get_db
from app.core.exceptions import ClienteNotFoundError, WebhookEventAlreadyProcessedError
from app.schemas.errors import ErrorResponse
from app.schemas.webhook import WebhookPayload
from app.services.webhook_service import process_webhook

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post(
    "/pipefy/card-updated",
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def post_card_updated(
    payload: WebhookPayload,
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        return await process_webhook(payload, db)
    except WebhookEventAlreadyProcessedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": str(exc)},
        )
    except ClienteNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": str(exc)},
        )
