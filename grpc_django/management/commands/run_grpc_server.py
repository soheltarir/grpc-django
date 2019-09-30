import re
import time
from contextlib import contextmanager
from datetime import datetime
from ipaddress import ip_address

from django.conf import settings as django_settings
from django.core.management import BaseCommand, CommandError

from grpc_django.server import init_server
from grpc_django.settings import settings
from grpc_django.views import ServerStreamGRPCView

naiveip_re = re.compile(r"""^(?:(?P<addr>(?P<ipv4>\d{1,3}(?:\.\d{1,3}){3}) |):)?(?P<port>\d+)$""", re.X)


class Command(BaseCommand):
    help = "Starts a GRPC server"

    default_addr = '127.0.0.1'

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
        self.stdout.write("Performing system checks...\n\n")
        self.check_migrations()
        server = init_server(addr, port, max_workers=kwargs.get('max_workers', 1), stdout=self.stdout)
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
        server.start()
        yield
        server.stop(0)

    @staticmethod
    def get_addrport(value):
        error_msg = '"{}" is not a valid port number or address:port pair.'.format(value)
        parts = value.split(':')
        if len(parts) > 2:
            raise CommandError(error_msg)
        if len(parts) == 1:
            addr = settings.server_port
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
        # Initialise Settings
        if not options.get('addrport'):
            addr, port = self.default_addr, settings.server_port
        else:
            addr, port = self.get_addrport(options['addrport'])
        with self.serve_forever(addr=addr, port=port):
            try:
                while True:
                    time.sleep(60*60*24)
            except KeyboardInterrupt:
                pass
