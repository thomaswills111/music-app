import uuid
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from database import get_db
from middleware.auth_middleware import auth_middleware
import cloudinary
import cloudinary.uploader
from dotenv import dotenv_values

from models.song import Song

configs = dotenv_values()

router = APIRouter()

cloudinary.config(
    cloud_name="dg0hf9bid",
    api_key="641292328936345",
    api_secret=configs[
        "API_SECRET"
    ],  # Click 'View Credentials' below to copy your API secret
    secure=True,
)

# 201 because creating a new song
@router.post("/upload", status_code=201)
# (...) means it is required
def upload_song(
    song: UploadFile = File(...),
    thumbnail: UploadFile = File(...),
    artist: str = Form(...),
    song_name: str = Form(...),
    hex_code: str = File(...),
    db: Session = Depends(get_db),
    auth_dict=Depends(auth_middleware),
):
    song_id: str = str(uuid.uuid4())
    song_res = cloudinary.uploader.upload(song.file, resource_type='auto', folder=f'songs/{song_id}')
    thumbnail_res = cloudinary.uploader.upload(thumbnail.file, resource_type='image', folder=f'songs/{song_id}')
    
    new_song = Song(
        id =song_id,
        song_name = song_name,
        artist = artist,
        hex_code = hex_code,
        song_url = song_res['url'],
        thumbnail_url = thumbnail_res['url']
    )
    
    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    return new_song
