from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.get_db import get_db
from app.core.exceptions import ClienteAlreadyExistsError
from app.schemas.cliente import ClienteCreate
from app.schemas.errors import ErrorResponse
from app.services.cliente_service import create_cliente

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
async def post_cliente(
    payload: ClienteCreate,
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        _, pipefy_response = await create_cliente(payload, db)
        return pipefy_response
    except ClienteAlreadyExistsError as exc:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "conflict", "message": str(exc)},
        )
