# Benchmark 002: 1D heat equation with explicit Euler

## Purpose

This benchmark extends the repository from a static elliptic problem to a time-dependent PDE.
The main new concept is **stability**.

The benchmark should exercise the complete workflow:

- mathematical specification,
- Python implementation,
- numerical convergence tests,
- stable and unstable regimes,
- Lean formalization of the local stability mechanism,
- Python–Lean cross-validation,
- local validation and GitHub CI.

The mathematics is deliberately classical and well understood so that failures can be attributed to the implementation or workflow rather than to an open problem.

## Continuous problem

Consider the one-dimensional heat equation

\[
\partial_t u(x,t)=\partial_{xx}u(x,t),
\qquad 0<x<1,\quad t>0,
\]

with homogeneous Dirichlet boundary conditions

\[
u(0,t)=u(1,t)=0.
\]

For the accuracy benchmark, use the initial condition

\[
u(x,0)=\sin(\pi x).
\]

The exact solution is

\[
u(x,t)=e^{-\pi^2 t}\sin(\pi x).
\]

## Spatial grid and time step

Use `n` interior grid points

\[
x_i=ih,
\qquad i=0,1,\ldots,n+1,
\qquad h=\frac{1}{n+1}.
\]

Let

\[
t_m=m\,\Delta t
\]

and define

\[
\mu=\frac{\Delta t}{h^2}.
\]

The first and last entries are boundary values and remain zero at every time step.

## FTCS discretization

Use centered differences in space and forward Euler in time:

\[
\frac{u_i^{m+1}-u_i^m}{\Delta t}
=
\frac{u_{i-1}^m-2u_i^m+u_{i+1}^m}{h^2}.
\]

Equivalently,

\[
u_i^{m+1}
=
\mu u_{i-1}^m+(1-2\mu)u_i^m+\mu u_{i+1}^m.
\]

Do not silently change this sign convention, grid convention, or boundary treatment.

## Stability mechanism

For

\[
0\le \mu\le \frac12,
\]

the three coefficients

\[
\mu,\qquad 1-2\mu,\qquad \mu
\]

are nonnegative and sum to one.
Therefore each updated interior value is a convex combination of its three neighboring old values.
This gives a one-step discrete maximum principle and, consequently, an \(\ell^\infty\) non-expansiveness property for the homogeneous Dirichlet problem.

This convex-combination argument is the first formal stability statement for Lean.

## Python implementation

Create the heat-equation implementation under

`src/ai_math_lab/heat.py`.

Keep the implementation explicit and readable. Reuse the repository's existing grid convention where practical instead of creating an incompatible second convention.

At minimum, provide functionality for:

1. constructing the grid,
2. performing one FTCS step,
3. evolving an initial state to a requested final time,
4. evaluating the exact sine solution for comparison.

For a requested final time `T`, choose the number of steps so that the actual time step lands exactly at `T`. For convergence experiments, start from a target stable value such as `mu_target = 0.4`, choose enough integer time steps to reach `T`, and use the resulting effective

\[
\mu_{\mathrm{eff}}=\frac{\Delta t}{h^2}\le \mu_{\mathrm{target}}.
\]

Document the convention used by the solver.

## Required Python tests

Create tests under

`tests/test_heat.py`.

At minimum, automated tests should verify all of the following.

### 1. One-step formula

For a small deterministic state, check directly that the implementation agrees with

\[
u_i^{m+1}
=
\mu u_{i-1}^m+(1-2\mu)u_i^m+\mu u_{i+1}^m.
\]

### 2. Boundary conditions

The first and last entries must remain exactly zero after every step and after a full evolution.

### 3. Stable maximum-principle behavior

For several values with

\[
0\le\mu\le\frac12,
\]

use deterministic initial vectors and check that one FTCS step does not increase the maximum absolute value:

\[
\|u^{m+1}\|_\infty\le\|u^m\|_\infty
\]

up to a small floating-point tolerance.

This test should exercise the same convex-combination mechanism formalized in Lean.

### 4. Exact sine solution

For a fixed final time such as

\[
T=0.01,
\]

compare the numerical solution with

\[
e^{-\pi^2T}\sin(\pi x).
\]

### 5. Convergence under refinement

Use a stable target value such as

\[
\mu_{\mathrm{target}}=0.4
\]

and refine grids with interior counts such as

`[15, 31, 63]`.

Because \(\Delta t=O(h^2)\), the first-order temporal error and second-order spatial error are both \(O(h^2)\) along this refinement path. The observed error should therefore approach second order in \(h\).

Use a documented tolerance; an observed order above approximately `1.8` on the selected grids is an acceptable benchmark criterion if supported by the actual numerical results.

### 6. Explicit unstable example

Do **not** encode the incorrect statement that every finite-grid computation with \(\mu>1/2\) must immediately grow for every initial condition.

Instead use a specified high-frequency discrete eigenmode. For `n = 63`, let

\[
v_i=\sin\left(\frac{n\pi i}{n+1}\right),
\qquad i=1,\ldots,n.
\]

For one FTCS step this mode has amplification factor

\[
g_n(\mu)
=
1-4\mu\sin^2\left(\frac{n\pi}{2(n+1)}\right).
\]

At \(\mu=0.6\), verify numerically that

\[
|g_n(0.6)|>1
\]

and that one numerical step amplifies the norm of this mode accordingly.

This is the benchmark's controlled unstable case.

## Lean formal benchmark

Create the Lean formalization under

`AIMathLab/Heat.lean`

and expose it from `AIMathLab.lean`.

Work over `ℝ`.

### Required formal statements

At minimum formalize the local FTCS update

\[
F_\mu(a,b,c)
=
\mu a+(1-2\mu)b+\mu c.
\]

Then prove statements expressing the stability mechanism for

\[
0\le\mu\le\frac12.
\]

The formalization should include:

1. nonnegativity of the three weights,
2. the identity that the three weights sum to one,
3. a one-step upper-bound theorem: if `a ≤ M`, `b ≤ M`, and `c ≤ M`, then `F_mu(a,b,c) ≤ M`,
4. a corresponding lower-bound theorem, or an equivalent absolute-value / interval preservation theorem.

The statements must use the same FTCS coefficients and sign convention as the Python implementation.

Do not use `sorry`.

## Python–Lean cross-validation

Include at least one Python test whose mathematical content directly mirrors the Lean stability theorem.

For example, for deterministic triples or grid states and stable \(\mu\), verify the one-step interval or maximum-principle property using the production FTCS implementation rather than a duplicated test-only implementation.

The purpose is not to make Python prove the theorem. The purpose is to check that the production numerical implementation realizes the same mathematical update that Lean formalizes.

## Milestone 3 acceptance criteria

Benchmark 002 is complete only when all of the following hold:

- `src/ai_math_lab/heat.py` exists.
- `tests/test_heat.py` exists.
- `AIMathLab/Heat.lean` exists and is imported by `AIMathLab.lean`.
- The exact sine solution is tested at positive time.
- Stable maximum-principle behavior is tested.
- A controlled high-frequency unstable example is tested for `mu = 0.6`.
- A grid-refinement study demonstrates approximately second-order convergence along the specified stable refinement path.
- The Python implementation and Lean theorem use the same FTCS coefficients.
- `uv run pytest` passes.
- `uv run ruff check .` passes.
- `lake build` passes.
- No failing test is weakened or removed merely to obtain a passing result.
- No Lean theorem is weakened merely to make the proof easier.
- README is updated with concise instructions for running Benchmark 002 validation.
