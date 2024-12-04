import ray
from ray import serve
import time
import requests

@serve.deployment(
    ray_actor_options={"num_cpus": 0.2, "memory": 500 * 1024 * 1024},
    autoscaling_config={
        "target_num_ongoing_requests_per_replica": 1,
        "min_replicas": 0,
        "initial_replicas": 1,
        "max_replicas": 20,
    },
)
# @ray.remote
class DowntimeDetectorWorker:
    def __init__(
        self,
        gcs_url_signer_handle
    ):
        self.gcs_url_signer = serve.get_deployment_handle('GCSUrlSigner')

    async def __call__(self, data):
        import json
        success = False
        try:
            print("c")
            result = await self.gcs_url_signer.sign_url.remote(data)
            print(result)
            success = True
        except Exception as e:
            print(f"Error: {e}")
        return success

@serve.deployment(
)
class GCSUrlSigner:
    def __init__(self):
        import os
        from google.oauth2 import service_account

        self.credentials = service_account.Credentials.from_service_account_file(
            os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        )
        self.client_email = self.credentials.service_account_email
        print("bbb")

    def sign_url(self, data):
        print("aaa")

@ray.remote
def request_inference(signed_url):
    import requests

    frame_as_bytes = requests.get(signed_url).content
    response = requests.post(
        "http://localhost:8000/",
        data=frame_as_bytes
    )
    return response.json()

@ray.remote(
    runtime_env={
        "pip": ["pika"],
        "env_vars": {
            "RABBITMQ_URL": "amqp://processing-pipeline:pipe123@10.128.0.102:5672/mediasnap",
            "EXCHANGE_NAME": "downtime_results",
            "QUEUE_NAME": "downtime_results",
            "RAY_ENABLE_RECORD_ACTOR_TASK_LOGGING": "1"
        },
    },
)
class RabbitMQPublisher:
    def __init__(self):
        import os
        self.rabbitmq_url = os.environ.get("RABBITMQ_URL")
        self.exchange_name = os.environ.get("EXCHANGE_NAME")
        self.queue_name = os.environ.get("QUEUE_NAME")
        print(f"RabbitMQ URL: {self.rabbitmq_url}")
        print(f"Queue name: {self.queue_name}")

    def publish_result(self, result):
        import pika
        import json
        try:
            print(f"Publishing result: {result}")
            connection = pika.BlockingConnection(
                parameters=pika.URLParameters(self.rabbitmq_url)
            )
            channel = connection.channel()
            channel.queue_declare(
                queue=self.queue_name,
                durable=True
            )
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
