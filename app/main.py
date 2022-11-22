"""Initializes and runs BioViewer AMR model."""
from config import settings
from model import Model
from rabbit import RabbitHelper


def main():
    """
    Initializes BioViewer AMR model with methods for direct and indirect AMR detection.
    Subscribes to RabbitMQ queues, returns calculation results in response for input data.
    """
    model = Model()

    methods = [
        {
            "name": "AMRDirect",
            "params": settings.get("AMR_PARAMS")
        }
    ]

    for method in methods:
        model.add_method(name=method['name'], params=method['params'])

    rabbit = RabbitHelper(
        host=settings.get("RABBIT_HOST"),
        timeout=settings.get("RABBIT_CONNECTION_TIMEOUT")
    )

    # Connects to the "status_container" fanout exchange
    # The response goes to "respond_status" queue if "model" exchange
    rabbit.add_consumer(
        exchange="status_container",
        queue="",
        callback=lambda x: model.get_description(),
        exchange_type="fanout",
        reply_exchange="model",
        reply_queue="respond_status"
    )

    # Connects model methods to the corresponding queues
    for method in methods:
        rabbit.add_consumer(
            exchange="model",
            queue="request_" + str(method["name"]),
            callback=lambda x, method_name=method["name"]: model.run_method(method_name, x)
        )
    # TODO try-except here
    rabbit.start_consuming()


if __name__ == '__main__':
    main()
