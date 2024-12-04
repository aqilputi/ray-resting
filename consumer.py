from downtime_analysis.consumer import RabbitMQConsumer, call_ray_app
import os
from typing import Callable

from task_manager import TaskManager



callables: list[Callable] = []
callables += [RabbitMQConsumer(call_ray_app).run for i in range(30)]
manager = TaskManager(callables=callables)
manager.run()
