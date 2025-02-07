from fastapi import FastAPI , Depends, HTTPException ,status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer , OAuth2PasswordRequestForm


app = FastAPI()
oauth2 = OAuth2PasswordBearer(tokenUrl="login")


class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool

class UserDB(User):
    password: str




user_db = {
    "Luigui":{
        "username": "Luigui",
        "full_name": "Luigui Hernandez" ,
        "email": "Luiguibuelvas43@gmail.com" ,
        "disabled": False,
        "password": "Luigui.2024"
    }, 
    "Maria":{
        "username": "Maria",
        "full_name": "Maria Matutrana" ,
        "email": "MariaM@gmail.com" ,
        "disabled": False,
        "password": "Maria12548"
    },
    "Sebastian":{
        "username": "Sebastian",
        "full_name": "Sebastian Camargo" ,
        "email": "Camargo_sebastian@gmail.com" ,
        "disabled": False,
        "password": "Sebastian0258"
    },
}


def search_user_db(username:str): 
    if username in user_db:  # Recorre con in el user_db Para encontrar el username 
        return UserDB(**user_db[username]) # devuelve el nombre del usuario encontrado 
    

def search_user(username:str): 
    if username in user_db:  # Recorre con in el user_db Para encontrar el username 
        return User(**user_db[username]) # devuelve el nombre del usuario encontrado 


async def current_user(token:str = Depends(oauth2)):
    user = search_user(token)
    if not user:
        raise HTTPException(status_code=401,  
                            detail="Credenciales de atutenticacion invalidas" , 
                            headers={"www-Authenticate":"Bearer"})
    return user


@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_data = None  # Se inicializa user_data = None. Esto servirá para almacenar los datos del usuario si lo encontramos.
    for value in user_db.values():      # Se recorre el diccionario user_db, que contiene los datos de los usuarios registrados.
        if value["username"] == form.username:  # Se compara si el username del usuario en la base de datos coincide con form.username (el que envió el usuario en la solicitud).
            user_data = value  # Si hay una coincidencia, se guarda la información del usuario en user_data y se usa break para salir del bucle for.
            break
    if not user_data:
        raise HTTPException(status_code=400, detail="El usuario no es correcto")

    user = UserDB(**user_data)  # UserDB(**user_data) convierte el diccionario user_data en un objeto UserDB.
                                        # Esto permite acceder a los datos del usuario como atributos en lugar de claves de diccionario.

    if form.password != user.password: # Se compara la contraseña que envió el usuario (form.password) con la contraseña almacenada en la base de datos (user.password).
        raise HTTPException(status_code=400, detail="La contraseña no es correcta")
    
    
    """
        ♦ Si el usuario y la contraseña son correctos, se retorna un diccionario con:
        ♣ "access_token": user.username → En este caso, el token de acceso es simplemente el nombre de usuario.
        ♣ "token_type": "bearer" → Indica que el tipo de autenticación es Bearer Token.
        
    Nota:
        Este ejemplo no usa tokens JWT reales, sino que simplemente devuelve el username como token.
        En una implementación real, deberías generar un JWT Token con PyJWT o fastapi.security.
    """

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/user/me")
async def me(user: User = Depends(current_user)):
    return user