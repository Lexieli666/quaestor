"""``run_model``: executing a subject in a capped subprocess, and the spec 3.3 contract it writes.

Spec section 3.6, implemented in Phase 3. A subject is never imported into the validator's
process: it runs in a subprocess with a scrubbed environment, a wall-clock cap, a memory cap where
the platform honours one and networking declared off, and every file of the standard artifact
contract is checked for presence and schema afterwards. The ``Dockerfile`` beside this module
documents the containerised path, where the network guarantee is real; no test uses it.
"""

from __future__ import annotations

from .contract import ContractFile, features_artifact, read_contract, required_files
from .runner import MemoryCap, RunResult, build_argv, memory_cap_policy, run_model

__all__ = [
    "ContractFile",
    "MemoryCap",
    "RunResult",
    "build_argv",
    "features_artifact",
    "memory_cap_policy",
    "read_contract",
    "required_files",
    "run_model",
]
