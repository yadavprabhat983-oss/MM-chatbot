import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.schemas.health import HealthResponse, ReadinessResponse
from app.core.config import settings

router = APIRouter(prefix="/api/health", tags=["Health"])

@router.get("", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok",
        app_env=settings.APP_ENV,
        timestamp=datetime.datetime.utcnow()
    )

@router.get("/ready", response_model=ReadinessResponse)
def readiness_check(db: Session = Depends(get_db)):
    db_status = "disconnected"
    pgvector_supported = False
    err_msg = None

    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"

        dialect = db.bind.dialect.name if db.bind else "unknown"
        if dialect == "postgresql":
            res = db.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'")).fetchone()
            pgvector_supported = res is not None
        else:
            pgvector_supported = True  # In fallback / sqlite testing mode
    except Exception as e:
        err_msg = str(e)

    is_ready = db_status == "connected" and err_msg is None

    return ReadinessResponse(
        status="ready" if is_ready else "not_ready",
        database=db_status,
        pgvector_supported=pgvector_supported,
        error=err_msg,
        timestamp=datetime.datetime.utcnow()
    )
