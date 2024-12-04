from downtime_analysis import consumer
import ray
from downtime_analysis.consumer import RabbitMQConsumer
from downtime_analysis.app import (
    GCSUrlSigner,
    RabbitMQPublisher,
    DowntimeDetectorWorker
)
from ray import serve
ray.init(
    "ray://localhost:10001",
    runtime_env={
        "working_dir": "./credentials",
        "pip": ["pika", "google-cloud-storage", "requests"],
        "env_vars": {
            "GOOGLE_APPLICATION_CREDENTIALS": "gcp_credentials.json",
        }
    }
)
# ray.shutdown("ray://localhost:10001")

url_signer_handle = GCSUrlSigner.bind()

# result_publisher_handle = RabbitMQPublisher.options(name="rabbit_pub", namespace="ray", lifetime="detached").remote()

worker_handle = DowntimeDetectorWorker.bind(
    url_signer_handle
)

# worker_handle.deploy()
# consumer_handler = RabbitMQConsumer.options(
# ).remote(worker_handle=worker_handle)

serve.start(detached=True)
serve.run(worker_handle)
# serve.run(url_signer_handle)
