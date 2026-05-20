# Requirements

## Introduction

The `hyperv-client` feature provides a typed Python client for Microsoft
Hyper-V driven through PowerShell cmdlets executed via an `ICommandRunner`
(typically `SSHCommandRunner` or a WinRM-backed equivalent). Because
Hyper-V has no REST API, this client does **not** use `RestClientBase`.
The "one transport per package" rule still applies.

The client covers host info, virtual switches, VHDX disks, VM lifecycle
and hardware configuration, virtual NIC and disk attach-detach,
checkpoints, and long-running op tracking. Every behaviour-bearing
method accepts `aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS`.

---

## Requirements

### Requirement 1: Construct With Credential and Runner

#### Acceptance Criteria

1. WHEN the client is constructed with a `HypervWinrmCredential` and
   an `ICommandRunner` THE SYSTEM SHALL store both as immutable state
   reachable from every operation.
2. WHEN the credential is missing endpoint, username, or auth material
   THE SYSTEM SHALL raise `ConfigurationError`.

### Requirement 2: Safe PowerShell Argument Composition

#### Acceptance Criteria

1. WHEN composing a PowerShell command with caller-supplied identifiers
   or paths THE SYSTEM SHALL quote each substitution using single-quote
   PowerShell rules with doubled embedded quotes.
2. WHEN any substitution contains a newline or null byte THE SYSTEM
   SHALL raise `SemanticError`.
3. THE SYSTEM SHALL render deterministically: the same inputs produce
   the same command line.

### Requirement 3: Query Host and Capability Information

#### Acceptance Criteria

1. WHEN the caller invokes `host_info(aspects)` THE SYSTEM SHALL invoke
   `Get-VMHost | ConvertTo-Json` (and related cmdlets), parse the JSON,
   and return a `HypervHostInfo` record.

### Requirement 4: Manage Virtual Switches

#### Acceptance Criteria

1. WHEN the caller invokes `list_switches(aspects)` THE SYSTEM SHALL
   invoke `Get-VMSwitch | ConvertTo-Json` and return `HypervVirtualSwitch`
   records.
2. WHEN the caller invokes `new_switch(spec, aspects)` THE SYSTEM SHALL
   invoke `New-VMSwitch ...` with safe argument substitution. WHEN a
   switch with the same name already exists THE SYSTEM SHALL return the
   existing record (idempotent).
3. WHEN the caller invokes `remove_switch(name, aspects)` against an
   unknown switch THE SYSTEM SHALL succeed as a no-op.

### Requirement 5: Manage VHDX Disks

#### Acceptance Criteria

1. WHEN the caller invokes `new_vhdx(path, size_bytes, dynamic, aspects)`
   THE SYSTEM SHALL invoke `New-VHD` with quoted path and return a
   `HypervVhdxInfo` record. An existing VHDX at the same path matching
   the requested size and dynamic flag SHALL be returned (idempotent).
2. WHEN the caller invokes `resize_vhdx(path, size_bytes, aspects)`
   THE SYSTEM SHALL invoke `Resize-VHD`.
3. WHEN the caller invokes `delete_vhdx(path, aspects)` against an
   absent path THE SYSTEM SHALL succeed as a no-op.

### Requirement 6: Manage VM Lifecycle

#### Acceptance Criteria

1. WHEN the caller invokes `new_vm(spec, aspects)` THE SYSTEM SHALL
   invoke `New-VM` with safe quoting and return a `HypervVm` record.
   A VM of the same name SHALL be returned (idempotent create).
2. WHEN the caller invokes `start_vm(name, aspects)`,
   `stop_vm(name, aspects)`, `restart_vm(name, aspects)`,
   `shutdown_vm(name, aspects)` (graceful), or
   `remove_vm(name, aspects)` THE SYSTEM SHALL invoke the appropriate
   cmdlet. `remove_vm` against an absent name SHALL be a no-op.
3. WHEN the caller invokes `get_vm(name, aspects)` and
   `list_vms(aspects)` THE SYSTEM SHALL return `HypervVm` records.

### Requirement 7: Configure VM Hardware

#### Acceptance Criteria

1. WHEN the caller invokes `set_vm_processor(name, count, aspects)`,
   `set_vm_memory(name, startup_bytes, dynamic, min_bytes, max_bytes, aspects)`,
   `set_vm_secure_boot(name, enabled, aspects)`, or
   `set_vm_generation(name, generation, aspects)` THE SYSTEM SHALL
   invoke the corresponding `Set-VM*` cmdlet.
2. WHEN the current value already matches the desired value THE SYSTEM
   SHALL be a no-op (idempotent).

### Requirement 8: Attach and Detach Virtual NICs and Disks

#### Acceptance Criteria

1. WHEN the caller invokes `add_vm_network_adapter(name, switch_name, mac, aspects)`,
   `remove_vm_network_adapter(name, mac, aspects)`,
   `add_vm_hard_disk(name, vhdx_path, controller_type, aspects)`, or
   `remove_vm_hard_disk(name, controller_type, controller_number, controller_location, aspects)`
   THE SYSTEM SHALL invoke the corresponding cmdlet with idempotent
   behaviour.

### Requirement 9: Manage Checkpoints

#### Acceptance Criteria

1. WHEN the caller invokes `checkpoint_vm(name, snapshot_name, aspects)`,
   `list_checkpoints(name, aspects)`,
   `restore_checkpoint(name, snapshot_name, aspects)`, or
   `remove_checkpoint(name, snapshot_name, aspects)` THE SYSTEM SHALL
   invoke `Checkpoint-VM`/`Get-VMSnapshot`/`Restore-VMSnapshot`/`Remove-VMSnapshot`
   with idempotent remove.

### Requirement 10: Wait For VM State

#### Acceptance Criteria

1. WHEN the caller invokes `wait_for_state(name, desired_state, aspects)`
   THE SYSTEM SHALL poll `get_vm` per aspects.
2. WHEN the aspects timeout elapses THE SYSTEM SHALL raise `TimeoutError`.

### Requirement 11: Long-Running Op Task Handles

#### Acceptance Criteria

1. WHEN a long-running cmdlet is dispatched in the background (via
   `Start-Job` or a job-id-returning cmdlet) THE SYSTEM SHALL return a
   `HypervTaskHandle` implementing `ITaskHandle`.
2. WHEN `handle.wait(aspects)` is invoked THE SYSTEM SHALL poll
   `Get-Job <id>` per aspects and SHALL return the final
   `HypervTaskResult`.
3. WHEN the aspects timeout elapses THE SYSTEM SHALL raise
   `TimeoutError`.

### Requirement 12: Aspects on Every Behaviour-Bearing Call

#### Acceptance Criteria

1. THE SYSTEM SHALL accept `aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS`
   on every operation; no behaviour-modifying decorators.
