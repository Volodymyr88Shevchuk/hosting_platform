from fastapi import FastAPI, UploadFile, File, Form, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
from auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
import os

app = FastAPI()

UPLOAD_DIR = Path("/mnt/truenas/projects")

# Zorg dat 'hosting_platform' wordt geserveerd als statische map
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# ⬇️ Mount je statische bestanden
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Route naar index.html bij bezoek aan root
@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token(data={"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/upload")
async def upload_file(
    request: Request,
    username: str = Form(...),
    file: UploadFile = File(...)
):
    user_dir = UPLOAD_DIR / username
    user_dir.mkdir(parents=True, exist_ok=True)

    file_path = user_dir / file.filename

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        return {"error": f"Failed to save file: {str(e)}"}

    base_url = str(request.base_url).rstrip("/")
    return {
        "message": "File uploaded successfully",
        "access_url": f"{base_url}/sites/{username}/{file.filename}"
    }

@app.get("/sites/{username}/{filename}")
async def get_file(username: str, filename: str):
    file_path = UPLOAD_DIR / username / filename
    if file_path.exists():
        return FileResponse(file_path, media_type="text/html")
    return {"error": "File not found"}
