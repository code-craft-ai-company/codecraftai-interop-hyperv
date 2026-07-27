"""
    Tests for PwshScriptBuilder deterministic command rendering.
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from ccai import testbase


from ccai.testbase.properties import given
from ccai.testbase.properties import strategies as st

from ccai.errors.exceptions import SemanticError

from ccai.interop.hyperv.pwsh.pwshscriptbuilder import PwshScriptBuilder


def test_render_simple_cmdlet():
    builder = PwshScriptBuilder(cmdlet="Get-VMHost")
    rendered = builder.render()
    assert rendered == "Get-VMHost | ConvertTo-Json -Depth 6 -Compress"
    return


def test_render_with_parameter():
    builder = PwshScriptBuilder(cmdlet="Get-VM")
    builder.parameter(name="Name", value="vm01")
    rendered = builder.render()
    assert "Get-VM -Name 'vm01'" in rendered
    return


def test_render_without_json():
    builder = PwshScriptBuilder(cmdlet="Start-VM")
    builder.parameter(name="Name", value="vm01")
    builder.without_json()
    rendered = builder.render()
    assert rendered == "Start-VM -Name 'vm01'"
    return


def test_render_argv_shape():
    builder = PwshScriptBuilder(cmdlet="Get-VMHost")
    argv = builder.render_argv()
    assert argv[0] == "pwsh"
    assert "-NoProfile" in argv
    assert "-Command" in argv
    return


def test_literal_parameter_rejects_injection():
    builder = PwshScriptBuilder(cmdlet="New-VM")
    with testbase.raises(SemanticError):
        builder.literal_parameter(name="Count", value="4; rm -rf /")
    return


def test_param_name_must_be_alphanumeric():
    builder = PwshScriptBuilder(cmdlet="New-VM")
    with testbase.raises(SemanticError):
        builder.parameter(name="Na me", value="x")
    return


def test_cmdlet_rejects_statement_separator():
    with testbase.raises(SemanticError):
        PwshScriptBuilder(cmdlet="Get-VM; Remove-VM")
    return


_NAME_TEXT = st.text(
    alphabet=st.characters(
        blacklist_characters="\n\r\x00",
        min_codepoint=32, max_codepoint=126,
    ),
    min_size=1, max_size=40,
)


@given(name=_NAME_TEXT)
def test_render_is_deterministic_over_arbitrary_names(name):
    first = PwshScriptBuilder(cmdlet="Get-VM")
    first.parameter(name="Name", value=name)
    second = PwshScriptBuilder(cmdlet="Get-VM")
    second.parameter(name="Name", value=name)
    assert first.render() == second.render()
    # Rendered command remains a single statement (no bare newline).
    assert "\n" not in first.render()
    return
