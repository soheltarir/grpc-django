import importlib
import time
from concurrent import futures
from contextlib import contextmanager
from types import MethodType

import grpc
from django.core.management import BaseCommand, CommandError

from grpc_django.views import ServerStreamGRPCView


class Command(BaseCommand):
    help = "Starts the GRPC server"

    def add_arguments(self, parser):
        parser.add_argument(
            "project", nargs=1,
            help="Django project settings path"
        )
        parser.add_argument(
            "port", nargs="?",
            help="Optional port number"
        )
        parser.add_argument(
            "--workers", dest="max_workers",
            help="Number of maximum worker threads"
        )

    @staticmethod
    def _get_rpc_method(rpc_call):
        if issubclass(rpc_call.cls, ServerStreamGRPCView):
            def method(*args):
                yield from rpc_call.cls(args[1], args[2]).__call__()
        else:
            def method(*args):
                return rpc_call.cls(args[1], args[2]).__call__()
        return method

    @contextmanager
    def serve_forever(self, settings, **kwargs):
        max_workers = kwargs.get("max_workers", settings.workers)
        server_port = kwargs.get("port", settings.server_port)
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
        # Add services to server
        for service in settings.services:
            self.stdout.write("Adding service {}".format(service.service.__name__))
            servicer = service.service()
            # Add methods
            rpc_calls = importlib.import_module(service.rpc_paths).rpc_calls
            for rpc_call in rpc_calls:
                setattr(
                    servicer,
                    rpc_call.name,
                    MethodType(self._get_rpc_method(rpc_call), servicer)
                )
            service.servicer(servicer, server)
        server.add_insecure_port("[::]:{}".format(server_port))
        server.start()
        yield
        server.stop(0)

    def handle(self, *args, **options):
        project_module = importlib.import_module(".".join([options["project"][0], "grpc"]))
        project_settings = project_module.settings

        if not options.get("port"):
            port = project_settings.server_port
        else:
            port = options["port"]
            if not port.isdigit():
                raise CommandError("{} is not a valid port number".format(port))
        with self.serve_forever(project_settings, port=port):
            self.stdout.write("Running GRPC server on localhost:{}".format(port))
            try:
                while True:
                    time.sleep(60*60*24)
            except KeyboardInterrupt:
                pass
