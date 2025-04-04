# RabbitMQ AMQP 1.0 Python Client

This library is in early stages of development. It is meant to be used with RabbitMQ 4.0.

# Table of Contents

- [How to Build the project and run the tests](#How-to-Build-the-project-and-run-the-tests)
- [Installation](#Installation)
- [Getting started](#Getting-Started)
    * [Creating a connection](#Creating-a-connection)
    * [Managing resources](#Managing-resources)
    * [Publishing messages](#Publishing-messages)
    * [Consuming messages](#Consuming-messages)
    * [Support for streams](#support-for-streams)
    * [SSL connection](#ssl-connections)
    * [Oauth authentication](#oauth-authentication)
    * [Managing disconnections](#Managing-disconnections)


## How to Build the project and run the tests

- Start a RabbitMQ 4.x broker
- poetry build: build the source project
- poetry install: resolves and install dependencies
- poetry run pytest: run the tests

## Installation

The client is distributed via [`PIP`](https://pypi.org/project/rabbitmq-amqp-python-client/):
```bash
 pip install rabbitmq-amqp-python-client
```

## Getting Started

An example is provided [`here`](./examples/getting_started/getting_started.py) you can run it after starting a RabbitMQ 4.0 broker with:

poetry run python ./examples/getting_started/getting_started.py

Also consider to have a look to the examples documented in the RabbitMQ website: 

https://www.rabbitmq.com/client-libraries/amqp-client-libraries

### Creating a connection

A connection to the RabbitMQ AMQP 1.0 server can be established using the Environment object.

For example:

```python
    environment = Environment("amqp://guest:guest@localhost:5672/")
    connection = environment.connection()
    connection.dial()
```

### Managing resources

Once we have a Connection object we can get a Management object in order to submit to the server management operations
(es: declare/delete queues and exchanges, purging queues, binding/unbinding objects ecc...)

For example (this code is declaring an exchange and a queue:

```python
    management = connection.management()

    print("declaring exchange and queue")
    management.declare_exchange(ExchangeSpecification(name=exchange_name, arguments={}))

    management.declare_queue(
        QuorumQueueSpecification(name=queue_name)
    )
```

### Publishing messages

Once we have a Connection object we can get a Publisher object in order to send messages to the server (to an exchange or queue)

For example:

```python
    addr_queue = AddressHelper.queue_address(queue_name)
    publisher = connection.publisher(addr)

    # publish messages
    for i in range(messages_to_publish):
        publisher.publish(Message(body="test"))

    publisher.close()
```

### Consuming messages

Once we have a Connection object we can get a Consumer object in order to consumer messages from the server (queue).

Messages are received through a callback

For example:

Create a class which extends AMQPMessagingHandler which defines at minimum the on_consumer method, that will receive the 
messages consumed:

```python
class MyMessageHandler(AMQPMessagingHandler):

    def __init__(self):
        super().__init__()
        self._count = 0

    def on_message(self, event: Event):
        print("received message: " + str(event.message.body))

        # accepting
        self.delivery_context.accept(event)
```

Then from connection get a consumer object:

```python
    addr_queue = AddressHelper.queue_address(queue_name)
    consumer = connection.consumer(addr_queue, handler=MyMessageHandler())

    try:
        consumer.run()
    except KeyboardInterrupt:
        pass

    consumer.close()
```

The consumer will run indefinitively waiting for messages to arrive.

### Support for streams

The client natively supports streams: https://www.rabbitmq.com/blog/2021/07/13/rabbitmq-streams-overview

You can consume from a given offset or specify a default starting point (FIRST, NEXT, LAST).

Streams filtering is also supported: https://www.rabbitmq.com/blog/2023/10/16/stream-filtering

You can check the [`stream example`](./examples/streams/example_with_streams.py) to see how to work with RabbitMQ streams.

### SSL connections

The client supports TLS/SSL connections.

You can check the [`ssl example`](./examples/tls/tls_example.py) to see how to establish a secured connection

### Oauth authentication

The client supports oauth2 authentication.

You can check the [`oauth2 example`](./examples/oauth/oaut.py) to see how to establish and refresh a connection using an oauth2 token

### Managing disconnections

The client supports automatic reconnection with the ability to reconnect Managements, Producers and Consumers

You can check the [`reconnection example`](./examples/reconnection/reconnection_example.py) to see how to manage disconnections





