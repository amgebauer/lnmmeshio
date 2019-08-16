from progress import bar, spinner
import time

def progress(iterator, out = True, label=None, btype='bar'):

    max_val = 0
    try:
        max_val = len(iterator)
    except TypeError:
        max_val = -1
    
    if max_val == 0:
        out = False

    if out:
        if label is None:
            label = 'progress'
        
        if max_val < 0:
            return ProgressIterator(spinner.Spinner(label).iter(iterator), label)
        else:
            return ProgressIterator(bar.Bar(label).iter(iterator), label)
    else:
        return iterator

def clearln():
    print('\033[F\r\x1b[K', end='')

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
            print('{0} ... {1:.2f}s'.format(self.label, time.time()-self.starttime))
            raise StopIteration