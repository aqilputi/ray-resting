import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, List


class TaskManager:
    def __init__(self, callables: List[Callable]):
        self._callables = callables

    def run(self):
        """Método responsável por ligar as tarefas e mantelas em funcionamento.
        """
        with ThreadPoolExecutor(max_workers=len(self._callables)) as executor:
            mapped_tasks : dict[Future, Callable] = self._initialize_tasks(executor)

            self._keeps_tasks_running(executor, mapped_tasks)

    def _initialize_tasks(self, executor: ThreadPoolExecutor) -> dict[Future, Callable]:
        """Metodo responsavel por iniciar as tasks na pool de tasks.
        Os objetos instânciados são armazenados como chaves em um dicionário e seus valores a função callable usada para criar a task.

        Args:
            executor (ThreadPoolExecutor): Executor da pool de threads.

        Returns:
            dict[Future, Callable]: Mapeamento das inicializações das future das tarefas com seus callables.
        """
        futures = {}
        for _callable in self._callables:
            futures[executor.submit(_callable)] = _callable

        return futures

    def _keeps_tasks_running(self, executor: ThreadPoolExecutor, mapped_tasks: dict[Future, Callable]):
        """Método responsável por manter as tarefas funcionando.
        As tarefas que param por terem sido completadas com sucesso (esses caso não ocorre) ou falha são reiniciadas.

        Args:
            executor (ThreadPoolExecutor): Executor da pool de threads.
            mapped_tasks (dict[Future, Callable]): Mapeamento das inicializações das future das tarefas com seus callables.
        """
        while True:
            interrupted_tasks = self._get_interrupted_tasks(mapped_tasks)

            # if interrupted_tasks:
            #     mapped_tasks = self._retry_interrupted_tasks(executor, mapped_tasks, interrupted_tasks)

            time.sleep(3)

    def _get_interrupted_tasks(self, mapped_tasks: dict[Future, Callable]) -> list[Future]:
        """Método responsável por obter as tarefas que foram interrompidas por ter ocorrido uma exceção.

        Args:
            mapped_tasks (dict[Future, Callable]): Mapeamento das inicializações das future das tarefas com seus callables.

        Returns:
            list[Future]: Lista de future referente as tarefas que foram interrompidas.
        """
        interrupted_tasks = []

        for _task in mapped_tasks.keys():
            if not _task.running() and _task.exception():
                interrupted_tasks.append(_task)

        return interrupted_tasks

    def _retry_interrupted_tasks(self, executor: ThreadPoolExecutor, mapped_tasks: dict[Future, Callable], interrupted_tasks: list[Future]) -> dict[Future, Callable]:
        """Método responsável por reiniciar as tasks que foram interrompidas.

        Args:
            executor (ThreadPoolExecutor): Executor da pool de threads.
            mapped_tasks (dict[Future, Callable]): Mapeamento das inicializações das future das tarefas com seus callables.
            interrupted_tasks (list[Future]): Listas das tarefas interrompidas.

        Returns:
            dict[Future, Callable]: Mapeamento atualizado das futures inicializadas com as tasks reinicializadas.
        """
        for _task in interrupted_tasks:
            callable_future = mapped_tasks[_task]

            mapped_tasks.pop(_task)
            mapped_tasks[executor.submit(callable_future)] = callable_future

        return mapped_tasks
