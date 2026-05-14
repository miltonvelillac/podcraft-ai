from enum import StrEnum
from typing import TypeVar

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from starlette.datastructures import UploadFile

from api_host.schemas.podcast_schemas import (
    GeneratePodcastRequest,
    GeneratePodcastResponse,
    PodcastInputType,
    PodcastStyle,
    PodcastTargetDuration,
)
from api_host.services.podcast_pipeline import PodcastPipeline

router = APIRouter(prefix="/api/podcasts", tags=["podcasts"])

EnumT = TypeVar("EnumT", bound=StrEnum)


@router.post("/generate", response_model=GeneratePodcastResponse)
async def generate_podcast(request: Request) -> GeneratePodcastResponse:
    content_type = request.headers.get("content-type", "").lower()
    pipeline = PodcastPipeline()

    if content_type.startswith("application/json"):
        return await _generate_from_json(request=request, pipeline=pipeline)

    if content_type.startswith(("multipart/form-data", "application/x-www-form-urlencoded")):
        return await _generate_from_multipart(request=request, pipeline=pipeline)

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="Use application/json for text input or multipart/form-data for PDF input.",
    )


async def _generate_from_json(
    request: Request,
    pipeline: PodcastPipeline,
) -> GeneratePodcastResponse:
    try:
        podcast_request = GeneratePodcastRequest.model_validate(await request.json())
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=jsonable_encoder(exc.errors()),
        ) from exc

    if podcast_request.input_type != PodcastInputType.TEXT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Use multipart/form-data with a PDF file for input_type='pdf'.",
        )

    return pipeline.generate_from_text(podcast_request)


async def _generate_from_multipart(
    request: Request,
    pipeline: PodcastPipeline,
) -> GeneratePodcastResponse:
    form = await request.form()
    uploaded_file = form.get("file")

    if not isinstance(uploaded_file, UploadFile):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDF file is required.",
        )

    style = _parse_enum(form.get("style"), PodcastStyle, "style", PodcastStyle.EDUCATIONAL)
    target_duration = _parse_enum(
        form.get("target_duration"),
        PodcastTargetDuration,
        "target_duration",
        PodcastTargetDuration.SHORT,
    )
    voice = str(form.get("voice") or "default").strip()
    if not voice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voice cannot be empty.",
        )

    try:
        content = await uploaded_file.read()
        return pipeline.generate_from_pdf(
            filename=uploaded_file.filename or "upload.pdf",
            content=content,
            style=style,
            voice=voice,
            target_duration=target_duration,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


def _parse_enum(
    value: object,
    enum_type: type[EnumT],
    field_name: str,
    default: EnumT,
) -> EnumT:
    if value is None:
        return default

    try:
        return enum_type(str(value))
    except ValueError as exc:
        allowed_values = ", ".join(member.value for member in enum_type)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name}. Allowed values: {allowed_values}.",
        ) from exc
