from django.conf import settings
from azure.cosmos import CosmosClient, exceptions

class CosmosDB:
    def __init__(self):
        self.client = CosmosClient(
            settings.COSMOS_DB["URI"],
            credential=settings.COSMOS_DB["KEY"],
            connection_verify=False  
            username=settings.COSMOS_DB["NAME"],
            tls=True,
            tlsAllowInvalidCertificates=True,
        )
        self.database = self.client.get_database_client(settings.COSMOS_DB["DATABASE_NAME"])
        self.containers = {
            "produtos": self.database.get_container_client(settings.COSMOS_DB["COLLECTIONS"]["PRODUTOS"]),
            "pedidos": self.database.get_container_client(settings.COSMOS_DB["COLLECTIONS"]["PEDIDOS"]),
        }
        self.collection = self.containers["produtos"]  # Default collection

    def insert(self, document):
        """Insert a document into Cosmos DB"""
        return self.collection.create_item(document)

    def find_by_id(self, id, partition_key):
        """Find document by ID and partition key"""
        return self.collection.read_item(id, partition_key=partition_key)

    def find_all(self):
        """Query all documents"""
        return list(self.collection.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))

    def delete(self, id, partition_key):
        """Delete a document"""
        return self.collection.delete_item(id, partition_key=partition_key)