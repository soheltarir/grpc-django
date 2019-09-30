import sys
from concurrent import futures

import grpc

from grpc_django.settings import settings


def init_server(addr, port, max_workers=1, stdout=sys.stdout):
    stdout.write("Performing system checks...\n\n")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    # Add services to server
    stdout.write("\nAdding GRPC services: {}\n\n".format(', '.join([x.name for x in settings.services])))
    for service in settings.services:
        servicer = service.load()
        handler = service.find_server_handler()
        handler(servicer, server)
    server.add_insecure_port("{}:{}".format(addr, port))
    return server
