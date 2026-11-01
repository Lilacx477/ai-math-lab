# AI Math Lab

A small research workspace for building and validating AI-assisted mathematical and numerical workflows with Codex, Python, Lean 4, and Git.

The first benchmark is the one-dimensional Poisson equation with homogeneous Dirichlet boundary conditions. The benchmark is intentionally standard: Python provides numerical verification, while Lean provides a separate formal verification layer for a simple exact finite-difference identity.

## Project roles

- **Codex**: repository-aware implementation, testing, repair, and documentation.
- **Python + pytest**: numerical and software verification.
- **Lean 4 + mathlib**: formal verification.
- **Git/GitHub**: reproducibility, review, and change history.
- **Human reviewer**: mathematical specification, interpretation, and final acceptance.

Project-wide agent instructions are in `AGENTS.md`.
The current mathematical specification and acceptance criteria are in `BENCHMARK.md`.

## Python setup

The project uses Python 3.12 and `uv`.

Install/synchronize dependencies with:

```powershell
uv sync
```

Run the Python validation layer with:

```powershell
uv run pytest
uv run ruff check .
```

## Lean setup

The Lean toolchain and mathlib revision are pinned by `lean-toolchain`, `lakefile.toml`, and `lake-manifest.json`.

Fetch mathlib build artifacts if needed:

```powershell
lake exe cache get
```

Run the Lean validation layer with:

```powershell
lake build
```

## Current benchmark

Benchmark 001 studies

\[
-u''(x)=f(x), \qquad x\in(0,1), \qquad u(0)=u(1)=0.
\]

The Python side uses the manufactured solution

\[
u(x)=\sin(\pi x),
\]

and checks the expected second-order convergence of the centered finite-difference method.

The Lean side proves an exact centered-difference identity for

\[
q(x)=\frac{x(1-x)}{2}.
\]

See `BENCHMARK.md` for the precise conventions and Milestone 1 acceptance criteria.

## Milestone 1 implementation

The numerical implementation is in `src/ai_math_lab/poisson.py`.
`uniform_grid(n)` uses `n` interior points and spacing `h = 1/(n+1)`.
`poisson_matrix(n)` constructs the dense interior matrix with diagonal `2/h²`
and adjacent entries `-1/h²`. `solve_poisson(n)` solves the sine manufactured
problem and returns `(x, u)`, both of length `n+2`, including the endpoints
and their prescribed zero solution values. The interior solution is `u[1:-1]`.

Run the numerical tests and lint check from the repository root:

```powershell
uv run pytest
uv run ruff check .
```

The tests in `tests/test_poisson.py` check the matrix, grid, boundary values,
manufactured solution, scaled residual, and maximum interior error. Refinement
uses `n = 15, 31, 63, 127`, so each step halves `h`. The observed orders must
be within `0.05` of two, and errors must strictly decrease. Pytest is configured
to import the implementation from `src/`.

The formal benchmark is `AIMathLab.quadratic_centered_difference` in
`AIMathLab/Poisson.lean`, exposed through `AIMathLab.lean`. It proves the exact
negative centered-difference identity over all real `x` and all real `h ≠ 0`,
without `sorry`. Check it with the pinned Lean toolchain and mathlib:

```powershell
lake build
```

The numerical checks provide evidence of second-order convergence. The Lean
theorem verifies the separate quadratic algebraic identity; it is not a formal
proof of convergence of the Python solver.
