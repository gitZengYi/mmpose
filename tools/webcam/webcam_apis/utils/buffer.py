# Copyright (c) OpenMMLab. All rights reserved.
import queue
from functools import wraps
from multiprocessing import Queue
from typing import List


def check_buffer_registered(exist=True):

    def wrapper(func):

        @wraps(func)
        def wrapped(manager, name, *args, **kwargs):
            if exist:
                # Assert buffer exist
                if name not in manager:
                    raise ValueError(f'Fail to call {func.__name__}: '
                                     f'buffer "{name}" is not registered.')
            else:
                # Assert buffer not exist
                if name in manager:
                    raise ValueError(f'Fail to call {func.__name__}: '
                                     f'buffer "{name}" is already registered.')
            return func(manager, name, *args, **kwargs)

        return wrapped

    return wrapper


class BufferManager():

    def __init__(self):
        self._buffers = {}

    def __contains__(self, name):
        return name in self._buffers

    @check_buffer_registered(False)
    def register_buffer(self, name, maxsize=0):
        self._buffers[name] = Queue(maxsize=maxsize)

    @check_buffer_registered()
    def put(self, name, item, block=True, timeout=None):
        self._buffers[name].put(item, block, timeout)

    @check_buffer_registered()
    def try_put(self, name, item):
        try:
            self._buffers[name].put_nowait(item)
            return True
        except queue.Full:
            return False

    @check_buffer_registered()
    def get(self, name, block=True, timeout=None):
        return self._buffers[name].get(block, timeout)

    @check_buffer_registered()
    def is_empty(self, name):
        return self._buffers[name].empty()

    @check_buffer_registered()
    def is_full(self, name):
        return self._buffers[name].full()

    def get_sub_manager(self, buffer_names: List[str]):
        buffers = {name: self._buffers[name] for name in buffer_names}
        return BufferManager(buffers)

    def get_info(self):
        buffer_info = {
            name: buffer.qsize()
            for name, buffer in self._buffers.items()
        }
        return buffer_info