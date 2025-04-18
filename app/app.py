from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI()

UPLOAD_DIR = Path("/mnt/truenas/projects")

@app.get("/", response_class=HTMLResponse)
async def upload_form():
    return """
    <html>
        <head><title>Upload</title></head>
        <body>
            <h2>Upload your HTML project</h2>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <label for="username">Username:</label>
                <input type="text" name="username" required /><br><br>

                <label for="file">Choose file:</label>
                <input type="file" name="file" required /><br><br>

                <button type="submit">Upload</button>
            </form>
        </body>
    </html>
    """

@app.post("/upload")
async def upload_file(username: str = Form(...), file: UploadFile = File(...)):
    user_dir = UPLOAD_DIR / username
    user_dir.mkdir(parents=True, exist_ok=True)

    file_path = user_dir / file.filename

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        return {"error": f"Failed to save file: {str(e)}"}

    return {
        "message": "File uploaded successfully",
        "access_url": f"http://192.168.1.100/sites/{username}/{file.filename}"
    }

@app.get("/sites/{username}/{filename}")
async def get_file(username: str, filename: str):
    file_path = UPLOAD_DIR / username / filename
    if file_path.exists():
        return {
            "message": f"File available at: http://192.168.1.100/sites/{username}/{filename}"
        }
    return {"error": "File not found"}
