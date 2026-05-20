# Design

## Overview

`HypervClient` is a CLI-shaped client that drives the Hyper-V cmdlet
surface (`Hyper-V`, `NetAdapter`, `Storage`) through an `ICommandRunner`.
Because Hyper-V has no REST API, this client does NOT use
`RestClientBase`. The transport is PowerShell invocation, optionally
remoted via WinRM or SSH-for-Windows by the chosen runner.

A central concern is **safe PowerShell argument composition**. The
`pwshquote` helper performs single-quoted, double-the-quotes escaping
and rejects newline/null bytes to eliminate command injection. JSON
output (`ConvertTo-Json -Compress`) is the canonical wire shape from
the cmdlets back into Python typed records.

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│  automojo-provisioning / venues / hyperv               │
└──────────┬─────────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────┐
│  HypervClient                                          │
│   AspectsRunner on every op                            │
│   pwshquote safe argument composer                     │
│   JSON-out parsers for typed records                   │
│   API groups: host, switches, vhdx, vms, hardware,     │
│     adapters, checkpoints, jobs                        │
└──────────┬─────────────────────────────────────────────┘
           │ ICommandRunner.run(["pwsh","-NoProfile","-Command", ...])
           ▼
┌────────────────────────────────────────────────────────┐
│  Hyper-V host (local pwsh, WinRM, or OpenSSH)          │
└────────────────────────────────────────────────────────┘
```

---

## Data Model

`model/`: `hypervhostinfo.py`, `hypervvirtualswitch.py`,
`hypervvhdxinfo.py`, `hypervvm.py`, `hypervadapter.py`,
`hypervcheckpoint.py`, `hypervjobinfo.py`, `hyperv taskhandle.py`.

`specs/`: `hypervswitchspec.py`, `hypervvhdxspec.py`,
`hypervvmcreatespec.py`, `hypervadapterspec.py`.

Exceptions: `HypervCmdletError`, `HypervTaskFailedError`.

---

## Module Layout

```
source/packages/automojo/interop/hyperv/
├── hypervclient.py
├── aspectshyperv.py             # AspectsRunner + DEFAULT_HYPERV_ASPECTS
├── pwsh/
│   ├── pwshquote.py             # safe arg composer
│   ├── pwshscriptbuilder.py
│   └── pwshjsonparser.py
├── apigroups/{hostgroup, switchesgroup, vhdxgroup, vmsgroup,
│              hardwaregroup, adaptersgroup, checkpointsgroup,
│              jobsgroup}.py
├── model/
├── specs/
└── exceptions/
```

---

## See Also

- `automojo-interfaces/specs/icommandrunner/` — the runner contract.
- `automojo-provisioning/specs/venue-hyperv/`
- Cross-cutting usability commitment §8.1 — Hyper-V is the CLI-shaped sibling to libvirt/Xen native examples.

---

## Testing Strategy

Example-based tests use a mock `ICommandRunner` that returns canned
cmdlet JSON output. Tests cover safe argument composition, idempotent
switch/VHDX/VM/checkpoint operations, hardware-set short-circuit when
already matching, and job-based async waiter happy path.

Property-based tests (hypothesis) are **required** for:
1. **PowerShell argument quoting safety.** For any input string drawn
   from a wide character set (including `'`, `"`, `;`, `|`, `$`,
   backtick), the produced command line passes a PowerShell tokenizer
   round-trip check and yields the original string unchanged on the
   other side; newline/null inputs raise `SemanticError`.
2. **Idempotent retry semantics** within and beyond budget.
3. **`HypervTaskHandle.wait`** terminal-state correctness across
   arbitrary monotonic mock `Get-Job` status streams.
4. **`wait_for_state` waiter** terminal correctness.

Live-Hyper-V integration tests run under `multihost` against a sandbox
host gated by an env var.
