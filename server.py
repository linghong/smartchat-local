from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"info": f"File '{file.filename}' saved at '{file_location}'"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
