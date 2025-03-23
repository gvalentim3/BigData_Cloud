from django.apps import AppConfig
from .cosmos_db import CosmosDB


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

# Inicializa a conexão com o Cosmos DB.
cosmos_db = CosmosDB()