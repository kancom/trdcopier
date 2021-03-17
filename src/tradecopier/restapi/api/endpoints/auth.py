from datetime import datetime, timedelta

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from tradecopier.application import Terminal, TerminalRepo
from tradecopier.application.domain.value_objects import TerminalId
from tradecopier.restapi.deps import Container

from ...dto.objects import Token, TokenData

ALGORITHM = "HS256"

router = APIRouter()
BEARER_HEADER = APIKeyHeader(name="Bearer")


@inject
def create_access_token(
    data: dict,
    expires_days: int,
    secret_key: str = Depends(Provide[Container.config.secret_key]),
    algorithm: str = ALGORITHM,
):
    expires_delta = timedelta(days=expires_days)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=5)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


@inject
async def get_current_terminal(
    token: str = Depends(BEARER_HEADER),
    secret_key: str = Depends(Provide[Container.config.secret_key]),
    term_repo: TerminalRepo = Depends(Provide[Container.terminal_repo]),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate terminal",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        terminal_id: TerminalId = TerminalId(payload.get("sub"))
        if terminal_id is None:
            raise credentials_exception
        token_data = TokenData(terminal_id=terminal_id)
    except JWTError:
        raise credentials_exception
    terminal = term_repo.get(token_data.terminal_id)
    if terminal is None:
        raise credentials_exception
    return terminal


async def get_current_active_terminal(
    current_terminal: Terminal = Depends(get_current_terminal),
):
    if not current_terminal.is_active:
        raise HTTPException(status_code=400, detail="Inactive terminal")
    return current_terminal


@router.post("/token", response_model=Token)
@inject
async def get_access_token(
    terminal_id: TerminalId,
    term_repo: TerminalRepo = Depends(Provide[Container.terminal_repo]),
    expires_days: int = Depends(Provide[Container.config.token_expire.as_int()]),
):
    terminal = term_repo.get(terminal_id)
    if not terminal:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": terminal.terminal_id.hex}, expires_days=expires_days
    )
    return {"access_token": access_token, "token_type": "bearer"}
