"""
    Example-based and property-based tests for safe PowerShell argument
    composition.
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import pytest

from hypothesis import given, strategies as st

from ccai.errors.exceptions import SemanticError

from ccai.interop.hyperv.pwsh.pwshquote import pwsh_quote, pwsh_unquote


def test_quote_plain_value():
    quoted = pwsh_quote(value="MyVM01")
    assert quoted == "'MyVM01'"
    return


def test_quote_doubles_single_quotes():
    quoted = pwsh_quote(value="it's a vm")
    assert quoted == "'it''s a vm'"
    return


def test_quote_leaves_metacharacters_literal():
    tricky = "a;b|c$d`e\"f"
    quoted = pwsh_quote(value=tricky)
    assert quoted == "'" + tricky + "'"
    return


def test_quote_rejects_newline():
    with pytest.raises(SemanticError):
        pwsh_quote(value="line1\nline2")
    return


def test_quote_rejects_carriage_return():
    with pytest.raises(SemanticError):
        pwsh_quote(value="line1\rline2")
    return


def test_quote_rejects_null_byte():
    with pytest.raises(SemanticError):
        pwsh_quote(value="bad\x00value")
    return


def test_quote_is_deterministic():
    first = pwsh_quote(value="C:\\VMs\\disk's.vhdx")
    second = pwsh_quote(value="C:\\VMs\\disk's.vhdx")
    assert first == second
    return


_SAFE_TEXT = st.text(
    alphabet=st.characters(
        blacklist_characters="\n\r\x00",
        min_codepoint=32, max_codepoint=126,
    ),
    min_size=0, max_size=80,
)


@given(value=_SAFE_TEXT)
def test_quote_roundtrip_is_identity(value):
    quoted = pwsh_quote(value=value)
    recovered = pwsh_unquote(literal=quoted)
    assert recovered == value
    return


@given(value=_SAFE_TEXT)
def test_quote_output_is_single_quoted(value):
    quoted = pwsh_quote(value=value)
    assert quoted[0] == "'"
    assert quoted[-1] == "'"
    return


@given(prefix=_SAFE_TEXT, suffix=_SAFE_TEXT)
def test_quote_rejects_embedded_newline_anywhere(prefix, suffix):
    with pytest.raises(SemanticError):
        pwsh_quote(value=prefix + "\n" + suffix)
    return
