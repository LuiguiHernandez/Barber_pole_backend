from fastapi import APIRouter , Depends, HTTPException ,status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer , OAuth2PasswordRequestForm
from jose import jwt , JWTError
from passlib.context import CryptContext


from datetime import datetime , timedelta # esta importacion nos sirve pra trabajar con fechas y horas "timedelta" para trabajar con calculos de fechas 
import pytz

KEY = "1008951357"
ALGORITHM = "HS256" # Algoritmo de incriptacion 
ACCES_TOKEN_DURATION = 3  # duracion de la utenticacion del token 


router = APIRouter()


oauth2 = OAuth2PasswordBearer(tokenUrl="login")


crypt = CryptContext(schemes=["bcrypt"]) # contexto de incryptacion 


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
        "password": "$2a$12$IL0NCYBPGQaI.oLkefV1v.9rSM0vfcpqzGk.OmaUJG/pMU4pfroJ6" # contraseña incriptada 
    }, 
    "Maria":{
        "username": "Maria",
        "full_name": "Maria Matutrana" ,
        "email": "MariaM@gmail.com" ,
        "disabled": False,
        "password": "$2a$12$InDfgCBrEyndYZsUO898tO23eUhktd4DWxUk/b6byM88.jG2MlO0q" # contraseña incriptada 
    },
    "Sebastian":{
        "username": "Sebastian",
        "full_name": "Sebastian Camargo" ,
        "email": "Camargo_sebastian@gmail.com" ,
        "disabled": False,
        "password": "$2a$12$S2rTnhlAIn520cnoBK1O7O3z0cco1Gvh85JowrV632xLLe12ZifDS"  # contraseña incriptada 
    },
}



def search_user_db(username:str): 
    if username in user_db:  # Recorre con in el user_db Para encontrar el username 
        return UserDB(**user_db[username]) # devuelve el nombre del usuario encontrado 


def search_user(username:str): 
    if username in user_db:  # Recorre con in el user_db Para encontrar el username 
        return User(**user_db[username]) # devuelve el nombre del usuario encontrado 


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
    user_data = None  # Se inicializa user_data = None. Esto servirá para almacenar los datos del usuario si lo encontramos.
    for value in user_db.values():      # Se recorre el diccionario user_db, que contiene los datos de los usuarios registrados.
        if value["username"] == form.username:  # Se compara si el username del usuario en la base de datos coincide con form.username (el que envió el usuario en la solicitud).
            user_data = value  # Si hay una coincidencia, se guarda la información del usuario en user_data y se usa break para salir del bucle for.
            break
    if not user_data:
        raise HTTPException(status_code=400, detail="El usuario no es correcto")

    user = UserDB(**user_data)  # UserDB(**user_data) convierte el diccionario user_data en un objeto UserDB.
                                        # Esto permite acceder a los datos del usuario como atributos en lugar de claves de diccionario.
    
    # usamos la funcion Verify() y le damos como parametros , la contraseña enviada por el usuario y la contraseña almacenada en base de datos 
    
    if not crypt.verify(form.password , user.password): # compara la contraseña que envió el usuario (form.password) con la contraseña almacenada en la base de datos (user.password).
        raise HTTPException(status_code=400, detail="La contraseña no es correcta")
    
    
    acces_token_expiration = timedelta(minutes=ACCES_TOKEN_DURATION) 
    """
    timedelta es una función del módulo datetime que permite definir diferencias de tiempo (días, horas, minutos, segundos, etc.)
    • minutes=ACCESS_TOKEN_DURATION crea un período de tiempo basado en el valor de 
    ACCESS_TOKEN_DURATION (una variable que almacena cuántos minutos debe durar algo, como un token de autenticación)
    
    """
    utc_now = datetime.utcnow()
    timezone = pytz.timezone("America/Bogota")  # Cambia según tu zona
    local_time = utc_now.replace(tzinfo=pytz.utc).astimezone(timezone)
    
    
    expire = local_time + acces_token_expiration 
    
    """
    • pytz.timezone(...) es una función de la biblioteca pytz que permite obtener una zona horaria específica.
    • "America/Bogota" es el identificador de la zona horaria de Bogotá en la base de datos de zonas horarias de IANA (Internet Assigned Numbers Authority).
    • replace(tzinfo=pytz.utc). Asigna explícitamente la zona horaria UTC al objeto de fecha y hora.
    • astimezone(timezone). Convierte la hora UTC a la zona horaria de Bogotá (America/Bogota).
    • datetime.utcnow() obtiene la fecha y hora actual en formato UTC.
    • + timedelta(minutes=ACCESS_TOKEN_DURATION) suma 30 minutos al tiempo actual.
    
    """
    
    acces_token = {
        "sub": user.username,
        "exp": expire
    }
    
    return {"access_token": jwt.encode(acces_token, KEY , algorithm=ALGORITHM), "token_type": "bearer"}
    """
    • acces_token: Es un diccionario que representa la carga útil (payload) del JWT. Contiene información que se quiere incluir en el token, como el ID del usuario, la expiración, roles, etc.
    • KEY: Es la clave secreta usada para firmar el token. Si se usa un algoritmo de clave pública (como RS256), esta será la clave privada.
    • ALGORITHM: Especifica el algoritmo de firma utilizado. Puede ser, por ejemplo, "HS256" (HMAC con SHA-256) o "RS256" (RSA con SHA-256).
    •  jwt.encode(...): Codifica el diccionario acces_token en un token JWT firmado digitalmente.
    """


@router.get("/user/me")
async def me(user: User = Depends(current_user)):
    return user