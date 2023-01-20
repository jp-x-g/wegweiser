from collections.abc import Iterable, Mapping
import json
import math
from numbers import Number
import re

LUA_RESTRICTED_TOKENS = {
    "and",
    "break",
    "do",
    "else",
    "elseif",
    "end",
    "false",
    "for",
    "function",
    "if",
    "in",
    "local",
    "nil",
    "not",
    "or",
    "repeat",
    "return",
    "then",
    "true",
    "until",
    "while",
}


def make_lua_string(s):
    if not isinstance(s, str):
        raise TypeError(f"make_lua_string expects strings ({type(s).__name__} given)")
    return json.dumps(s)


lua_name_regex = re.compile("[_a-zA-Z][_a-zA-Z0-9]*")  # Basic Lua name requirements
lua_internal_regex = re.compile("_[A-Z]+")  # Reserved for internal Lua use


def make_lua_table_key(s):
    if (
        s not in LUA_RESTRICTED_TOKENS
        and lua_name_regex.fullmatch(s)
        and not lua_internal_regex.fullmatch(s)
    ):
        return s
    else:
        return "[" + make_lua_string(s) + "]"


def is_object(obj):
    return isinstance(obj, Iterable) and not isinstance(obj, str)


def is_one_line(obj, *, indent_level, min_single_line_indent_level):
    for item in obj:
        if is_object(item):
            return False
    return indent_level >= min_single_line_indent_level


def add_lua_sequence(
    obj, ret, *, indent, indent_level, min_single_line_indent_level, table_sort_key
):
    one_line = is_one_line(
        obj,
        indent_level=indent_level,
        min_single_line_indent_level=min_single_line_indent_level,
    )
    next_indent_level = indent_level + 1
    ret.append("{")
    for i, item in enumerate(obj):
        if not one_line:
            ret.append("\n")
            ret += [indent] * next_indent_level
        add_lua_code(
            item,
            ret,
            indent=indent,
            indent_level=next_indent_level,
            min_single_line_indent_level=min_single_line_indent_level,
            table_sort_key=table_sort_key,
        )
        if not one_line:
            ret.append(",")
        elif i < len(obj) - 1:
            ret.append(", ")
    if not one_line:
        ret.append("\n")
        ret += [indent] * indent_level
    ret.append("}")


def add_lua_table(
    obj, ret, *, indent, indent_level, min_single_line_indent_level, table_sort_key
):
    one_line = is_one_line(
        obj,
        indent_level=indent_level,
        min_single_line_indent_level=min_single_line_indent_level,
    )
    next_indent_level = indent_level + 1
    ret.append("{")
    props = obj.keys()
    if table_sort_key is not None:
        props = sorted(props, key=table_sort_key)
    for i, prop in enumerate(props):
        if not one_line:
            ret.append("\n")
            ret += [indent] * next_indent_level
        ret.append(make_lua_table_key(prop))
        ret.append(" = ")
        add_lua_code(
            obj[prop],
            ret,
            indent=indent,
            indent_level=next_indent_level,
            min_single_line_indent_level=min_single_line_indent_level,
            table_sort_key=table_sort_key,
        )
        if not one_line:
            ret.append(",")
        elif i < len(props) - 1:
            ret.append(", ")
    if not one_line:
        ret.append("\n")
        ret += [indent] * indent_level
    ret.append("}")


def add_lua_code(
    obj, ret, *, indent, indent_level, min_single_line_indent_level, table_sort_key
):
    if obj is None:
        ret.append("nil")
    elif obj is True:
        ret.append("true")
    elif obj is False:
        ret.append("false")
    elif isinstance(obj, str):
        ret.append(make_lua_string(obj))
    elif isinstance(obj, Number):
        ret.append(str(obj))
    elif isinstance(obj, Mapping):
        add_lua_table(
            obj,
            ret,
            indent=indent,
            indent_level=indent_level,
            min_single_line_indent_level=min_single_line_indent_level,
            table_sort_key=table_sort_key,
        )
    elif isinstance(obj, Iterable):
        add_lua_sequence(
            obj,
            ret,
            indent=indent,
            indent_level=indent_level,
            min_single_line_indent_level=min_single_line_indent_level,
            table_sort_key=table_sort_key,
        )
    else:
        raise TypeError(f"Cannot serialize type {type(obj).__name__}")


def serialize(
    obj,
    *,
    indent="\t",
    indent_level=0,
    min_single_line_indent_level=math.inf,
    table_sort_key=None,
):
    """
    Serializes a Python object to a Lua table.

    Args:
        obj (number, int, float, str, dict, list): The object to serialize.
        indent (str, optional): The string to indent with, e.g. "\t" or "  ".
        indent_level (int, optional): The initial indentation level.
        min_single_line_indent_level (int, optional): At this indentation level
            or above, tables will be formatted on a single line.
        table_sort_key (Callable, optional): A key function with which to sort
            keys of Lua tables. If not specified, the table is not sorted. For
            details of key functions, see
            https://docs.python.org/3/howto/sorting.html#key-functions.

    Returns:
        string: A serialized Lua data table string.
    """
    ret = []
    add_lua_code(
        obj,
        ret,
        indent=indent,
        indent_level=indent_level,
        min_single_line_indent_level=min_single_line_indent_level,
        table_sort_key=table_sort_key,
    )
    return "".join(ret)
