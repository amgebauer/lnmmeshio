from collections import OrderedDict
import re

def read_dat_sections(origin):
    """
    Reads a dat file format and returns a dictionary containing of the sections with their lines

    Args:
        origin: File hander to read from
    
    Returns:
        dict: Dictionary with section names as key and lines as value
    """
    content = {}

    re_title = re.compile(r'^-{3,}(.*)')

    current_section = ''
    content[current_section] = []
    for line in origin:
        line_no_comment = line.split('//', 1)[0].strip()
        match_title = re_title.match(line_no_comment)
        if match_title:
            # this is a section title
            current_section = match_title.group(1)
            if current_section in content:
                raise ValueError('{0} is dublicate!'.format(current_section))

            content[current_section] = []
        else:
            content[current_section].append(line)
    
    return content

def read_option_item(line: str, option: str, num: int = 1):
    regex = re.compile('(^| ){0}{1}\\s'.format(re.escape(option), num*'[ ]+([\\S]+)'))

    # split comment
    line = line.split('//', 1)[0]

    # read option
    match = regex.search(line)

    if not match:
        return None, None
    
    if num == 1:
        return match.group(2), match.span(0)
    else:
        return [match.group(i) for i in range(2, num+2)], match.span(0)

def read_next_key(line):
    regex = re.compile(r'^[ ]*(\S+)\s*')

    # split comment
    line = line.split('//', 1)[0]

    # read option
    match = regex.search(line)

    if not match:
        return None, None
    
    # shorten line by parsed option
    line = line[match.span(0)[1]:]
    return line, match.group(1)

def read_next_value(line, num: int = 1):
    regex = re.compile('^[ ]*{0}\\s*'.format('[ ]+'.join(['([\\S]+)' for i in range(0, num)])))

    # split comment
    line = line.split('//', 1)[0]

    # read option
    match = regex.search(line)

    if not match:
        return None, None, None
    
    # shorten line by parsed option
    line = line[match.span(0)[1]:]

    return line, [match.group(i) for i in range(1, num+1)]


def read_next_option(line: str, num: int = 1):
    regex = re.compile('^[ ]*(\\S+){0}\\s*'.format(num*'[ ]+([\\S]+)'))

    # split comment
    line = line.split('//', 1)[0]

    # read option
    match = regex.search(line)

    if not match:
        return None, None, None
    
    # shorten line by parsed option
    line = line[match.span(0)[1]:]
    key = match.group(1)
    value = match.group(2)

    return line, match.group(1), [match.group(i) for i in range(2, num+2)]

def text_fill(text: str, length: int, chr=' ', minimum=1, fill_left: bool = False):
    fill_str: str = chr*max(minimum, length-len(text))

    if fill_left:
        return '{1}{0}'.format(text, fill_str)
    else:
        return '{0}{1}'.format(text, fill_str)

def write_title(dest, title: str, newline = True):
    dest.write('{0}{1}'.format(text_fill(title, 73, chr='-', minimum=3, fill_left=True), '\n' if newline else ''))

def write_option(dest, key: str, value, comment: str = None, newline = True):

    if comment is not None:
        dest.write('{0}{1}// {2}{3}'.format(
            text_fill(key, 32, chr=' '),
            text_fill(str(value), 32, chr=' '),
            comment,
            '\n' if newline else ''
        ))
    else:
        dest.write('{0}{1}{2}'.format(
            text_fill(key, 32, chr=' '),
            str(value),
            '\n' if newline else ''
        ))

def write_option_list(dest, list: OrderedDict, newline=True):

    first_entry: bool = True
    for key, value in list.items():
        if not first_entry:
            dest.write(' ')
        first_entry = False

        if hasattr(value, '__iter__') and not isinstance(value, str):
            val_str = ' '.join([str(i) for i in value])
        else:
            val_str = value

        dest.write('{0} {1}'.format(key, val_str))
    
    if newline:
        dest.write('\n')

def write_comment(dest, comment, newline = True):
    dest.write('// {0}{1}'.format(comment, '\n' if newline else ''))