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
The mathematical specifications and acceptance criteria are in `BENCHMARK.md`
(Poisson) and `BENCHMARK-002.md` (heat equation).

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

## Benchmark 002: heat equation with FTCS

`src/ai_math_lab/heat.py` solves `u_t = u_xx` with zero Dirichlet boundaries.
It reuses `uniform_grid(n)` with `h = 1/(n+1)`. `ftcs_step(u, mu)` applies
the weights `(mu, 1-2*mu, mu)` to full states, keeping both endpoints exactly
zero and leaving the input unchanged. Nonzero input boundary values are rejected.
The step permits `mu > 1/2` for the specified instability experiment.

`solve_heat(n, T, mu_target=0.4, initial_state=None)` uses the sine initial
condition by default, or accepts a full state of length `n+2`. Its stable target
must satisfy `0 < mu_target <= 1/2`. For positive `T`, it chooses
`steps = ceil(T/(mu_target*h²))`, then `dt = T/steps`, adding a step if needed
to keep the effective `mu = dt/h² <= mu_target` despite roundoff. Thus the
uniform time grid reaches `T` without accumulated time rounding. The returned
`HeatSolution` provides `x`, `u`, `time`, `dt`, `steps`, and effective `mu`.
At `T=0`, it returns the initial state with zero steps.

The tests compare against `exp(-pi²*T)*sin(pi*x)` at `T=0.01`. Refinement with
`n = 15, 31, 63` and target `mu=0.4` must give decreasing maximum interior errors
and orders above `1.8` and within `0.2` of two. The controlled unstable test
uses the specified highest-frequency sine mode at `n=63`, `mu=0.6`, and checks
its analytic amplification factor.

`AIMathLab/Heat.lean` formalizes the local update over the reals and proves
weight nonnegativity, weight sum, upper and lower bounds, and interval
preservation for `0 <= mu <= 1/2`, without `sorry`. Python cross-validation
probes the production weights and checks the same interval-preservation property.
These tests connect the implementation to the local formal mechanism; they do
not constitute a formal proof of the full numerical solver or its convergence.

Run Benchmark 002 tests alone with `uv run pytest tests/test_heat.py`.
Run the complete validation from the repository root:

```powershell
uv run pytest
uv run ruff check .
lake build
```
