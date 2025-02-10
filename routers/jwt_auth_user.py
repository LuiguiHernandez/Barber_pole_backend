from fastapi import APIRouter , Depends, HTTPException ,status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer , OAuth2PasswordRequestForm
from jose import jwt , JWTError
from passlib.context import CryptContext
from pymongo import ReturnDocument
from db.client import db_client
from db.models.user import User
from db.schemas.user import user_schema , users_schema


from datetime import datetime , timedelta # esta importacion nos sirve pra trabajar con fechas y horas "timedelta" para trabajar con calculos de fechas 
import pytz


router = APIRouter()


oauth2 = OAuth2PasswordBearer(tokenUrl="login")


users_collection = db_client["users"]


# Configuración de seguridad
crypt = CryptContext(schemes=["bcrypt"], deprecated="auto") # contexto de incryptacion 
KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 30  # Minutos

class UserDB(User):
    password: str


def search_user_db(username: str):
    user_data = db_client.test.users.find_one({"username": username}) # type: ignore
    print(user_data) 
    if user_data:
        return UserDB(
            username=user_data["username"],
            full_name=user_data.get("full_name", "No Name"),  # Valor por defecto
            email=user_data["email"],
            disabled=user_data.get("disabled", False),
            password=user_data.get("password", "")  # Evita errores
        )



# def search_user_db(username:str): 
#     if username in db_client:  # Recorre con in el user_db Para encontrar el username 
#         return UserDB(**db_client[username]) # devuelve el nombre del usuario encontrado 

def search_user(username:str): 
    if username in db_client:  # Recorre con in el user_db Para encontrar el username 
        return User(**db_client[username]) # devuelve el nombre del usuario encontrado 


async def auth_user(token: str = Depends(oauth2)):
    
    execepcion = HTTPException(status_code=401,  
                            detail="Credenciales de atutenticacion invalidas" , 
                            headers={"www-Authenticate":"Bearer"})
    try:
        payload  = jwt.decode(token, KEY , algorithms=[ALGORITHM]) 
        """
        jwt.decode()• jwt.decode(token, KEY, algorithms=[ALGORITHM]) descifra el token y obtiene su contenido.
                    • algorithms=[ALGORITHM] debe ser una lista con un solo string, no una lista de listas.
        """
        username = payload.get("sub") # Obtiene el campo "sub" que representa el usuario.   
        
        if username is None: 
            raise execepcion
                
    except JWTError:
        raise execepcion
    return search_user(username)


async def current_user(user:User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(status_code=401,  
                            detail="Credenciales de atutenticacion invalidas" , 
                            headers={"www-Authenticate":"Bearer"})
    return user


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    # Buscar usuario en la base de datos
    user_data = users_collection.find_one({"username": form.username})
    print(db_client.list_collection_names())
    print(user_data)
    if not user_data:
        raise HTTPException(status_code=400, detail="El usuario no es correcto")
    
    # Convertir a esquema de usuario (asegúrate de que user_schema funciona bien)
    user_data = user_schema(user_data)
    
    # Simulación de usuario antes de guardar en MongoDB
    password = form.password  # Contraseña en texto plano
    hashed_password = crypt.hash(password)  # Hashea la contraseña
    print(hashed_password)  # Ver cómo se ve el hash
    
    # Actualizar y devolver el usuario modificado
    password_hash = user_schema(db_client.users.find_one_and_update(
        {"username": form.username}, # Filtro: usuario a actualizar
        {"$set": {"password":hashed_password}}, # Nueva contraseña hasheada
        return_document=ReturnDocument.AFTER 
    ))
    print("Contraseña actualizada correctamente:", password_hash)
    
    
    print(f"Contraseña almacenada en la BD: {user_data}")
    print(f"Contraseña ingresada: {form.password}")
    
    
    # Validar contraseña
    if not crypt.verify(form.password, user_data["password"]):
        raise HTTPException(status_code=400, detail="La contraseña no es correcta")
    print(f"Contraseña almacenada en la BD: {user_data['password']}")
    print(f"Contraseña ingresada: {form.password}")

    
    # Definir expiración del token
    acces_token_expiration = timedelta(minutes=ACCESS_TOKEN_DURATION)
    timezone = pytz.timezone("America/Bogota")
    local_time = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(timezone)
    expire = local_time + acces_token_expiration
    
    
    """
    timedelta es una función del módulo datetime que permite definir diferencias de tiempo (días, horas, minutos, segundos, etc.)
    • minutes=ACCESS_TOKEN_DURATION crea un período de tiempo basado en el valor de 
        ACCESS_TOKEN_DURATION (una variable que almacena cuántos minutos debe durar algo, como un token de autenticación)
    • pytz.timezone(...) es una función de la biblioteca pytz que permite obtener una zona horaria específica.
    • "America/Bogota" es el identificador de la zona horaria de Bogotá en la base de datos de zonas horarias de IANA (Internet Assigned Numbers Authority).
    • replace(tzinfo=pytz.utc). Asigna explícitamente la zona horaria UTC al objeto de fecha y hora.
    • astimezone(timezone). Convierte la hora UTC a la zona horaria de Bogotá (America/Bogota).
    • datetime.utcnow() obtiene la fecha y hora actual en formato UTC.
    • + timedelta(minutes=ACCESS_TOKEN_DURATION) suma 30 minutos al tiempo actual.
    
    """

    
    # Crear token
    acces_token = {
        "sub": user_data["username"],
        "exp": expire
    }

    return {"access_token": jwt.encode(acces_token, KEY, algorithm=ALGORITHM), "token_type": "bearer"}
    """
    • acces_token: Es un diccionario que representa la carga útil (payload) del JWT. Contiene información que se quiere incluir en el token, como el ID del usuario, la expiración, roles, etc.
    • KEY: Es la clave secreta usada para firmar el token. Si se usa un algoritmo de clave pública (como RS256), esta será la clave privada.
    • ALGORITHM: Especifica el algoritmo de firma utilizado. Puede ser, por ejemplo, "HS256" (HMAC con SHA-256) o "RS256" (RSA con SHA-256).
    •  jwt.encode(...): Codifica el diccionario acces_token en un token JWT firmado digitalmente.
    """


@router.get("/user/me")
async def me(user: User = Depends(current_user)):
    return user