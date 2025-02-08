from fastapi import APIRouter , HTTPException
from pydantic import BaseModel
import asyncio

router = APIRouter(prefix="/user" , tags=["users"], responses={404: {"message": "no encontrado"}})
# Entidad user 

class User(BaseModel):
    id: int
    name: str
    sub_name: str
    age: int
    url: str

# Operacion para devolver un JSON 

users_list = [User(id=1,name='norberto',sub_name='Hernandez',age=28,url='https://luigui.hernandez.com'),
                User(id=2,name='Sebastian',sub_name='Camargo',age=28,url='https://s02Camargo.com'),
                User(id=3,name='Maria',sub_name='Maturana',age=28,url='https://maturana_mariajosefa.com')]

# iniciar el serve: uvicorn router:user --reload



@router.get("/users")
async def users():
    return users_list


@router.get("/test")
async def test():
    return 'E$sta mas rapida  que loco quemado con brea '


# Path
# @router.get("/user_id/{id}")
# async def user_id(id: int):
#     return search_user(id)


# Query //  se usa asi => /user/?id=1
@router.get("/")
async def user_id(id: int):
    return search_user(id)



@router.post("/")
async def user(user: User):
    
    # Verifica si el ID ya existe en la lista 
    for existing_user in users_list:
        if existing_user.id == user.id:
            raise HTTPException(status_code=404, detail="Usuario ya exsite")
    users_list.routerend(user)
    return {"succes": "Usuario creado", "user":user}

@router.put("/")
async def user(update_user: User):
    found = False 
    for index, saved_user in enumerate(users_list):
        if saved_user.id ==  update_user.id:
            users_list[index] = update_user
            found = True
    if not found:
        raise HTTPException(status_code=404, detail="Usuario no actualizado")
    return {"saucces": "usuarion Actualizado", "user":update_user}


@router.delete("/{id}",status_code=200)
async def user(id:int):
        found = False 
        for index, saved_user in enumerate(users_list):
            if saved_user.id ==  id:
                del users_list[index]
                found = True
        if not found:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"saucces": "usuarion eliminado"}

def search_user (id: int):
    user = next((u for u in users_list if u.id == id ), None)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user
    





# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(router, host="0.0.0.0", port=8000)  
    
# # documemntacion con Swagger http://127.0.0.1:8000/docs