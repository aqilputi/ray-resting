import json
from typing import Callable
import requests

def call_ray_app(data):
    res = requests.post("http://localhost:8000/DowntimeDetectorWorker", data=data)
    res.raise_for_status()
    return res

class RabbitMQConsumer:
    def __init__(self, callback: Callable):
        import os
        self.message_handler = callback
        self.rabbitmq_url = os.environ.get("RABBITMQ_URL")
        self.queue_name = os.environ.get("QUEUE_NAME")
        print(f"RabbitMQ URL: {self.rabbitmq_url}")
        print(f"Queue name: {self.queue_name}")

    def callback(self, ch, method, properties, body):
        import json
        print(f"Received {body}", flush=True)
        result = self.message_handler(body)
        if result:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_nack(delivery_tag=method.delivery_tag)

    def run(self):
        import pika
        print(f"Consuming messages from {self.queue_name} on {self.rabbitmq_url}", flush=True)
        connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
        channel = connection.channel()
        channel.basic_qos(prefetch_count=1)
        channel.queue_declare(queue=self.queue_name, durable=True)
        channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)
        while True:
            try:
                channel.start_consuming()
            except Exception as e:
                print(f"Error: {e}. Closing connection")
                break
        connection.close()
