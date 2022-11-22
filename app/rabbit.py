"""RabbitMQ helper class."""

import json
import time

import pika


class RabbitHelper:
    def __init__(self, host="localhost", timeout=60):
        """
        Создает подключение к RabbitMQ.
        Если RabbitMQ недоступен, попытка подключения повторится через timeout секунд.

        :param host: хост RabbitMQ для подключения
        """
        self.host = host
        try:
            self.connect()
        except pika.exceptions.AMQPConnectionError:
            time.sleep(timeout)
            self.connect()

    def connect(self):
        """Подключается к rabbitmq."""
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        self.channel = connection.channel()
        self.channel.basic_qos(prefetch_count=1)

    def add_consumer(
            self,
            exchange,
            callback,
            queue,
            exchange_type="direct",
            reply_exchange=None,
            reply_queue=""
    ):
        """
        Создает получателя, ожидающего сообщений от очереди queue обмена exchange.
        В случае типа обмена fanout необходимо указывать reply_exchange и reply_queue.

        :param exchange: наименование обмена
        :param callback: функция, применяемая к данным из сообщений
        :param queue: наименование очереди
        :param exchange_type: тип обмена
        :param reply_exchange: обмен для отправки результата
        :param reply_queue: очередь для отправки результата
        """
        RabbitConsumer(self.channel, exchange, callback, queue, exchange_type, reply_exchange, reply_queue)

    def start_consuming(self):
        """Запускает всех ранее созданных получателей"""
        self.channel.start_consuming()


class RabbitConsumer:
    def __init__(
            self,
            channel,
            exchange,
            callback,
            queue="",
            exchange_type="direct",
            reply_exchange=None,
            reply_queue=""
    ):
        """
        :param channel: канал
        :param exchange: наименование обмена
        :param callback: функция, применяемая к данным из сообщений
        :param queue: наименование очереди
        :param exchange_type: тип обмена
        :param reply_exchange: обмен для отправки результата
        :param reply_queue: очередь для отправки результата
        """
        self.exchange = exchange
        self.callback = callback
        self.exchange_type = exchange_type
        queue_ = channel.queue_declare(queue=queue,
                                       exclusive=(True if queue == "" else False),
                                       auto_delete=True,
                                       arguments={"x-expires": 60000})
        if self.exchange != "":
            channel.exchange_declare(self.exchange, exchange_type=exchange_type)
            channel.queue_bind(exchange=self.exchange, queue=queue_.method.queue)
        # reply_exchange и reply_queue нужно задавать при использовании exchange типа fanout.
        if reply_exchange is not None:
            reply_queue_ = channel.queue_declare(
                queue=reply_queue,
                exclusive=(True if reply_queue == "" else False),
                auto_delete=True,
                arguments={"x-expires": 60000}
            )
            self.reply_queue = reply_queue_.method.queue
            channel.exchange_declare(reply_exchange, exchange_type="direct")
            channel.queue_bind(exchange=reply_exchange, queue=self.reply_queue)
            self.reply_exchange = reply_exchange
        else:
            self.reply_queue = self.reply_exchange = None
        channel.basic_consume(
            queue=queue_.method.queue,
            on_message_callback=self.on_request
        )

    def on_request(self, ch, method, props, body):
        """Возвращает ответ в очередь"""
        response = self.callback(body)
        response = json.dumps(response)
        # Если данные пришли от fanout обмена,
        # то ответ нужно передать в очередь reply_queue обмена reply_exchange типа direct.
        # Иначе реализуется паттерн RPC и ответ передается в exchange.
        ch.basic_publish(
            exchange=(self.exchange if self.reply_exchange is None else self.reply_exchange),
            routing_key=(props.reply_to if self.reply_queue is None else self.reply_queue),
            properties=(
                None if self.exchange_type == "fanout" else pika.BasicProperties(correlation_id=props.correlation_id)
            ),
            body=str(response)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
