from datetime import datetime
import os
from pathlib import Path
import secrets
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
import logging
import sys

from db.db import get_session
from schemas.user import UserCreate
from models.entity import Token, Users, Storage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

router = APIRouter()


# Статус активности
@router.get('/ping')
async def ping_database() -> str:
    try:
        start_time = datetime.now()
        session = await get_session()
        await session.execute(select(1))
        end_time = datetime.now()
        timer = (end_time - start_time).total_seconds() * 1000
        return f'{timer} milliseconds'
    except SQLAlchemyError as e:
        logger.info(f'Database ping failed: {e}')
        return None

# Регистрация
@router.post('/register')
async def create_user(user: UserCreate) -> None:
    session = await get_session()
    query = await session.execute(select(Users).where(Users.username==user.name))
    if query.scalar():
        raise HTTPException(status_code=400, detail='Username already registered')
    else:
        new_user = Users(username=user.name, password=user.password)
        session.add(new_user)
        await session.commit()
        logger.info(f'New user was created: {user.name}')


# Авторизация
@router.post('/auth')
async def auth_user(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    session = await get_session()
    existing_user = await session.execute(select(Users).where(Users.username==form_data.username))
    existing_user = existing_user.scalar_one_or_none()
    if not existing_user:
        raise HTTPException(status_code=400, detail='Username not found')
    elif not existing_user.password == form_data.password:
        raise HTTPException(status_code=400, detail='Wrong password')
    token = secrets.token_urlsafe(10)
    new_token = Token(user_id=existing_user.id, token=token)
    session.add(new_token)
    await session.commit()
    return {'access_token': token, 'token_type': 'bearer'}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth')


# Вернуть информацию о пользователе
@router.get('/users/me')
async def read_users_me(token: str = Depends(oauth2_scheme)) -> dict:
    session = await get_session()
    result = await session.execute(select(Token).join(Users).where(Token.token==token))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail='Invalid authentication credentials')
    return user


# Информация о загруженных файлах
@router.get('/files/')
async def get_files(user: str = Depends(read_users_me)) -> list:
    session = await get_session()
    user_id = user.user_id
    query = await session.execute(select(Storage).where(Storage.user_id==user_id))
    user_storages = query.fetchall()
    if not user_storages:
        raise HTTPException(status_code=404, detail='User not found')
    user_storages_dicts = [storage._asdict() for storage in user_storages]
    return user_storages_dicts


# Загрузить файл в хранилище
@router.post('/files/')
async def upload_file(user: str = Depends(read_users_me), file: UploadFile = File(...), user_save_directory: str = None) -> None:
    user_id = user.user_id
    default_pass = f'storage\{user_id}'

    # Добавляем загруженный файл в БД
    session = await get_session()
    query = await session.execute(select(Storage).where(Storage.file_name==file.filename))
    existing_file = query.scalar_one_or_none()
    if not existing_file:
        new_storage_file = Storage(user_id=user_id, file_name=file.filename, file_path=user_save_directory)
        session.add(new_storage_file)
        await session.commit()
        logger.info(f'DB was updated: user{user_id} was upload new file: {file.filename}')
    else:
        raise HTTPException(status_code=400, detail='File already exist')
    
    # Загружаем файл в хранилище
    if user_save_directory:
        actual_save_directory = f'storage\{user_id}\{user_save_directory}'
    else:
        actual_save_directory = default_pass

    if not os.path.exists(actual_save_directory):
        os.makedirs(actual_save_directory)

    save_path = os.path.join(actual_save_directory, file.filename)
    with open(save_path, 'wb') as buffer:
        buffer.write(await file.read())
    logger.info(f'Storage was updated: user{user_id} was upload new file: {file.filename} with path: {actual_save_directory}')


# Скачать загруженный файл
@router.post('/files/download')
async def download_file(user: str = Depends(read_users_me), file_path: str=None, file_id: int=None) -> FileResponse:
    user_id = user.user_id
    if file_path:
        file_path = f'storage\{user_id}\{file_path}'
    elif file_id:
        session = await get_session()
        query = await session.execute(select(Storage).where(Storage.id==file_id))
        file = query.scalar_one_or_none()
        if not file:
            raise HTTPException(status_code=404, detail='File not found')
        else:
            if file.file_path:
                file_path = f'storage\{user_id}\{file.file_path}'
            else:
                file_path = f'storage\{user_id}\{file.file_name}'
    print(file_path)
    file = Path(file_path)
    if file.is_file():
        return FileResponse(file_path, filename=file.name, media_type='multipart/form-data')
    else:
        raise HTTPException(status_code=404, detail='File not found')
    
