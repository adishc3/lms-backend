from __future__ import annotations
import os
import pathlib
import uuid
import aiofiles
from app.core.config import settings

ALLOWED_UPLOAD_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".pdf",
    ".mp4",
    ".mp3",
    ".txt",
    ".csv",
    ".zip",
}


def get_upload_dir() -> str:
    upload_dir = settings.UPLOAD_FOLDER
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


def generate_upload_filename(filename: str) -> str:
    extension = pathlib.Path(filename).suffix.lower()
    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        raise ValueError("Unsupported file type")
    return f"{uuid.uuid4().hex}{extension}"


async def save_upload_file(upload_file) -> str:
    filename = generate_upload_filename(upload_file.filename)
    upload_dir = get_upload_dir()
    file_path = os.path.join(upload_dir, filename)

    size = 0
    async with aiofiles.open(file_path, "wb") as out_file:
        while True:
            chunk = await upload_file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > settings.UPLOAD_MAX_SIZE:
                await out_file.close()
                os.remove(file_path)
                raise ValueError("File exceeds maximum upload size")
            await out_file.write(chunk)

    await upload_file.close()
    return filename
