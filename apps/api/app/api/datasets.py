import json

from fastapi import APIRouter, HTTPException

from app.data.fundamentals_completion import load_completion_report
from app.data.quality import load_quality_report
from app.schemas.models import DatasetQualityResponse

router = APIRouter()


@router.get("/quality/latest", response_model=DatasetQualityResponse)
def latest_quality_report() -> DatasetQualityResponse:
    try:
        report = load_quality_report()
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return DatasetQualityResponse(**report)


@router.get("/fundamentals/completion/latest")
def latest_fundamentals_completion() -> dict:
    try:
        return load_completion_report()
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
