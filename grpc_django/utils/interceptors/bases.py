import six
import abc


class UnaryUnaryServerInterceptor(six.with_metaclass(abc.ABCMeta)):
    @abc.abstractmethod
    def intercept_unary_unary_handler(self, handler, method, request, servicer_context):
        """
        Intercepts unary-unary RPCs on the service-side.
        :param handler: The handler to continue processing the RPC. It takes a request value and a ServicerContext
                        object and returns a response value.
        :param method: The full method name of the RPC.
        :param request: The request value for the RPC.
        :param servicer_context: The context of the current RPC.
        :return: The RPC response
        """
        raise NotImplementedError()


class UnaryStreamServerInterceptor(six.with_metaclass(abc.ABCMeta)):
    @abc.abstractmethod
    def intercept_unary_stream_handler(self, handler, method, request, servicer_context):
        """
        Intercepts unary-stream RPCs on the service-side.
        :param handler: The handler to continue processing the RPC. It takes a request value and a ServicerContext
                        object and returns a response value.
        :param method: The full method name of the RPC.
        :param request: The request value for the RPC.
        :param servicer_context: The context of the current RPC.
        :return: An iterator of RPC response values.
        """
        raise NotImplementedError()


class StreamUnaryServerInterceptor(six.with_metaclass(abc.ABCMeta)):
    @abc.abstractmethod
    def intercept_stream_unary_handler(self, handler, method, request_iterator, servicer_context):
        """
        Intercepts stream-unary RPCs on the service-side.
        :param handler: The handler to continue processing the RPC. It takes a request value and a ServicerContext
                        object and returns a response value.
        :param method: The full method name of the RPC.
        :param request_iterator: An iterator of request values for the RPC.
        :param servicer_context: The context of the current RPC.
        :return: The RPC response.
        """
        raise NotImplementedError()


class StreamStreamServerInterceptor(six.with_metaclass(abc.ABCMeta)):
    @abc.abstractmethod
    def intercept_stream_stream_handler(self, handler, method, request_iterator, servicer_context):
        """
        Intercepts stream-stream RPCs on the service-side.
        :param handler: The handler to continue processing the RPC. It takes a request value and a ServicerContext
                        object and returns an iterator of response values.
        :param method: The full method name of the RPC.
        :param request_iterator: An iterator of request values for the RPC.
        :param servicer_context: The context of the current RPC.
        :return: An iterator of RPC response values.
        """
        raise NotImplementedError()
