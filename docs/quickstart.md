# Quickstart
We're going to create a simple service to view the users in the system.

## Project Setup
Create a new Django project named grpc_tutorial
```
# Create the project directory
$ mkdir grpc_tutorial
$ cd grpc_tutorial

# Create a virtualenv to isolate our package dependencies locally
$ virtualenv env
$ source env/bin/activate

# Install the packages into the virtualenv
$ pip install django
$ pip install djangorestframework
$ pip install grpc-django

# Set up a new project with a single application
$ django-admin startproject config .  # Note the trailing '.' character
$ python manage.py startapp users
```

The project layout should look like:
```
$ pwd
<some path>/grpc_tutorial
$ find .
.
./grpc_tutorial
./grpc_tutorial/__init__.py
./grpc_tutorial/settings.py
./grpc_tutorial/urls.py
./grpc_tutorial/wsgi.py
./users
./users/migrations
./users/migrations/__init__.py
./users/models.py
./users/__init__.py
./users/apps.py
./users/admin.py
./users/tests.py
./users/views.py
./manage.py
```
Now sync your database for the first time:
```
python manage.py migrate
```
Create the Protocol Buffer file `users/user.proto` and define the GRPC service:
```proto
syntax = "proto3";

package user;

message User {
    int64 id = 1;
    string username = 2;
    string first_name = 3;
    string last_name = 4;
}

message GetPayload {
    int64 id = 1;
}

message Empty {}

service UserService {
    rpc GetUser (GetPayload) returns (User);
    rpc ListUsers (Empty) returns (stream User);
}
```

## Settings
Add `'grpc_django'` to `INSTALLED_APPS`. The settings module will be in `grpc_tutorial/settings.py`.
```
INSTALLED_APPS = (
    ...
    'grpc_django',
)
```
Add `GRPC_SETTINGS` in the settings module
```python
from grpc_django import GRPCSettings, GRPCService


GRPC_SETTINGS = GRPCSettings(
    services=[GRPCService(
        # Name of the service as defined in .proto definition
        name='UserService',
        # The package name as defined in .proto definition (in our case it should look like `package user;`
        package_name='user',
        # The path (relative to `manage.py`) to the .proto definition 
        proto_path='users/user.proto',
        # This will be the list of RPCs similar to `urls.py` definition in Django
        rpc_conf='users.rpc'
    )]
)

```

## Generating the client and server code
Next you need to generate the gRPC client and server interfaces from your `users/user.proto` service
definition.

First, install the `grpcio-tools` package:
```
$ pip install grpcio-tools
```

Use the following Django management command to generate the Python code:
```
$ python manage.py generate_grpc_stubs
```

The above command will generate a python package `grpc_codegen` containing the following modules:
```
./manage.py
...
./grpc_codegen
./grpc_codegen/__init__.py
./grpc_codegen/user_pb2.py
./grpc_codegen/user_pb2_grpc.py
...
```

## Serializers
Now we're going to define some serializers using Django REST framework. Let's create a new module
named `users/serializers.py` that we'll be used for data representations.
```python
from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username')

```
Please refer [DjangoRESTFramework - Serializers](https://www.django-rest-framework.org/api-guide/serializers/) for
detailed usage of serializers

## RPCs
We are gonna write some RPCs in `users/views.py` which should look familiar to Django Views 
or Django REST Framework Views
```python
from grpc_django.views import RetrieveGRPCView, ServerStreamGRPCView
from grpc_codegen.user_pb2 import User as UserProto
from django.contrib.auth.models import User
from .serializers import UserSerializer

class GetUser(RetrieveGRPCView):
    """
    RPC to view a single user by ID
    """
    queryset = User.objects.all()
    response_proto = UserProto
    serializer_class = UserSerializer


class ListUsers(ServerStreamGRPCView):
    """
    RPC to list all users
    """
    queryset = User.objects.all()
    response_proto = UserProto
    serializer_class = UserSerializer
```

Similar to **urls.py** in Django, where we define API endpoints and link them to respective views,
in GRPC Django we are gonna link views to corresponding RPCs as defined in the `users/user.proto` file.
Create a module `users/rpcs.py` with the following:
```python
from grpc_django.interfaces import rpc
from .views import GetUser, ListUsers


rpcs = [
    rpc(name='GetUser', view=GetUser),
    rpc(name='ListUsers', view=ListUsers)
]
```

## Running the Server
Finally you can run your gRPC server by the following command:
```
$ python manage.py run_grpc_server
```
This will run your gRPC server on `127.0.0.1:55000`

## Testing Our Service
To test our gRPC service we need to create a client that would use the generated client code to
access the RPCs. Create a python module `test_grpc_client.py`, and write the following sample code in it:
```python
import grpc
import sys

from grpc_codegen.user_pb2 import GetPayload, Empty
from grpc_codegen.user_pb2_grpc import UserServiceStub


def run():
    # Create a connection with the server
    channel = grpc.insecure_channel("localhost:55000")
    try:
        grpc.channel_ready_future(channel).result(timeout=10)
    except grpc.FutureTimeoutError:
        sys.exit('Error connecting to server')
    else:
        stub = UserServiceStub(channel)
        
    # Test the GetUser RPC
    print("Calling GetUser with id = 1")
    response = stub.GetUser(GetPayload(id=1))
    if response:
        print("Received response for GetUser: {}".format(response))
    
    # Test the ListUsers RPC
    print("Calling ListUsers")
    response = stub.ListUsers(Empty())
    for _ in response:
        print(_)

    # Close the connection
    channel.close()


if __name__ == "__main__":
    run()

```
Run the above code using `python test_grpc_client.py`
