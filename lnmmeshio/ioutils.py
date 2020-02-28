import io
import re
import struct
from collections import OrderedDict

import numpy as np

from .progress import progress


def read_dat_sections(origin):
    """
    Reads a dat file format and returns a dictionary containing of the sections with their lines

    Args:
        origin: File hander to read from

    Returns:
        dict: Dictionary with section names as key and lines as value
    """
    content = {}

    re_title = re.compile(r"^-{3,}(.*)")

    current_section = ""
    content[current_section] = []
    for line in progress(origin, label="Read input"):
        line_no_comment = line.split("//", 1)[0].strip()
        match_title = re_title.match(line_no_comment)
        if match_title:
            # this is a section title
            current_section = match_title.group(1)
            if current_section in content:
                raise ValueError("{0} is dublicate!".format(current_section))

            content[current_section] = []
        else:
            content[current_section].append(line)

    return content


def read_option_item(line: str, option: str, num: int = 1):
    regex = re.compile(
        r"(^| ){0}{1}($|\s)".format(re.escape(option), num * "[ ]+([\\S]+)")
    )

    # split comment
    line = line.split("//", 1)[0]

    # read option
    match = regex.search(line)

    if not match:
        return None, None

    if num == 1:
        return match.group(2), match.span(0)
    else:
        return [match.group(i) for i in range(2, num + 2)], match.span(0)


def read_ints(line: str, option: str, num: int) -> np.array:
    str_items = read_option_item(line, option, num)[0]

    if str_items is None:
        raise RuntimeError("Could not find int array {1} in {0}".format(line, option))

    int_items = None
    try:
        int_items = [int(i) for i in str_items]
    except TypeError:
        int_items = [int(str_items)]
    return np.array(int_items)


def read_int(line: str, option: str) -> int:
    return read_ints(line, option, 1)[0]


def read_floats(line: str, option: str, num: int) -> np.array:
    str_items = read_option_item(line, option, num)[0]

    if str_items is None:
        raise RuntimeError("Could not find float array {1} in {0}".format(line, option))

    if isinstance(str_items, str):
        str_items = [str_items]
    float_items = None
    try:
        float_items = [float(i) for i in str_items]
    except TypeError:
        float_items = [float(str_items)]
    return np.array(float_items)


def read_float(line: str, option: str) -> int:
    return read_floats(line, option, 1)[0]


def read_next_key(line):
    regex = re.compile(r"^[ ]*(\S+)\s*")

    # split comment
    line = line.split("//", 1)[0]

    # read option
    match = regex.search(line)

    if not match:
        return None, None

    # shorten line by parsed option
    line = line[match.span(0)[1] :]
    return line, match.group(1)


def read_next_value(line, num: int = 1):
    regex = re.compile(
        "^[ ]*{0}\\s*".format("[ ]+".join(["([\\S]+)" for i in range(0, num)]))
    )

    # split comment
    line = line.split("//", 1)[0]

    # read option
    match = regex.search(line)

    if not match:
        return None, None, None

    # shorten line by parsed option
    line = line[match.span(0)[1] :]

    return line, [match.group(i) for i in range(1, num + 1)]


def read_next_option(line: str, num: int = 1):
    regex = re.compile("^[ ]*(\\S+){0}\\s*".format(num * "[ ]+([\\S]+)"))

    # split comment
    line = line.split("//", 1)[0]

    # read option
    match = regex.search(line)

    if not match:
        return None, None, None

    # shorten line by parsed option
    line = line[match.span(0)[1] :]
    match.group(1)
    match.group(2)

    return line, match.group(1), [match.group(i) for i in range(2, num + 2)]


def text_fill(text: str, length: int, chr=" ", minimum=1, fill_left: bool = False):
    fill_str: str = chr * max(minimum, length - len(text))

    if fill_left:
        return "{1}{0}".format(text, fill_str)
    else:
        return "{0}{1}".format(text, fill_str)


def line_title(title: str):
    return text_fill(title, 73, chr="-", minimum=3, fill_left=True)


def write_title(dest, title: str, newline=True):
    dest.write("{0}{1}".format(line_title(title), "\n" if newline else ""))


def line_option(key: str, value, comment: str = None):
    if comment is not None:
        return "{0}{1}// {2}".format(
            text_fill(key, 32, chr=" "), text_fill(str(value), 32, chr=" "), comment
        )
    else:
        return "{0}{1}".format(text_fill(key, 32, chr=" "), str(value))


def write_option(dest, key: str, value, comment: str = None, newline=True):
    dest.write(
        "{0}{1}".format(line_option(key, value, comment), "\n" if newline else "")
    )


def line_option_list(list: OrderedDict):
    line = io.StringIO()
    first_entry: bool = True
    for key, value in list.items():
        if not first_entry:
            line.write(" ")
        first_entry = False

        if hasattr(value, "__iter__") and not isinstance(value, str):
            val_str = " ".join([str(i) for i in value])
        else:
            val_str = value

        line.write("{0} {1}".format(key, val_str))

    return line.getvalue()


def write_option_list(dest, options: OrderedDict, newline=True):
    dest.write("{0}{1}".format(line_option_list(options), "\n" if newline else ""))


def line_comment(comment):
    return "// {0}".format(comment)


def write_comment(dest, comment, newline=True):
    dest.write("{0}{1}".format(line_comment(comment), "\n" if newline else ""))


def ens_write_floats(file_handle, arr: np.array, binary=True):
    """reads array of length floats"""
    if binary:
        np.ravel(arr, "F").astype("<f").tofile(file_handle)
    else:
        for f in np.ravel(arr, "F").astype("<f"):
            ens_write_float(file_handle, f, binary)


def ens_write_ints(file_handle, arr: np.array, binary=True):
    if binary:
        np.ravel(arr).astype("<i").tofile(file_handle)
    else:
        if len(arr.shape) == 2:
            for i in range(arr.shape[0]):
                for j in range(arr.shape[1]):
                    ens_write_int(
                        file_handle, int(arr[i, j]), binary=binary, newline=False
                    )
                ens_write_string(file_handle, "", False)
        else:
            for i in np.ravel(arr, "F").astype("<i"):
                ens_write_int(file_handle, i, binary=binary)


def ens_write_int(file_handle, i, binary=True, newline=True):
    if binary:
        file_handle.write(struct.pack("i", i))
    else:
        s = str(i)
        file_handle.write(
            " " * (10 - len(s)) + s + "{0}".format("\n" if newline else "")
        )


def ens_write_float(file_handle, v, binary=True):
    if binary:
        file_handle.write(struct.pack("f", v))
    else:
        if v >= 0:
            file_handle.write(" ")
        file_handle.write("{0:10.5e}\n".format(v))


def ens_write_string(file_handle, s, binary=True):
    ws = ""

    if binary:
        ws = s[:80]
        ws = s + "\0" * (80 - len(s))
        ws = ws.encode("ascii")
    else:
        ws = s + "\n"

    file_handle.write(ws)
