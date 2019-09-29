from django.conf import settings as django_settings

from .service import GRPCService
from .interfaces import ISettings, IService


class GRPCSettings:
    def __init__(self):
        # Extract GRPC Setting from Django settings
        _settings = getattr(django_settings, 'GRPC_SETTINGS')
        if not _settings:
            raise AssertionError("Missing GRPC_SETTINGS")
        if not isinstance(_settings, ISettings):
            raise AssertionError("Invalid object type provided for GRPC_SETTINGS, "
                                 "should be an instance of grpc_django.interfaces.GRPCSettings")

        # Server Port
        self.server_port = _settings.server.port

        # No. of worker threads
        self.workers = _settings.server.num_of_workers

        # List of services
        self.services = []
        assert _settings.services, "You must provide at least one gRPC service, in GRPC_SETTINGS.services"
        for service in _settings.services:
            assert isinstance(service, IService), "Invalid service definition provided"
            self.services.append(GRPCService(service))

        self.auth_user_meta_key = _settings.auth_user_key


settings = GRPCSettings()

__all__ = ['settings']
