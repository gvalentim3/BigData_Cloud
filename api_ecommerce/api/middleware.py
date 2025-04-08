from django.http import HttpResponseForbidden
from ipaddress import ip_address, ip_network

class CustomAllowedHostsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_nets = [
            ip_network('169.254.0.0/16') 
        ]

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        try:
            ip = ip_address(host)
            if any(ip in net for net in self.allowed_nets):
                return self.get_response(request)
        except ValueError:
            pass
        return HttpResponseForbidden("Host without permission")