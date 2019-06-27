from progress import bar, spinner

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
            return spinner.Spinner(label).iter(iterator)
        else:
            return bar.Bar(label).iter(iterator)
    else:
        return iterator