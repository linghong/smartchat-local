from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

app = FastAPI()

# Allow cross-origin requests from any domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set the directory where files are stored
UPLOAD_DIR = os.path.expanduser("~/clarify_uploads") 
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/uploads/{filename}")
def get_file(filename: str):
    """ Serve files directly from the uploads folder """
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

@app.post("/uploads/")
async def upload_file(file: UploadFile = File(...)):
    """ Upload a file to the local clarify_uploads folder """
    try:
        # Create upload directory if not exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        
        # Save file atomically
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
            
        return JSONResponse(
            status_code=200,
            content={"info": f"File saved at {file_location}", "fileUrl": f"/uploads/{file.filename}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"File upload failed: {str(e)}"}
        )

@app.delete("/uploads/delete")
async def delete_file(request: Request):
    """ Delete a file from the uploads folder """
    data = await request.json()
    filename = data.get("filename")
    
    if not filename:
        return {"error": "Filename is required"}
        
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"info": f"File '{filename}' deleted successfully"}
    return {"error": "File not found"}

@app.get("/healthcheck")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
