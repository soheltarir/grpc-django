import importlib
import sys
from types import MethodType

import pkg_resources
from django.conf import settings as django_settings
from django.core.management import CommandError
from grpc_tools import protoc

from .exceptions import GrpcServerStartError
from .interfaces import IService, rpc
from .views import ServerStreamGRPCView


class GRPCService:
    def __init__(self, definition: IService, stdout=None, stderr=None):
        self.stdout = stdout if stdout else sys.stdout
        self.stderr = stderr if stderr else sys.stderr

        self.name = definition.name
        self.proto_path = definition.proto_path
        self.proto_filename = self.proto_path.split('/')[-1]
        self.stub_destination = definition.stub_conf
        self.rpcs = self.get_rpc_paths(definition.rpc_conf)

        # Internal Variables
        self._pb = None         # Protobuf message interfaces
        self._pb_grpc = None    # GRPC Service interfaces

    def load(self):
        pb, pb_grpc = self.find_stubs()
        # Checks the gRPC server interfaces are generated or not
        if not pb or not pb_grpc:
            raise GrpcServerStartError(
                "Failed to find gRPC server interface stubs for the service {}.\n"
                "Run 'python manage.py generate_grpc_stubs to generate them.".format(self.name)
            )

        servicer = self.find_servicer(pb_grpc)

        declared_methods = self.get_declared_methods(servicer)

        for _rpc in self.rpcs:
            assert isinstance(_rpc, rpc), "Invalid rpc definition {} provided".format(_rpc)
            # Check if the rpc is actually defined in the protocol buffer or not
            if _rpc.name not in declared_methods:
                raise LookupError("RPC {} doesn't exists in proto declarations".format(_rpc.name))
            # Add the method definition in servicer
            setattr(servicer, _rpc.name, MethodType(self._get_rpc_method(_rpc), servicer))
            declared_methods.remove(_rpc.name)

        # Show warning if a declared RPC is not implemented
        if len(declared_methods):
            print("*WARNING* Missing implementations for the RPCs: {}\n\n".format(declared_methods))
        return servicer

    @staticmethod
    def _get_rpc_method(_rpc: rpc):
        if issubclass(_rpc.view, ServerStreamGRPCView):
            def method(*args):
                yield from _rpc.view(args[1], args[2]).__call__()
        else:
            def method(*args):
                return _rpc.view(args[1], args[2]).__call__()
        return method

    @staticmethod
    def get_rpc_paths(path):
        return importlib.import_module(path).rpcs

    def find_stubs(self):
        dest = self.stub_destination + '.' if self.stub_destination != '.' else ''
        filename_without_ext = self.proto_filename.split('.')[0]
        pb = importlib.import_module('{}{}_pb2'.format(dest, filename_without_ext))
        pb_grpc = importlib.import_module('{}{}_pb2_grpc'.format(dest, filename_without_ext))
        self._pb, self._pb_grpc = pb, pb_grpc
        return pb, pb_grpc

    def find_server_handler(self):
        func_name = 'add_{}Servicer_to_server'.format(self.name)
        if not hasattr(self._pb_grpc, func_name):
            raise AttributeError('No server handler found')
        return getattr(self._pb_grpc, func_name)

    def find_servicer(self, pb_grpc):
        cls_name = '{}Servicer'.format(self.name)
        if not hasattr(pb_grpc, cls_name):
            raise AttributeError('No servicer class found')
        return getattr(pb_grpc, cls_name)

    @staticmethod
    def get_declared_methods(servicer):
        return [x for x in servicer.__dict__ if not x.startswith('__')]

    def generate_stubs(self):
        well_known_protos_include = pkg_resources.resource_filename(
            'grpc_tools', '_proto')
        command = [
            'grpc_tools.protoc',
            "--proto_path={}".format(django_settings.GRPC_PROTO_PATH),
            "--proto_path={}".format(well_known_protos_include),
            "--python_out={}".format(self.stub_destination),
            "--grpc_python_out={}".format(self.stub_destination),
        ] + [self.proto_path]
        if protoc.main(command) != 0:
            raise CommandError('Failed to generate proto stubs for {}'.format(self.proto_path))
