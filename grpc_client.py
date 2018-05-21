import grpc
import sys

from test_pb2 import GetPayload, Empty
from test_pb2_grpc import TestServiceStub


def run():
    channel = grpc.insecure_channel("localhost:8000")
    try:
        grpc.channel_ready_future(channel).result(timeout=10)
    except grpc.FutureTimeoutError:
        sys.exit('Error connecting to server')
    else:
        stub = TestServiceStub(channel)
    print("Calling GetUser with id = 1")
    response = stub.GetUser(GetPayload(id=1))
    if response:
        print("Received response for GetUser: {}".format(response))
    print("Calling ListUsers")
    response = stub.ListUsers(Empty())
    for _ in response:
        print(_)


if __name__ == "__main__":
    run()
