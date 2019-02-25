import importlib
import inspect
import sys

import pkg_resources
from django.conf import settings as django_settings
from django.core.management import CommandError
from grpc_tools import protoc

import django

from .exceptions import GrpcServerStartError

django.setup()


class GrpcService(object):
    def __init__(self, name, definition, stub_destination, stdout=None, stderr=None):
        self.stdout = stdout if stdout else sys.stdout
        self.stderr = stderr if stderr else sys.stderr

        self.name = name
        assert definition.get('proto_path'), 'Missing setting proto_path for service {}'.format(name)
        assert definition.get('rpc_path'), 'Missing setting rpc_path for service {}'.format(name)
        self.proto_path = definition['proto_path']
        self.proto_filename = self.proto_path.split('/')[-1]
        self.stub_destination = stub_destination
        self.rpcs = self.get_rpc_paths(definition['rpc_path'])

    def load(self):
        # Checks the gRPC server interfaces are generated or not
        if not self.find_stubs():
            raise GrpcServerStartError(
                "Failed to find gRPC server interface stubs for the service {}.\n"
                "Run 'python manage.py generate_grpc_stubs to generate them.".format(self.name)
            )


    @staticmethod
    def get_rpc_paths(path):
        return importlib.import_module(path).rpc_calls

    def find_stubs(self):
        dest = self.stub_destination + '.' if self.stub_destination != '.' else ''
        filename_without_ext = self.proto_filename.split('.')[0]
        pb = importlib.import_module('{}{}_pb2'.format(dest, filename_without_ext))
        pb_grpc = importlib.import_module('{}{}_pb2_grpc'.format(dest, filename_without_ext))
        return pb, pb_grpc

    def find_server_handler(self, pb_grpc):
        func_name = 'add_{}Servicer_to_server'.format(self.name)
        if not hasattr(pb_grpc, func_name):
            raise AttributeError('No server handler found')
        return getattr(pb_grpc, func_name)

    def find_servicer(self, pb_grpc):
        cls_name = '{}Servicer'.format(self.name)
        if not hasattr(pb_grpc, cls_name):
            raise AttributeError('No servicer class found')
        return getattr(pb_grpc, cls_name)

    @staticmethod
    def get_declared_methods(servicer):
        methods = inspect.getmembers(servicer, predicate=inspect.ismethod)
        return [x[0] for x in methods]

    def get_defined_methods(self):
        pass

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