"""Red Line CLI wrappers.

This file keeps the local ``scripts`` directory a regular package so explicit
imports of these thin wrappers (``from scripts import build_canary``) resolve
to this project rather than to a same-named package from a sibling or host
checkout on ``sys.path``. Without it the directory is only a namespace
portion, and Python's path finder keeps scanning until it meets a regular
``scripts`` package elsewhere — which is what happens when the suite runs
under a render host that ships its own ``scripts/__init__.py``.

Every script here is an orchestrator: it calls the package, prints what came
back, and chooses an exit code from a value the package computed. No decision
rule lives in this directory.
"""
