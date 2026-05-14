from fastapi import APIRouter, HTTPException, status

from api_host.schemas.podcast_schemas import (
    GeneratePodcastRequest,
    GeneratePodcastResponse,
    PodcastInputType,
)
from api_host.services.podcast_pipeline import PodcastPipeline

router = APIRouter(prefix="/api/podcasts", tags=["podcasts"])


@router.post("/generate", response_model=GeneratePodcastResponse)
def generate_podcast(request: GeneratePodcastRequest) -> GeneratePodcastResponse:
    if request.input_type != PodcastInputType.TEXT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDF input is not available yet. Use input_type='text'.",
        )

    pipeline = PodcastPipeline()
    return pipeline.generate_from_text(request)
