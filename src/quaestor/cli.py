"""The ``quaestor`` console script.

Phase 0 ships a stub so that the entry point declared in ``pyproject.toml`` is wired and testable
from the first commit: it prints the version and exits zero. The commands of spec section 3.14
(``validate``, ``tool``, ``study``, ``verifier-eval``, ``corpus``, ``mcp``) arrive in Phase 9, at
which point this module grows an argument parser. Until then there is deliberately no parser at
all, so that no half-built flag can be mistaken for a supported one.
"""

from __future__ import annotations

from collections.abc import Sequence

from . import __version__


def main(argv: Sequence[str] | None = None) -> int:
    """Print the Quaestor version and return the process exit code.

    Args:
        argv: Command-line arguments, excluding the program name. Accepted and ignored by the
            Phase 0 stub; the signature is fixed now so that tests can pass an explicit argument
            list once a parser exists, rather than mutating ``sys.argv``.

    Returns:
        ``0``. The console-script wrapper generated from ``[project.scripts]`` passes this value
        to :func:`sys.exit`.
    """
    del argv  # No flags are supported yet; see the module docstring.
    print(f"quaestor {__version__}")
    return 0
