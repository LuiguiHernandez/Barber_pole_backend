# instalar FastApi: pip install fastapi[all]
from fastapi import FastAPI
from routers import products , user , jwt_auth_user, user_db# ya con eso tenemos acceso ala api de products
from fastapi.staticfiles import StaticFiles


app = FastAPI()
# url Local http://127.0.0.1:8000

# routers 
app.include_router(user_db.router)
app.include_router(jwt_auth_user.router)
app.include_router(user.router)
app.include_router(products.router)
app.mount("/static", StaticFiles(directory="static"), name="static")





@app.get("/")
async def root():
    return ' Hola fastApi'



@app.get("/url")
async def url():
    return {"url":"https://mouredev.com/python"}

# Inica el server:  uvicorn main:app --reload
# Detener el server: CTRL+C

# Documentacion con Swagger: http://127.0.0.1:8000/doc
# Documentacion con Redocly: http://127.0.0.1:8000/redoc
