from io import StringIO

import grpc
from django.test import TestCase

from grpc_django.server import init_server
from tests.grpc_codegen.test_pb2 import GetPayload, User, Empty
from tests.grpc_codegen.test_pb2_grpc import TestServiceStub


TEST_USERS = {
    1: User(id=1, name="Bruce Wayne", username='bruce.wayne'),
    2: User(id=2, name="Diana Prince", username='diana.prince')
}


class GrpcServerTest(TestCase):
    def setUp(self):
        self.users = TEST_USERS
        self.server = init_server('127.0.0.1', '55000', max_workers=1, stdout=StringIO())
        self.server.start()

    @property
    def client_stub(self):
        channel = grpc.insecure_channel("localhost:55000")
        grpc.channel_ready_future(channel).result(timeout=10)
        stub = TestServiceStub(channel)
        return stub

    def test_get(self):
        response = self.client_stub.GetUser(GetPayload(id=1))
        self.assertEqual(response, self.users[1])

    def test_list(self):
        response = self.client_stub.ListUsers(Empty())
        for _ in response:
            self.assertIsInstance(_, User)

    def tearDown(self):
        self.server.stop(0)
