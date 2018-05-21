from grpc_django.settings import settings
from test_pb2_grpc import TestServiceServicer, add_TestServiceServicer_to_server

settings.add_service(add_TestServiceServicer_to_server, TestServiceServicer, "tests.rpcs")
