from django.core.exceptions import ObjectDoesNotExist

from grpc_django.rpcs import rpc
from grpc_django.views import RetrieveGRPCView, ServerStreamGRPCView
from test_pb2 import User

USERS = [{
            "id": 1,
            "name": "Clay Jenson",
            "username": "clay.jenson"
        }, {
            "id": 2,
            "name": "Clary Fairchild",
            "username": "clary.fairchild"
        }]


class UserSerializer:
    def __init__(self, obj):
        self.obj = obj

    @property
    def data(self):
        return self.obj


class GetUser(RetrieveGRPCView):
    response_proto = User
    serializer_class = UserSerializer

    def get_queryset(self):
        return USERS

    def get_object(self):
        users = self.get_queryset()
        for user in users:
            if user["id"] == getattr(self.request, self.lookup_kwarg):
                return user
        raise ObjectDoesNotExist("User matching query does not exists.")


class ListUsers(ServerStreamGRPCView):
    response_proto = User
    serializer_class = UserSerializer

    def get_queryset(self):
        return USERS


rpc_calls = [
    rpc("GetUser", GetUser),
    rpc("ListUsers", ListUsers)
]
