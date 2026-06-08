# Implementation Plan — Hyper-V Client

## Package Skeleton

- [x] 1. Create `source/packages/ccai/interop/hyperv/` package tree with `pwsh/`, `apigroups/`, `model/`, `specs/`, `exceptions/` subpackages.
- [x] 2. Add `aspectshyperv.py` defining `AspectsRunner` and `DEFAULT_HYPERV_ASPECTS`.

## PowerShell Substrate

- [x] 3. Implement `pwshquote.py` — single-quoted-double-the-quotes escaping with newline/null rejection.
- [x] 4. Implement `pwshscriptbuilder.py` — composes deterministic, single-statement PowerShell commands.
- [x] 5. Implement `pwshjsonparser.py` — parses `ConvertTo-Json -Compress` output into Python records.

## Client Core

- [x] 6. Implement `HypervClient.__init__(runner, credential, config)` and credential validation.
- [x] 7. Implement HTTP/cmdlet error reclassification into `HypervCmdletError`.

## API Groups

- [x] 8. Implement `HostGroup.host_info`.
- [x] 9. Implement `SwitchesGroup.list / new / remove` with idempotency.
- [x] 10. Implement `VhdxGroup.new / resize / delete` with idempotent create/delete.
- [x] 11. Implement `VmsGroup.new / get / list / start / stop / restart / shutdown / remove` with idempotent create/remove.
- [x] 12. Implement `HardwareGroup.set_processor / set_memory / set_secure_boot / set_generation` with no-op-on-match.
- [x] 13. Implement `AdaptersGroup.add_network_adapter / remove_network_adapter / add_hard_disk / remove_hard_disk` with idempotency.
- [x] 14. Implement `CheckpointsGroup.checkpoint / list / restore / remove` with idempotent remove.
- [x] 15. Implement `JobsGroup.get` consumed by `HypervTaskHandle.wait`.

## Waiters

- [x] 16. Implement `wait_for_state(name, desired_state, aspects)`.

## Data Model & Specs

- [x] 17. Implement model dataclasses for host info, virtual switch, VHDX info, VM, adapter, checkpoint, job info.
- [x] 18. Implement spec dataclasses for switch/VHDX/VM-create/adapter.
- [x] 19. Implement `HypervTaskHandle` against `ITaskHandle`.

## Tests — Example-Based

- [x] 20. Safe arg composition tests with representative tricky inputs.
- [x] 21. Idempotent switch/VHDX/VM/checkpoint tests using a mock runner.
- [x] 22. Hardware-set no-op tests.
- [x] 23. Job-based async waiter happy path.
- [x] 24. Cmdlet error reclassification.

## Tests — Property-Based (hypothesis)

- [x] 25. PowerShell quoting round-trip safety over arbitrary strings + newline/null rejection.
- [x] 26. Idempotent-retry equivalence within budget; bubble-through outside.
- [x] 27. `HypervTaskHandle.wait` terminal-state correctness.
- [x] 28. `wait_for_state` terminal correctness.

## Integration

- [ ] 29. Live-Hyper-V smoke-test fixture gated by env var.
