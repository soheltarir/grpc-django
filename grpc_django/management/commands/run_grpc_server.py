import importlib
import re
import time
from concurrent import futures
from contextlib import contextmanager
from datetime import datetime
from ipaddress import ip_address
from types import MethodType

import grpc
from django.core.management import BaseCommand, CommandError
from django.conf import settings as django_settings

from grpc_django.settings import settings
from grpc_django.views import ServerStreamGRPCView


naiveip_re = re.compile(r"""^(?:(?P<addr>(?P<ipv4>\d{1,3}(?:\.\d{1,3}){3}) |):)?(?P<port>\d+)$""", re.X)


class Command(BaseCommand):
    help = "Starts a GRPC server"

    default_addr = '127.0.0.1'
    default_port = '55000'

    def add_arguments(self, parser):
        parser.add_argument(
            "addrport", nargs="?",
            help="Optional port number, or ipaddr:port"
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
    def serve_forever(self, addr, port, **kwargs):
        max_workers = kwargs.get("max_workers", 1)
        self.stdout.write("Performing system checks...\n\n")
        self.check_migrations()
        self.stdout.write(datetime.now().strftime('%B %d, %Y - %X'))
        self.stdout.write(
            "Django version {version}, using settings {settings}\n"
            "Starting GRPC server at {addr}:{port}".format(**{
                'version': self.get_version(),
                'settings': django_settings.SETTINGS_MODULE,
                'addr': addr,
                'port': port
            })
        )
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
        server.add_insecure_port("{}:{}".format(addr, port))
        server.start()
        yield
        server.stop(0)

    def get_addrport(self, value):
        error_msg = '"{}" is not a valid port number or address:port pair.'.format(value)
        parts = value.split(':')
        if len(parts) > 2:
            raise CommandError(error_msg)
        if len(parts) == 1:
            addr = self.default_port
            port = parts[0]
            if not port.isdigit():
                raise CommandError(error_msg)
        else:
            addr, port = parts
            try:
                ip_address(addr)
            except ValueError:
                raise CommandError(error_msg)
        return addr, port

    def handle(self, *args, **options):
        if not options.get('addrport'):
            addr, port = self.default_addr, self.default_port
        else:
            addr, port = self.get_addrport(options['addrport'])
        with self.serve_forever(addr=addr, port=port):
            try:
                while True:
                    time.sleep(60*60*24)
            except KeyboardInterrupt:
                pass
