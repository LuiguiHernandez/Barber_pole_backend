# Usa una imagen de Python como base
FROM python:3.11

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Instala las dependencias del archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 8000
EXPOSE 8000

# Comando para ejecutar la API con uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
