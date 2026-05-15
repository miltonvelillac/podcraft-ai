from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status

from api_host.api.request_validation import reject_unknown_fields
from api_host.schemas.podcast_schemas import (
    GeneratePodcastPdfFormRequest,
    GeneratePodcastRequest,
    GeneratePodcastResponse,
    PodcastFormField,
    PodcastInputType,
    PodcastStyle,
    PodcastTargetDuration,
)
from api_host.services.podcast_pipeline import PodcastPipeline

router = APIRouter(prefix="/api/podcasts", tags=["podcasts"])
ALLOWED_PDF_FORM_FIELDS = {field.value for field in PodcastFormField}


@router.post("/generate/text", response_model=GeneratePodcastResponse)
def generate_podcast_from_text(request: GeneratePodcastRequest) -> GeneratePodcastResponse:
    if request.input_type != PodcastInputType.TEXT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use /api/podcasts/generate/pdf for PDF input.",
        )

    pipeline = PodcastPipeline()
    return pipeline.generate_from_text(request)


@router.post("/generate/pdf", response_model=GeneratePodcastResponse)
async def generate_podcast_from_pdf(
    request: Request,
    file: Annotated[UploadFile, File()],
    style: Annotated[PodcastStyle, Form()] = PodcastStyle.EDUCATIONAL,
    voice: Annotated[str, Form()] = "default",
    target_duration: Annotated[PodcastTargetDuration, Form()] = PodcastTargetDuration.SHORT,
) -> GeneratePodcastResponse:
    form_data = await request.form()
    reject_unknown_fields(
        received_fields=form_data.keys(),
        allowed_fields=ALLOWED_PDF_FORM_FIELDS,
        field_group_name="form field",
    )
    form = GeneratePodcastPdfFormRequest(
        style=style,
        voice=voice,
        target_duration=target_duration,
    )

    try:
        content = await file.read()
        pipeline = PodcastPipeline()
        return await pipeline.generate_from_pdf(
            filename=file.filename or "upload.pdf",
            content=content,
            style=form.style,
            voice=form.voice,
            target_duration=form.target_duration,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
