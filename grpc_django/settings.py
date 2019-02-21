"""
Settings for GRPC Django are all namespaced in the GRPC_* settings.
For example your project's `settings.py` file might look like this:
GRPC_PORT = 55001
GRPC_SERVICES = [
    (add_TestServiceServicer_to_server, TestServiceServicer, "tests.rpcs")
]
This module provides the `grpc_setting` object, that is used to access
GRPC Django settings, checking for user settings first, then falling
back to the defaults.
"""
import importlib
import inspect

from django.conf import settings as django_settings


DEFAULT_GRPC_PORT = 55000
DEFAULT_GRPC_SERVER_WORKERS = 5


class GrpcService(object):
    def __init__(self, name: str, definition: dict):
        self.name = name
        assert definition.get('proto_path'), 'Missing setting proto_path for service {}'.format(name)
        assert definition.get('rpc_path'), 'Missing setting rpc_path for service {}'.format(name)
        self.proto_path = definition['proto_path']
        self.rpcs = self.get_rpc_paths(definition['rpc_path'])

    @staticmethod
    def get_rpc_paths(path: str):
        return importlib.import_module(path).rpc_calls


class _ServiceSettings:
    def __init__(self, definition: tuple):
        """
        :param definition: The service definition
        """
        self.validate(definition)
        self.service = definition[0]
        self.servicer = definition[1]
        self.rpcs = self.get_rpc_paths(definition[2])

    @staticmethod
    def get_rpc_paths(module_path: str):
        return importlib.import_module(module_path).rpc_calls

    @staticmethod
    def validate(definition):
        if not isinstance(definition, tuple) or len(definition) != 3:
            raise AttributeError('Invalid service provide inside GRPC_SERVICES settings '
                                 'should be a tuple similar to '
                                 '(add_TestServiceServicer_to_server, TestServiceServicer, "tests.rpcs")')
        # Check whether the first index of the tuple is a function or not
        assert callable(definition[0]), "{} within GRPC_SERVICES setting, is not callable".format(definition[0])
        # Check whether the second index is a class or not
        assert inspect.isclass(definition[1]), "{} within GRPC_SERVICES setting, is expected to be a class".\
            format(definition[1])


class GRPCSettings:
    _default_meta_keys = {
        "AUTH_USER": "user",
        "JWT": "Authorization"
    }

    def __init__(self):
        # The GRPC Server Port
        self.server_port = getattr(django_settings, 'GRPC_PORT', DEFAULT_GRPC_PORT)

        # No. of threads
        self.workers = getattr(django_settings, 'GRPC_SERVER_WORKERS', DEFAULT_GRPC_SERVER_WORKERS)

        # Protobuf file/s location

        # List of services
        self.services = []
        _services = getattr(django_settings, 'GRPC_SERVICES', {})
        assert _services, "The GRPC_SERVICES setting cannot be empty, you must provide at least one service."
        assert isinstance(_services, dict), "The GRPC_SERVICES settings should be a dict"
        for name, definition in _services.items():
            self.services.append(GrpcService(name, definition))

        # List of interceptors

        self.auth_user_metakey = self._default_meta_keys["AUTH_USER"]
        self.rpc_paths = []


settings = GRPCSettings()

__all__ = ['settings']
