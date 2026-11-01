# AGENTS.md

## Project purpose

This repository is a small laboratory for AI-assisted mathematical and numerical research.
The initial benchmark is a standard one-dimensional Poisson boundary-value problem.
The goal is not to optimize performance, but to build a reliable workflow in which Codex can implement, test, repair, and document mathematical software while numerical and formal verification remain explicit and reproducible.

## Source of truth

- Read `BENCHMARK.md` before changing benchmark code or formal statements.
- Do not silently change the mathematical problem, sign convention, grid convention, boundary conditions, or manufactured solutions.
- If a requested change conflicts with `BENCHMARK.md`, stop and report the conflict instead of guessing.

## Verification layers

This project uses two distinct verification layers:

1. Numerical/software verification with Python and `pytest`.
2. Formal verification with Lean 4 and mathlib.

A passing numerical test is evidence, not a mathematical proof.
A passing Lean proof verifies the formal statement encoded in Lean; it does not by itself prove that the formal statement matches the intended informal mathematics.

## Python rules

- Target Python 3.12 as pinned by the repository.
- Use NumPy and SciPy only when needed; keep dependencies minimal.
- Use `pytest` for automated tests.
- Prefer small, explicit, readable numerical implementations over premature abstraction or optimization.
- Put implementation code under `src/` and tests under `tests/`.
- After modifying Python code, run:
  - `uv run pytest`
  - `uv run ruff check .`

## Lean rules

- Use Lean 4 and the repository's pinned mathlib version.
- Put project theorems under `AIMathLab/` and expose modules through `AIMathLab.lean` when appropriate.
- Prefer transparent statements that closely mirror the mathematics in `BENCHMARK.md`.
- Avoid proving a weaker or differently quantified theorem merely because it is easier.
- After modifying Lean code, run:
  - `lake build`

## Mathematical checks

For numerical PDE work, verify whenever applicable:

- boundary conditions,
- grid spacing and indexing,
- operator sign convention,
- residual of the discrete system,
- comparison with a known exact solution,
- observed convergence order,
- matrix dimensions and basic structural properties.

## Change discipline

- Make small, logically coherent changes.
- Do not modify unrelated files.
- Do not delete failing tests to make the suite pass.
- If a test or theorem appears incorrect, explain why before changing it.
- Report all validation commands actually run and whether they passed.
- If a required command cannot be run, state that explicitly.
