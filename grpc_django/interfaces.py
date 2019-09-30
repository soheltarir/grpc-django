from collections import namedtuple
from typing import List


rpc = namedtuple('rpc', ['name', 'view'])


class IService:
    _DEFAULT_STUB_MODULE = 'grpc_codegen'

    def __init__(
            self,
            name: str,
            package_name: str,
            proto_path: str,
            rpc_conf: str,
            stub_conf: str = None,
    ):
        self.name = name
        self.package_name = package_name
        self.proto_path = proto_path
        self.rpc_conf = rpc_conf
        self.stub_conf = stub_conf if stub_conf else self._DEFAULT_STUB_MODULE


class IServer:
    DEFAULT_SERVER_PORT = 55000
    DEFAULT_WORKER_COUNT = 1

    def __init__(self, port: int = None, num_of_workers: int = None):
        if port and type(port) != int:
            raise TypeError("Invalid port provided, should be int")
        self.port = port if port else self.DEFAULT_SERVER_PORT

        if num_of_workers and type(num_of_workers) != int:
            raise TypeError("Invalid num_of_workers provided, should be int")
        self.num_of_workers = num_of_workers if num_of_workers else self.DEFAULT_WORKER_COUNT


class ISettings:
    DEFAULT_AUTHENTICATION_KEY = 'user'
    DEFAULT_CODEGEN_LOCATION = 'grpc_codegen'

    def __init__(
            self,
            services: List[IService],
            server: IServer = None,
            auth_user_key: str = None,
            stubs: str = None
    ):
        self.services = services
        self.server = server if server else IServer()
        self.auth_user_key = auth_user_key if auth_user_key else self.DEFAULT_AUTHENTICATION_KEY
        self.stubs = stubs if stubs is not None else self.DEFAULT_CODEGEN_LOCATION


__all__ = ['IService', 'ISettings', 'IServer', 'rpc']
