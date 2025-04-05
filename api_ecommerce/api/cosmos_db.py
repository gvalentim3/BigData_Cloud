from django.conf import settings
from azure.cosmos import CosmosClient, exceptions

from azure.cosmos import CosmosClient, exceptions as cosmos_exceptions
from django.conf import settings

class CosmosDB:
    def __init__(self):
        try:
            self.client = CosmosClient(
                url=settings.COSMOS_DB["URI"],
                credential=settings.COSMOS_DB["KEY"],
                retry_total=3,
                retry_backoff_max=10,
                consistency_level='Session',
                connection_policy={
                    'enable_endpoint_discovery': False,
                    'connection_mode': 'Gateway',
                    'request_timeout': 10 
                }
            )
            self.database = self.client.get_database_client(settings.COSMOS_DB["DATABASE_NAME"])
            self.containers = {
                "produtos": self.database.get_container_client(settings.COSMOS_DB["COLLECTIONS"]["PRODUTOS"]),
            }
        except cosmos_exceptions.CosmosHttpResponseError as e:
            raise Exception(f"Failed to initialize CosmosDB client: {str(e)}")

    def insert(self, document, container_name="produtos"):
        try:
            return self.containers[container_name].create_item(document)
        except KeyError:
            raise ValueError(f"Container {container_name} does not exist.")
        except cosmos_exceptions.CosmosHttpResponseError as e:
            raise Exception(f"Failed to insert document: {str(e)}")

    def find_by_id(self, id, partition_key, container_name="produtos"):
        try:
            return self.containers[container_name].read_item(id, partition_key=partition_key)
        except KeyError:
            raise ValueError(f"Container {container_name} does not exist.")
        except cosmos_exceptions.CosmosResourceNotFoundError:
            raise ValueError(f"Document with id {id} not found.")
        except cosmos_exceptions.CosmosHttpResponseError as e:
            raise Exception(f"Failed to fetch document: {str(e)}")

    def find_all(self, container_name="produtos"):
        try:
            return list(self.containers[container_name].query_items(
                query="SELECT * FROM c",
                enable_cross_partition_query=True
            ))
        except KeyError:
            raise ValueError(f"Container {container_name} does not exist.")
        except cosmos_exceptions.CosmosHttpResponseError as e:
            raise Exception(f"Failed to query documents: {str(e)}")

    def delete(self, id, partition_key, container_name="produtos"):
        try:
            return self.containers[container_name].delete_item(id, partition_key=partition_key)
        except KeyError:
            raise ValueError(f"Container {container_name} does not exist.")
        except cosmos_exceptions.CosmosResourceNotFoundError:
            raise ValueError(f"Document with id {id} not found.")
        except cosmos_exceptions.CosmosHttpResponseError as e:
            raise Exception(f"Failed to delete document: {str(e)}")
    