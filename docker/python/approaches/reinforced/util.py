import socket
import time
from typing import List, Callable
from gym import spaces

def update_list_in_order(input_list: List, update_value: object, update_index: int,
                         stub_generator: Callable[[], object]) -> List:
    while True:
        try:
            input_list[update_index] = update_value
            return input_list
        except IndexError:
            input_list.append(stub_generator())


def get_available_port(address: str) -> int:
    s = socket.socket()
    s.bind((address, 0))
    available_port = s.getsockname()[1]
    s.close()
    return available_port


# Decorator:
def timer(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print(f'{method.__name__}, {(te - ts) * 1000} ms')
        return result

    return timed


def build_multidiscrete(nvec: list):
    space = []
    for val in nvec:
        space.append(spaces.Discrete(val))
    return spaces.Tuple(space)


def build_multibinary(n: int):
    return build_multi_space(spaces.Discrete(2), n)


def build_multi_space(duplicated_space, n: int):
    space = []
    for _ in range(n):
        space.append(duplicated_space)
    return spaces.Tuple(space)
