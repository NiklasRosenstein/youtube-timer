
import time
import threading
import sys


class ThreadHub:
  """
  """

  def __init__(self):
    self.events = {}
    self.lock = threading.Lock()
    self.threads = []

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, exc_tb):
    do_reraise = False
    if not exc_type:
      try:
        self.join()
      except:
        exc_type, exc_value, exc_tb = sys.exc_info()
        do_reraise = True

    if exc_type:
      self.set('stop')
      self.set('error')
      if issubclass(exc_type, KeyboardInterrupt):
        self.set('interrupt')

    self.join()
    if do_reraise:
      raise exc_value

  def is_set(self, event_name):
    with self.lock:
      event = self.events.get(event_name)
      if event:
        return event.is_set()
    return False

  def set(self, event_name):
    with self.lock:
      try:
        event = self.events[event_name]
      except KeyError:
        event = self.events[event_name] = threading.Event()
      event.set()

  def clear(self, event_name):
    with self.lock:
      event = self.events.get(event_name)
      if event:
        event.clear()

  def wait(self, event_name, timeout=None):
    with self.lock:
      event = self.events[event_name]
      if event:
        event.wait(timeout)

  def join(self, timeout=None):
    start_time = time.clock()
    for thread in self.threads:
      thread.join(timeout)
      if thread.is_alive():
        break
      if timeout is not None:
        current_time = time.clock()
        timeout -= (current_time - start_time)
        start_time = current_time
    self.threads[:] = (x for x in self.threads if x.is_alive())

  def start(self, __func, *args, **kwargs):
    return self.start_anonymous(__func, self, *args, **kwargs)

  def start_anonymous(self, __func, *args, **kwargs):
    def wrapper():
      try:
        __func(*args, **kwargs)
      except:
        self.set('error')
        self.set('stop')
        raise
    thread = threading.Thread(target=wrapper)
    self.threads.append(thread)
    thread.start()
    return thread

  def stop(self):
    self.set('stop')

  def stopped(self):
    return self.is_set('stop')
