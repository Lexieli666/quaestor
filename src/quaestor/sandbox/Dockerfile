# The containerised path for `run_model`, documented and not used by any test.
#
# `quaestor.sandbox.run_model` caps a subject's wall clock, caps its address space where the
# platform honours the limit, scrubs its environment to four variables and declares
# QUAESTOR_NO_NETWORK=1. What it cannot do from inside Python is *enforce* the absence of a
# network: that needs the operating system. This image is where the guarantee becomes real --
# `docker run --network none` is the whole of it -- and it is written down here so that the
# limitation of the in-process path is visible next to the code that has it (spec section 3.6).
#
# Nothing in `pytest` builds or runs this file. CI has no Docker step, and spec section 1 names
# Docker a non-requirement for v0.1.
#
#   docker build -f src/quaestor/sandbox/Dockerfile -t quaestor-subject .
#   docker run --rm --network none \
#     --memory 4g --memory-swap 4g --cpus 2 --pids-limit 64 \
#     --read-only --tmpfs /tmp:rw,size=256m \
#     -v "$PWD/subjects/credit_default/code:/subject/code:ro" \
#     -v "$PWD/out:/out:rw" \
#     quaestor-subject python -m code.run --out /out --synthetic 5000
#
# The three caps above are the container-level statements of the same three limits the in-process
# runner makes: `--memory` is `runtime.max_memory_mb` and is enforced by the kernel rather than by
# RLIMIT_AS, so it holds on every host; `--network none` is what QUAESTOR_NO_NETWORK only asks
# for; `--read-only` plus a single writable `/out` is what makes "the subject wrote an unexpected
# file" a statement about one directory. The wall-clock cap stays with the caller, which is the
# one of the four Docker does not express: `run_model` still kills the process group.

FROM python:3.12-slim

# The subject's dependencies, which are exactly the three scientific libraries a subject may
# import (spec section 4): no `quaestor`, so a subject cannot import the validator that is
# grading it, and no build toolchain in the final image.
RUN pip install --no-cache-dir "numpy" "pandas" "scikit-learn>=1.4"

# A non-root user with no home to write to but the one the runner passes as HOME.
RUN useradd --create-home --shell /usr/sbin/nologin subject
USER subject

WORKDIR /subject
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    QUAESTOR_NO_NETWORK=1

# No ENTRYPOINT: the command is the package's own `entrypoint` from `package.yaml`, which the
# caller passes, exactly as the in-process runner reads it rather than assuming it.
CMD ["python", "-c", "print('pass the package entrypoint as the command; see the header')"]
