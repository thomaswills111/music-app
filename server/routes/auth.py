import uuid
import bcrypt
from fastapi import Depends, HTTPException
import jwt
from database import get_db
from middleware.auth_middleware import auth_middleware
from models.user import User
from pydantic_schemas.user_create import UserCreate
from fastapi import APIRouter
from sqlalchemy.orm import Session
from dotenv import dotenv_values

configs = dotenv_values()

from pydantic_schemas.user_login import UserLogin

router = APIRouter()


# 201 is the code for creation success
@router.post("/signup", status_code=201)
# dependancy injection to get and dispose of the db
def signup_user(user: UserCreate, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.email == user.email).first()
    if user_db:
        raise HTTPException(400, "A user with that email already exists!")
    hashed_pw = bcrypt.hashpw(user.password.encode(), salt=bcrypt.gensalt())
    user_db = User(
        id=str(uuid.uuid4()), name=user.name, email=user.email, password=hashed_pw
    )

    db.add(user_db)
    db.commit()
    db.refresh(user_db)

    return user_db


@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.email == user.email).first()
    if not user_db:
        raise HTTPException(400, "A user with that email does not exist!")

    is_match = bcrypt.checkpw(user.password.encode(), user_db.password)
    if not is_match:
        raise HTTPException(400, "The password is incorrect!")

    # maybe I can create a session/instance and share the id so other's can join
    token = jwt.encode({"id": user_db.id}, configs['PASSWORD'])

    return {"token": token, "user": user_db}


@router.get("/")
def get_user_data(db: Session = Depends(get_db), user_dict=Depends(auth_middleware)):
    user = db.query(User).filter(User.id == user_dict['uid']).first()
    if not user:
        raise HTTPException(404, 'User not found!')
    return user