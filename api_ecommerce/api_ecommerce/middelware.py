from django.http import JsonResponse
import os

class CosmosAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip Swagger UI requests
        if not request.path.startswith('/swagger/') and not request.path.get('Authorization'):
            request.META['HTTP_AUTHORIZATION'] = f"Bearer {os.getenv('COSMOS_PRIMARY_KEY')}"
        return self.get_response(request)