# USER DB API 

from fastapi import APIRouter , HTTPException,status
from pydantic import BaseModel
from pymongo import ReturnDocument
from db.models.user import User
from db.schemas.user import user_schema , users_schema
from db.client import db_client
from bson import ObjectId

import asyncio

router = APIRouter(prefix="/userdb" , tags=["user"], responses={404: {"message": "no encontrado"}})
# Entidad user 

@router.get("/userdb1")
async def get_users():
    user = users_schema(db_client.users.find())
    print(user)
    return user

@router.get("/users", response_model=list[User])
async def users():
    return users_schema(db_client.users.find())


@router.get("/{id}")
async def user_id(id: str):
    return search_user("_id", ObjectId(id))


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)  # agrego ala base de datos 
async def user(user: User):
    
    # Verifica si el ID ya existe en la lista 
    if type(search_user("email", user.email)) == User :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario Ya existe")
    
    
    
    # Convertir el objeto User a un diccionario y eliminar 'id' ya que MongoDB lo generará
    user_dict = dict(user)
    
    del user_dict["id"]  # Eliminar el 'id' ya que MongoDB lo genera automáticamente
    
    # Insertar el nuevo usuario en la base de datos
    id = db_client.users.insert_one(user_dict).inserted_id
    
    # Recuperar el usuario recién insertado desde la base de datos
    new_user = user_schema(db_client.users.find_one({"_id": ObjectId(id)}))

    # Devolver el usuario con el id generado por MongoDB
    return User(**new_user)


@router.put("/" , response_model=User)
async def user(user: User ):
    user_dict = user.dict()  # Convertir Pydantic a diccionario
    user_id = user_dict.pop("id", None)  # Extraer ID y eliminarlo del dict

    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")

    try:
        updated_user = user_schema(db_client.users.find_one_and_replace(
            {"_id": ObjectId(user_id)}, user_dict, return_document=ReturnDocument.AFTER
        )
        )
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")

        return User(**updated_user)  # Retornar un objeto del modelo User

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
async def user(id: str):
        found = db_client.users.find_one_and_delete({"_id": ObjectId(id)})
        if not found:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"saucces": "usuario eliminado"}

def search_user(field: str, key):
    user = db_client.users.find_one({field: key})
    return User(**user_schema(user)) if user else None




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(router, host="0.0.0.0", port=8000)  
    
# documemntacion con Swagger http://127.0.0.1:8000/docs