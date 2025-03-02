import time

from rabbitmq_amqp_python_client import (
    ConnectionClosed,
    Environment,
    StreamSpecification,
)
from rabbitmq_amqp_python_client.qpid.proton import Event, Handler

from .http_requests import delete_all_connections


def on_disconnected():

    print("disconnected")
    global disconnected
    disconnected = True


def test_connection() -> None:
    environment = Environment(uri="amqp://guest:guest@localhost:5672/")
    connection = environment.connection()
    connection.dial()
    environment.close()


def test_environment_context_manager() -> None:
    with Environment(uri="amqp://guest:guest@localhost:5672/") as environment:
        connection = environment.connection()
        connection.dial()


def test_connection_ssl(ssl_context) -> None:
    environment = Environment(
        "amqps://guest:guest@localhost:5671/",
        ssl_context=ssl_context,
    )

    connection = environment.connection()
    connection.dial()

    environment.close()


def test_environment_connections_management() -> None:

    environment = Environment(uri="amqp://guest:guest@localhost:5672/")
    connection = environment.connection()
    connection.dial()
    connection2 = environment.connection()
    connection2.dial()
    connection3 = environment.connection()
    connection3.dial()

    assert environment.active_connections == 3

    # this shouldn't happen but we test it anyway
    connection.close()

    assert environment.active_connections == 2

    connection2.close()

    assert environment.active_connections == 1

    connection3.close()

    assert environment.active_connections == 0

    environment.close()


def test_connection_reconnection() -> None:

    reconnected = False
    connection = None
    disconnected = False

    class DisconnectHandler(Handler):
        def on_connection_remote_close(self, event: Event) -> None:
            event.container.schedule(0, self)

        def on_timer_task(self, event: Event) -> None:
            nonlocal connection

            # reconnect
            if connection is not None:
                connection = environment.connection()
                connection.dial()

            nonlocal reconnected
            reconnected = True

    environment = Environment(
        "amqp://guest:guest@localhost:5672/", on_disconnection_handler=DisconnectHandler()
    )

    connection = environment.connection()
    connection.dial()

    # delay
    time.sleep(5)
    # simulate a disconnection
    delete_all_connections()
    # raise a reconnection
    management = connection.management()
    stream_name = "test_stream_info_with_validation"
    queue_specification = StreamSpecification(
        name=stream_name,
    )

    try:
        management.declare_queue(queue_specification)
    except ConnectionClosed:
        disconnected = True

    # check that we reconnected
    management = connection.management()
    management.declare_queue(queue_specification)
    management.delete_queue(stream_name)
    management.close()
    environment.close()

    assert disconnected is True
    assert reconnected is True
