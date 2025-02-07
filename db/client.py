### MongoDB  Client ###
# modulo de conexcion MongoDB :  pip install pymongo

from pymongo import MongoClient

# base de datos local 
# db_client = MongoClient().local


# base de satos remota 
db_client = MongoClient(
    "mongodb+srv://luiguibuelvas43:Luigui.2024@cluster0.qab4d.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    ).test
