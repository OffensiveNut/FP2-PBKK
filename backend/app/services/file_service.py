import os
import uuid
from pathlib import Path

from fastapi import UploadFile

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def _ensure_upload_dir() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _validate_file(file: UploadFile) -> None:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Tipe file {ext} tidak diizinkan. Gunakan: {', '.join(ALLOWED_EXTENSIONS)}"
        )


async def save_upload(file: UploadFile) -> str:
    _ensure_upload_dir()
    _validate_file(file)

    ext = Path(file.filename or "").suffix.lower()
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = UPLOAD_DIR / filename

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise ValueError("File terlalu besar. Maksimal 5 MB")

    filepath.write_bytes(content)
    return str(filepath)


def delete_file(filepath: str) -> None:
    path = Path(filepath)
    if path.exists() and path.parent == UPLOAD_DIR:
        path.unlink()
