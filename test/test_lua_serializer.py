import functools

import pytest

import lua_serializer
import lua_wrangler


@pytest.mark.parametrize(
    ["text", "expected"],
    [
        ("foo", '"foo"'),
        ('"foo"', r'"\"foo\""'),
        (r"\"", r'"\\\""'),
        ("foo\nbar", '"foo\\nbar"'),
        ("über", '"über"'),
    ],
)
def test_make_lua_string(text, expected):
    assert lua_serializer.make_lua_string(text) == expected


@pytest.mark.parametrize(
    ["text", "expected"],
    [
        ("fooBAR123", "fooBAR123"),
        ("_private", "_private"),
        ("_INTERNAL", '["_INTERNAL"]'),
        ('"foo"', r'["\"foo\""]'),
        ("foo:bar", '["foo:bar"]'),
    ],
)
def test_make_lua_table_key(text, expected):
    assert lua_serializer.make_lua_table_key(text) == expected


SIGNPOST_DATA = [
    {
        "date": "2023-01-01",
        "subpage": "Arbitration report",
        "title": "Arbitration Committee Election 2022",
        "authors": ["Kudpung"],
        "tags": ["arbcom", "arbcomelection", "arbitrationreport"],
        "views": {
            "d007": 740,
            "d015": 1144,
            "d030": 1155,
            "d060": 1155,
            "d090": 1155,
            "d120": 1155,
            "d180": 1155,
        },
    },
    {
        "date": "2023-01-01",
        "subpage": "CommonsComix",
        "title": "#4: The Course of WikiEmpire",
        "authors": ["Adam Cuerden"],
        "tags": ["finance", "humour"],
        "views": {
            "d007": 705,
            "d015": 1123,
            "d030": 1134,
            "d060": 1134,
            "d090": 1134,
            "d120": 1134,
            "d180": 1134,
        },
    },
]

EXPECTED_SIGNPOST_LUA_TABLE = """{
	{
		date = "2023-01-01",
		subpage = "Arbitration report",
		title = "Arbitration Committee Election 2022",
		authors = {"Kudpung"},
		tags = {"arbcom", "arbcomelection", "arbitrationreport"},
		views = {d007 = 740, d015 = 1144, d030 = 1155, d060 = 1155, d090 = 1155, d120 = 1155, d180 = 1155},
	},
	{
		date = "2023-01-01",
		subpage = "CommonsComix",
		title = "#4: The Course of WikiEmpire",
		authors = {"Adam Cuerden"},
		tags = {"finance", "humour"},
		views = {d007 = 705, d015 = 1123, d030 = 1134, d060 = 1134, d090 = 1134, d120 = 1134, d180 = 1134},
	},
}"""


@pytest.mark.parametrize(
    [
        "obj",
        "indent",
        "indent_level",
        "min_single_line_indent_level",
        "table_sort_key",
        "expected",
    ],
    [
        (
            SIGNPOST_DATA,
            "\t",
            0,
            2,
            functools.cmp_to_key(lua_wrangler.compare_table_keys),
            EXPECTED_SIGNPOST_LUA_TABLE,
        ),
        (
            {"b": "b", "a": "a"},
            "\t",
            0,
            0,
            None,
            '{b = "b", a = "a"}',
        ),
        (
            {"b": "b", "a": "a"},
            "\t",
            0,
            0,
            str,
            '{a = "a", b = "b"}',
        ),
        (
            {"foo": "bar"},
            "  ",
            0,
            1,
            None,
            '{\n  foo = "bar",\n}',
        ),
        (
            {"foo": "bar"},
            "\t",
            1,
            2,
            None,
            '{\n\t\tfoo = "bar",\n\t}',
        ),
        (
            ["foo", "bar", "baz"],
            "\t",
            0,
            1,
            None,
            '{\n\t"foo",\n\t"bar",\n\t"baz",\n}',
        ),
        (
            ["foo", 7, -15.3, None, True, False],
            "\t",
            0,
            0,
            None,
            '{"foo", 7, -15.3, nil, true, false}',
        ),
    ],
)
def test_serialize(
    obj, indent, indent_level, min_single_line_indent_level, table_sort_key, expected
):
    actual = lua_serializer.serialize(
        obj,
        indent=indent,
        indent_level=indent_level,
        min_single_line_indent_level=min_single_line_indent_level,
        table_sort_key=table_sort_key,
    )
    assert actual == expected
