import uuid
import os
from pathlib import Path
import shutil

from typing import List
from fastapi import FastAPI, File, UploadFile

UPLOAD_FOLDER = 'uploads'

app = FastAPI()

def save_uploaded_file(upload_file: UploadFile, destination: Path) -> None:
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    tmp_uploads_path = './upload/'

    if not os.path.exists(tmp_uploads_path):
        os.makedirs(tmp_uploads_path)

    p = Path(tmp_uploads_path + filename)
    print(p)

    save_uploaded_file(file, p)
    return {"filename": file.filename}

@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    filenames = {"filenames": []}

    tmp_uploads_path = "./upload/{0}/".format(uuid.uuid1())
    if not os.path.exists(tmp_uploads_path):
        os.makedirs(tmp_uploads_path)
    
    for file in files:
        filenames["filenames"].append(file.filename)
        p = Path(tmp_uploads_path + file.filename)
        print(p)

        save_uploaded_file(file, p)

    return filenames