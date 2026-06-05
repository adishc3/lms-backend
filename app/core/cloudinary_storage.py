"""Cloudinary file storage for lesson attachments."""
import cloudinary
import cloudinary.uploader
from app.core.config import settings
from fastapi import UploadFile, HTTPException

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)


async def upload_lesson_file(file: UploadFile, lesson_id: int) -> dict:
    """
    Upload a file to Cloudinary for a lesson.
    
    Args:
        file: The uploaded file
        lesson_id: The lesson ID for organizing files
        
    Returns:
        dict with 'url' and 'public_id' from Cloudinary
        
    Raises:
        HTTPException: If upload fails or file is invalid
    """
    try:
        # Read file content
        content = await file.read()
        
        # Validate file size (max 100MB for Cloudinary free tier)
        max_size = 100 * 1024 * 1024  # 100MB
        if len(content) > max_size:
            raise HTTPException(status_code=413, detail="File too large (max 100MB)")
        
        # Determine resource type based on file extension
        file_ext = file.filename.split('.')[-1].lower() if file.filename else ''
        
        # Map extensions to resource types
        resource_type_map = {
            # Videos
            'mp4': 'video', 'avi': 'video', 'mov': 'video', 'mkv': 'video',
            'webm': 'video', 'flv': 'video', 'wmv': 'video',
            # Images
            'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image',
            'bmp': 'image', 'webp': 'image', 'svg': 'image', 'ico': 'image',
            # Documents
            'pdf': 'raw', 'doc': 'raw', 'docx': 'raw', 'txt': 'raw',
            'ppt': 'raw', 'pptx': 'raw', 'xls': 'raw', 'xlsx': 'raw',
            'zip': 'raw', 'rar': 'raw', '7z': 'raw',
        }
        
        resource_type = resource_type_map.get(file_ext, 'raw')
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            content,
            folder=f"lms/lessons/{lesson_id}",
            resource_type=resource_type,
            public_id=file.filename.rsplit('.', 1)[0] if file.filename else 'upload',
            overwrite=False,
        )
        
        return {
            'url': result['secure_url'],
            'public_id': result['public_id'],
            'resource_type': result['resource_type'],
            'file_name': file.filename,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file to Cloudinary: {str(e)}"
        )


async def delete_lesson_file(public_id: str, resource_type: str = 'image') -> bool:
    """
    Delete a file from Cloudinary.
    
    Args:
        public_id: The Cloudinary public ID of the file
        resource_type: The type of resource (image, video, raw)
        
    Returns:
        True if deletion was successful
    """
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return result.get('result') == 'ok'
    except Exception as e:
        print(f"Failed to delete file from Cloudinary: {str(e)}")
        return False
