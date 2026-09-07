# subjects/msr_prepayment/code/ — the subject itself: the only directory the sandbox copies.
#
# `quaestor.sandbox.run_model` copies this directory into a temporary working tree and runs
# `python -m code.run` with the working directory one level above the copy, so everything the
# subject needs at run time has to live in here. That is why the generating process is
# `code/synthetic.py` and not the subject-root `synthetic.py`, which is a thin re-export for a
# human and for the tests (DECISIONS D-029).
#
# The package is called `code`, which shadows the standard library module of that name for the
# duration of the subprocess. That is what spec section 3.2's `entrypoint: "python -m code.run"`
# asks for; nothing in numpy, pandas or scikit-learn imports the standard library `code`.
"""The msr_prepayment subject: the loan-month panel, the spline hazard and the projection."""
