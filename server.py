from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import re
from pathlib import Path

app = FastAPI()

# Allow cross-origin requests from any domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supported video types
SUPPORTED_TYPES = {
    # Video types
    'video/mp4', 'video/x-m4v', 'video/webm', 'video/quicktime',
    'video/x-msvideo', 'video/mpeg', 'video/ogg', 'video/x-matroska',
    # PDF
    'application/pdf', 'application/octet-stream'
}

# Set the directory where files are stored
UPLOAD_DIR = os.path.expanduser("~/clarify_uploads") 
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 1024 * 1024 * 100  # 100MB

@app.get("/uploads/{path:path}")
def get_file(path: str):
    """ Serve files directly from the uploads folder with path support """
    file_path = os.path.join(UPLOAD_DIR, path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

@app.post("/uploads/")
async def upload_file(
    file: UploadFile = File(...), 
    courseId: str = Form(None),
    lessonId: str = Form(None)
):
    """ Handle file uploads with type validation """
    try:
        print(f"[SERVER] Received upload request")
        print(f"[SERVER] Filename: {file.filename}")
        print(f"[SERVER] Content type: {file.content_type}")
        print(f"[SERVER] Course ID: {courseId}")
        print(f"[SERVER] Lesson ID: {lessonId}")

        if not file.filename:
            print("[SERVER] Error: No filename provided")
            raise HTTPException(400, "File name required")
            
        if file.content_type not in SUPPORTED_TYPES:
            print(f"[SERVER] Error: Unsupported type {file.content_type}")
            raise HTTPException(400, f"Unsupported file type: {file.content_type}")
        
        # Create a subfolder structure based on course and lesson IDs
        subfolder = f"course_{courseId}/lesson_{lessonId}" if courseId and lessonId else ""
        folder_path = os.path.join(UPLOAD_DIR, subfolder)
        os.makedirs(folder_path, exist_ok=True)
        
        # Sanitize filename
        original_name = Path(file.filename).name
        clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', original_name)
        file_path = os.path.join(folder_path, clean_name)
        print(f"[SERVER] Saving to: {file_path}")
        
        file_size = 0
        with open(file_path, "wb") as f:
            while content := await file.read(1024 * 1024):
                file_size += len(content)
                if file_size > MAX_FILE_SIZE:
                    raise HTTPException(413, "File too large (max 100MB)")
                f.write(content)
        print(f"[SERVER] File saved successfully")
        
        # Return the path that includes the course/lesson structure
        relative_path = f"{subfolder}/{clean_name}" if subfolder else clean_name
        
        return JSONResponse({
            "info": f"File saved at {file_path}",
            "fileUrl": f"/uploads/{relative_path}"
        })
        
    except HTTPException as he:
        print(f"[SERVER] HTTPException: {he.detail}")
        raise he
    except Exception as e:
        print(f"[SERVER] Unexpected error: {str(e)}")
        raise HTTPException(500, f"Internal server error: {str(e)}")

@app.delete("/uploads/delete")
async def delete_file(request: Request):
    """ Delete a file from the uploads folder """
    data = await request.json()
    file_path = data.get("filepath")
    delete_course_dir = data.get("delete_course_dir", False)
    
    if not file_path:
        return {"error": "File path is required"}
    
    # Handle both full URLs and relative paths
    if file_path.startswith('http'):
        # Extract the path portion after /uploads/
        parts = file_path.split('/uploads/')
        if len(parts) > 1:
            file_path = parts[1]
        else:
            return {"error": f"Invalid URL format: {file_path}"}
    
    # Construct the absolute path
    absolute_path = os.path.join(UPLOAD_DIR, file_path)
    print(f"[SERVER] Attempting to delete file/dir: {absolute_path}")
    
    # Special case: if we're deleting a course directory
    if delete_course_dir:
        # Extract course_id from path (assuming format course_XX/...)
        match = re.search(r'course_(\d+)', file_path)
        if match:
            course_id = match.group(1)
            course_dir = os.path.join(UPLOAD_DIR, f"course_{course_id}")
            
            if os.path.exists(course_dir):
                try:
                    print(f"[SERVER] Deleting entire course directory: {course_dir}")
                    shutil.rmtree(course_dir)
                    return {"success": True, "info": f"Course directory {course_dir} deleted successfully"}
                except Exception as e:
                    print(f"[SERVER] Error deleting course directory: {str(e)}")
                    return {"error": f"Failed to delete course directory: {str(e)}"}
            else:
                print(f"[SERVER] Course directory not found: {course_dir}")
                return {"error": f"Course directory not found: {course_dir}"}
    
    # Normal file deletion
    if os.path.exists(absolute_path):
        try:
            if os.path.isdir(absolute_path):
                shutil.rmtree(absolute_path)
                print(f"[SERVER] Successfully deleted directory: {absolute_path}")
            else:
                os.remove(absolute_path)
                print(f"[SERVER] Successfully deleted file: {absolute_path}")
            
            # Handle directory cleanup more robustly
            directory = os.path.dirname(absolute_path)
            while directory != UPLOAD_DIR and directory.startswith(UPLOAD_DIR):
                try:
                    if os.path.exists(directory) and not os.listdir(directory):
                        print(f"[SERVER] Removing empty directory: {directory}")
                        os.rmdir(directory)
                        # Move up to parent directory
                        directory = os.path.dirname(directory)
                    else:
                        # If directory has content or doesn't exist, stop checking
                        break
                except Exception as e:
                    print(f"[SERVER] Error removing directory {directory}: {str(e)}")
                    break
                    
            return {"success": True, "info": f"File '{file_path}' deleted successfully"}
        except Exception as e:
            print(f"[SERVER] Error deleting file {absolute_path}: {str(e)}")
            return {"error": f"Failed to delete file: {str(e)}"}
    else:
        print(f"[SERVER] File not found: {absolute_path}")
        return {"error": f"File not found: {absolute_path}"}

@app.get("/healthcheck")
def health_check():
    return {"status": "ok"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
