import time
from typing import List, Callable


def _update_list_in_order(self, input_list: List, update_value: object, update_index: int,
                          stub_generator: Callable[[], object]) -> List:
    while True:
        try:
            input_list[update_index] = update_value
            return input_list
        except IndexError:
            input_list.append(stub_generator())


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
