from .bases import UnaryUnaryServerInterceptor, UnaryStreamServerInterceptor, StreamStreamServerInterceptor, \
    StreamUnaryServerInterceptor


def intercept_server(server, *interceptors):
    """
    Creates an intercepted server.
    :param server: A Server object
    :param interceptors: Zero or more objects of type UnaryUnaryServerInterceptor, UnaryStreamServerInterceptor,
                        StreamUnaryServerInterceptor, or StreamStreamServerInterceptor.
                        Interceptors are given control in the order they are listed.
    :return: A Server that intercepts each received RPC via the provided interceptors.
    :raises: TypeError: If interceptor does not derive from any of
               UnaryUnaryServerInterceptor,
               UnaryStreamServerInterceptor,
               StreamUnaryServerInterceptor,
               StreamStreamServerInterceptor.
    """
    from . import _interceptor
    return _interceptor.intercept_server(server, *interceptors)
