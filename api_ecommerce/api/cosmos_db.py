from django.conf import settings
from pymongo import MongoClient

class CosmosDB:
    def __init__(self):
        """
        Initialize the Cosmos DB connection and collections.
        """
        self.client = MongoClient(
            settings.COSMOS_DB["URI"],
            username=settings.COSMOS_DB["NAME"],  # Replace with your Cosmos DB username if needed
            password=settings.COSMOS_DB["KEY"],
            tls=True,  # Enable TLS for secure connection
            tlsAllowInvalidCertificates=True,  # Allow self-signed certificates (for local development)
        )
        self.db = self.client[settings.COSMOS_DB["DATABASE_NAME"]]
        self.collections = {
            "produtos": self.db[settings.COSMOS_DB["COLLECTIONS"]["PRODUTOS"]],
            "pedidos": self.db[settings.COSMOS_DB["COLLECTIONS"]["PEDIDOS"]],
        }
    def insert(self, document):
        """
        Insere um documento na coleção do CosmosDB.
        """
        return self.collection.insert_one(document)

    def find_by_id(self, id):
        """
        Acha um documento pelo ID.
        """
        return self.collection.find_one({"id": id})

    def find_all(self):
        """
        Acha todos os documentos do Banco de dados.
        """
        return list(self.collection.find({}))

    def delete(self, id):
        """
        Deleta o documento pelo ID.
        """
        return self.collection.delete_one({"id": id})