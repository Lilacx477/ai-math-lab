# AGENTS.md

## Project purpose

This repository is a small laboratory for AI-assisted mathematical and numerical research.
It contains a sequence of standard numerical-analysis benchmarks used to validate a workflow in which Codex can implement, test, repair, and document mathematical software while numerical and formal verification remain explicit and reproducible.

The goal is not premature performance optimization. Mathematical correctness, transparent conventions, and reproducibility come first.

## Source of truth

- Before changing benchmark code or formal statements, read the benchmark specification relevant to the task.
- `BENCHMARK.md` specifies Benchmark 001 (1D Poisson equation).
- `BENCHMARK-002.md` specifies Benchmark 002 (1D heat equation with FTCS).
- Do not silently change the mathematical problem, sign convention, grid convention, boundary conditions, manufactured solutions, stability assumptions, or acceptance criteria.
- If a requested change conflicts with the relevant benchmark specification, stop and report the conflict instead of guessing.

## Verification layers

This project uses two distinct verification layers:

1. Numerical/software verification with Python and `pytest`.
2. Formal verification with Lean 4 and mathlib.

A passing numerical test is evidence, not a mathematical proof.
A passing Lean proof verifies the formal statement encoded in Lean; it does not by itself prove that the formal statement matches the intended informal mathematics.

When the same mathematical mechanism appears in both Python and Lean, add cross-validation when practical so that the production numerical implementation can be checked against the formal specification.

## Python rules

- Target Python 3.12 as pinned by the repository.
- Use NumPy and SciPy only when needed; keep dependencies minimal.
- Use `pytest` for automated tests.
- Prefer small, explicit, readable numerical implementations over premature abstraction or optimization.
- Put implementation code under `src/` and tests under `tests/`.
- Reuse existing conventions and production operators rather than duplicating test-only implementations.
- After modifying Python code, run:
  - `uv run pytest`
  - `uv run ruff check .`

## Lean rules

- Use Lean 4 and the repository's pinned mathlib version.
- Put project theorems under `AIMathLab/` and expose modules through `AIMathLab.lean` when appropriate.
- Prefer transparent statements that closely mirror the mathematics in the relevant benchmark specification.
- Avoid proving a weaker or differently quantified theorem merely because it is easier.
- Do not use `sorry` in benchmark acceptance theorems.
- After modifying Lean code, run:
  - `lake build`

## Mathematical checks

For numerical PDE work, verify whenever applicable:

- boundary conditions,
- grid spacing and indexing,
- operator sign convention,
- time-step convention,
- residual or update equation,
- comparison with a known exact solution,
- observed convergence order,
- stability conditions and controlled unstable examples,
- matrix dimensions and basic structural properties.

## Change discipline

- Make small, logically coherent changes.
- Do not modify unrelated files.
- Do not delete or weaken failing tests merely to make the suite pass.
- If a test or theorem appears incorrect, explain why before changing it.
- Report all validation commands actually run and whether they passed.
- If a required command cannot be run, state that explicitly.
