import time
from typing import Iterable, Iterator, Sized, Union, overload

from progress import bar, spinner


def progress(
    iterator: Union[Iterable, Sized],
    out: bool = True,
    label: str = None,
    btype: str = "bar",
) -> Union[Iterable, Sized]:
    max_val = 0
    try:
        max_val = len(iterator)
    except TypeError:
        max_val = -1

    if max_val == 0:
        out = False

    if out:
        if label is None:
            label = "progress"

        if max_val < 0:
            return ProgressIterator(FastSpinner(label).iter(iterator), label)
        else:
            return ProgressIterator(FastBar(label).iter(iterator), label)
    else:
        return iterator


def clearln():
    print("\033[F\r\x1b[K", end="")


class FastBar(bar.Bar):
    suffix = "%(percent).1f%% - %(eta_td)s"

    def __init__(self, label):
        super(FastBar, self).__init__(label)
        self.last = time.time()

    def update(self):
        if time.time() - self.last > 0.1:
            self.last = time.time()
            super(FastBar, self).update()


class FastSpinner(spinner.Spinner):
    def __init__(self, label):
        super(FastSpinner, self).__init__(label)
        self.last = time.time()

    def update(self):
        if time.time() - self.last > 0.1:
            self.last = time.time()
            super(FastSpinner, self).update()


class ProgressIterator:
    def __init__(self, iterator, label):
        self.iterator = iterator
        self.starttime = time.time()
        self.label = label

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.iterator.__next__()
        except StopIteration:
            # print total time
            clearln()
            print("{0} ... {1:.2f}s".format(self.label, time.time() - self.starttime))
            raise StopIteration
