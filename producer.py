payload = {"name": "open-closed-event", "image_url": "gs://rc-pflamboyant-1-snap/2024-11-29/pflamboyant_1_2024-11-29T01:30:00-03:00.jpg", "camera_id": "1", "shop_id": "pflamboyant", "timestamp": 1732854603.435714, "date": "2024-11-29"}


class RabbitMQPublisher:
    def __init__(self):
        import os
        self.rabbitmq_url = os.environ.get("RABBITMQ_URL")
        self.exchange_name = os.environ.get("EXCHANGE_NAME", 'msnap-default-exchange')
        self.queue_name = os.environ.get("QUEUE_NAME")
        print(f"RabbitMQ URL: {self.rabbitmq_url}")
        print(f"Queue name: {self.queue_name}")

    def publish_result(self):
        import pika
        import json
        try:
            result = payload
            print(f"Publishing result: {result}")
            connection = pika.BlockingConnection(
                parameters=pika.URLParameters(self.rabbitmq_url)
            )
            channel = connection.channel()
            channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )
            while True:
                channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key=self.queue_name,
                    body=json.dumps(result)
                )
            connection.close()
            print(f"Result published")
        except Exception as e:
            print(f"Error: {e}")
            raise e

p = RabbitMQPublisher()
from typing import Callable
from task_manager import TaskManager



callables: list[Callable] = []
callables += [RabbitMQPublisher().publish_result for i in range(30)]
manager = TaskManager(callables=callables)
manager.run()
