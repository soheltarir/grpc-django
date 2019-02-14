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

from django.conf import settings


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
            raise AttributeError('Invalid service provide inside GRPC_SERVICES settings,'
                                 'should be a tuple similar to,'
                                 '(add_TestServiceServicer_to_server, TestServiceServicer, "tests.rpcs")')
        # Check whether the first index of the tuple is a function or not
        assert callable(definition[0]), "{} within GRPC_SERVICES setting, is not callable".format(definition[0])
        # Check whether the second index is a class or not
        assert inspect.isclass(definition[1]), "{} within GRPC_SERVICES setting, is expected to be a class".\
            format(definition[1])


DEFAULT_GRPC_PORT = 55000
DEFAULT_GRPC_SERVER_WORKERS = 5


class GRPCSettings:
    _default_meta_keys = {
        "AUTH_USER": "user",
        "JWT": "Authorization"
    }

    def __init__(self):
        # The GRPC Server Port
        self.server_port = getattr(settings, 'GRPC_PORT', DEFAULT_GRPC_PORT)

        # No. of threads
        self.workers = getattr(settings, 'GRPC_SERVER_WORKERS', DEFAULT_GRPC_SERVER_WORKERS)

        # List of services
        self.services = []
        _services = getattr(settings, 'GRPC_SERVICES', [])
        assert _services, "The GRPC_SERVICES setting cannot contain empty list, you must provide at least one service."
        for _service in _services:
            self.services.append(_ServiceSettings(_service))

        self.auth_user_metakey = self._default_meta_keys["AUTH_USER"]
        self.rpc_paths = []


grpc_settings = GRPCSettings()
