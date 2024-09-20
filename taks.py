## Little utility tool to prevent thread spamming with threading.Timer

from dataclasses import dataclass
import time
from typing import Callable

@dataclass(eq=True, frozen=True)
class Task:
  delay: int
  func: Callable
  created_at: float  

# ExecutorPool is a class that manages a set of Task objects.
# It will be run every cheat loop

class TaskPool:
  pool = set()

  @staticmethod
  def new(delay: int, func: Callable):
    TaskPool.add(Task(delay, func, time.time()))

  @staticmethod
  def add(task: Task):
    TaskPool.pool.add(task)

  @staticmethod
  def remove(task: Task):
    TaskPool.pool.remove(task)

  @staticmethod
  def run():

    # Sets should not be modified while iterating over them
    # but our threads can modify the pool while we are iterating
    cp = TaskPool.pool.copy()

    to_remove = set()

    for task in cp:
      if time.time() - task.created_at > task.delay / 1000:
        task.func()
        to_remove.add(task)

    for task in to_remove:
      TaskPool.remove(task)
    
    del to_remove
    del cp



