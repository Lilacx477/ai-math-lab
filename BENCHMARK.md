# Benchmark 001: 1D Poisson equation

## Purpose

This benchmark validates the end-to-end workflow of the repository: specification, Python implementation, numerical testing, Lean formalization, automated repair, and Git review.

The mathematics is deliberately standard and well understood so that failures can be attributed to the implementation or workflow rather than to an open mathematical question.

## Continuous problem

Consider

\[
-u''(x)=f(x), \qquad x\in(0,1),
\]

with homogeneous Dirichlet boundary conditions

\[
u(0)=u(1)=0.
\]

## Discretization

Let

\[
x_i=ih, \qquad i=0,1,\dots,N+1,
\]

with

\[
h=\frac{1}{N+1}.
\]

The interior unknowns are \(u_i\approx u(x_i)\), \(i=1,\dots,N\).
Use the centered second difference

\[
-u''(x_i)\approx
\frac{-u_{i-1}+2u_i-u_{i+1}}{h^2}.
\]

Thus the discrete system is

\[
A_h u_h=f_h,
\]

where \(A_h\) is the standard tridiagonal matrix

\[
A_h=\frac{1}{h^2}
\begin{pmatrix}
2 & -1 \\
-1 & 2 & -1 \\
& \ddots & \ddots & \ddots \\
&& -1 & 2
\end{pmatrix}.
\]

## Python manufactured solution

Use

\[
u(x)=\sin(\pi x),
\]

so that

\[
f(x)=\pi^2\sin(\pi x).
\]

The numerical implementation should solve the discrete system and compare the interior numerical solution with the exact values at the grid points.

### Required numerical checks

At minimum, automated tests should verify:

1. the discrete matrix has shape \(N\times N\),
2. the matrix has the expected tridiagonal entries,
3. the returned grid respects the boundary interval and spacing convention,
4. the discrete residual \(\|A_hu_h-f_h\|\) is small relative to the problem scale,
5. the error decreases under grid refinement,
6. the observed convergence order approaches 2 for the sine manufactured solution.

For errors \(E_h\) and \(E_{h/2}\), estimate the order by

\[
p=\frac{\log(E_h/E_{h/2})}{\log 2}.
\]

A test may use a reasonable tolerance such as requiring an observed order above 1.8 on sufficiently fine grids. The exact tolerance should be documented in the test.

## Lean benchmark theorem

For the first formal benchmark, use the quadratic manufactured solution

\[
q(x)=\frac{x(1-x)}{2}.
\]

For \(h\neq 0\), prove the exact centered-difference identity

\[
\frac{-q(x-h)+2q(x)-q(x+h)}{h^2}=1.
\]

This theorem is intentionally algebraic. It checks that the Lean toolchain, mathlib, project layout, and Codex repair loop work before attempting a full formal convergence theorem.

### Lean acceptance criteria

- The theorem is stated over `ℝ`.
- The nonzero-spacing assumption is explicit.
- The statement matches the sign convention used by the Python discrete operator.
- `lake build` succeeds without `sorry` in the benchmark theorem.

## Milestone 1 acceptance criteria

Milestone 1 is complete only when all of the following hold:

- Python implementation exists under `src/`.
- Python tests exist under `tests/`.
- `uv run pytest` passes.
- `uv run ruff check .` passes.
- A Lean theorem for the quadratic centered-difference identity exists under `AIMathLab/`.
- `lake build` passes.
- No validation requirement is disabled merely to obtain a passing result.
- README documents how to run both validation layers.
