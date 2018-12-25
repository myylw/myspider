import datetime
from contextlib import contextmanager


@contextmanager
def my_timeit():
    start = datetime.datetime.now().timestamp()
    try:
        yield
    finally:
        print(f'共耗时:{datetime.datetime.now().timestamp() - start}')


if __name__ == '__main__':
    import time


    def delay():
        time.sleep(2)


    with my_timeit():
        delay()
