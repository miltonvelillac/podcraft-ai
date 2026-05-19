from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status

from api_host.api.request_validation import reject_unknown_fields
from api_host.agents.script_generation.errors import (
    ScriptGenerationConfigurationError,
    ScriptGenerationServiceError,
)
from api_host.clients.errors import McpExternalServiceError, McpToolInputError
from api_host.schemas.podcast_schemas import (
    GeneratePodcastPdfFormRequest,
    GeneratePodcastRequest,
    GeneratePodcastResponse,
    PodcastFormField,
    PodcastInputType,
    PodcastLanguage,
    PodcastStyle,
    PodcastTargetDuration,
)
from api_host.services.podcast_pipeline import PodcastPipeline
from podcraft_contracts import DEFAULT_AUDIO_VOICE

router = APIRouter(prefix="/api/podcasts", tags=["podcasts"])
ALLOWED_PDF_FORM_FIELDS = {field.value for field in PodcastFormField}


@router.post("/generate/text", response_model=GeneratePodcastResponse)
async def generate_podcast_from_text(request: GeneratePodcastRequest) -> GeneratePodcastResponse:
    if request.input_type != PodcastInputType.TEXT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use /api/podcasts/generate/pdf for PDF input.",
    )

    pipeline = PodcastPipeline()
    try:
        return await pipeline.generate_from_text(request)
    except ScriptGenerationConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ScriptGenerationServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except McpToolInputError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except McpExternalServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@router.post("/generate/pdf", response_model=GeneratePodcastResponse)
async def generate_podcast_from_pdf(
    request: Request,
    file: Annotated[UploadFile, File()],
    style: Annotated[PodcastStyle, Form()] = PodcastStyle.EDUCATIONAL,
    voice: Annotated[str, Form()] = DEFAULT_AUDIO_VOICE,
    language: Annotated[PodcastLanguage, Form()] = PodcastLanguage.ENGLISH,
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
        language=language,
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
            language=form.language,
            target_duration=form.target_duration,
        )
    except (ValueError, McpToolInputError, ScriptGenerationConfigurationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except (McpExternalServiceError, ScriptGenerationServiceError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
