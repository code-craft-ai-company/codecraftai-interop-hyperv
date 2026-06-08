=========================================
Code Craft AI Interop - Hyper-V
=========================================

The ``codecraftai-interop-hyperv`` package is the venue-specific client for Microsoft
Hyper-V. The native automation surface for Hyper-V is PowerShell — the ``Hyper-V`` module
cmdlets plus a small set of related modules — invoked remotely over WinRM. To stay aligned
with the suite-wide "one transport per package" rule, this client speaks PowerShell
exclusively, executed through an ``ICommandRunner`` from ``codecraftai-interfaces``;
``RestClientBase`` does not apply.

Highlights
==========

- ``HypervClient`` — the venue client driving Hyper-V PowerShell cmdlets; host capability and node enumeration.
- Switch and disk management — virtual switch management (External / Internal / Private) and virtual disk (VHDX) management.
- VM lifecycle — New/Start/Stop/Restart/Shutdown/Remove, template / sysprep-from-VHDX provisioning, hardware configuration (processors, memory, generation, secure boot), and virtual NIC/disk attach-detach.
- Checkpoints and task handles — checkpoint (snapshot) management, PS-Session-based guest customization, and a typed ``HypervTaskHandle`` driven by stdout markers and exit-code polling.
- Aspects-driven transport — transport is ``ICommandRunner.run(["pwsh", ...])`` over WinRM or SSH; credentials enter as ``HypervWinrmCredential`` from ``codecraftai-credentials``; every behaviour-bearing call accepts ``aspects: AspectsRunner = DEFAULT_HYPERV_ASPECTS``.

Repository Structure
====================

- ``development/`` - Runtime environment scripts.
- ``repository-setup/`` - Repository homing and setup scripts.
- ``source/packages/ccai/interop/hyperv/`` - Package source code.
- ``source/testroots/testbase/ccai/tests/interop/hyperv/`` - TestBase test roots.
- ``specs/`` - Requirements, design, and task documentation (Kiro-style).
- ``userguide/`` - Standards, conventions, and documentation.

Environment Setup
=================

When working in a Codex container:

.. code-block:: bash

   ./development/setup-agent-container

For local development:

.. code-block:: bash

   ./repository-setup/rehome-repository
   ./development/setup-environment

Running Tests
=============

.. code-block:: bash

   source .venv/bin/activate
   PYTHONPATH=source/packages:source/testroots/testbase python -m pytest source/testroots -q

Standards and Conventions
=========================

- Naming conventions: ``userguide/10-02-naming-conventions.rst``
- Code organization: ``userguide/10-01-code-organization.rst``
- Coding standards: ``userguide/10-00-coding-standards.rst``

Additional Resources
====================

- User guide entry point: ``userguide/userguide.rst``
