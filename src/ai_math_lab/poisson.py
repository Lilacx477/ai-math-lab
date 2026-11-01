"""Centered differences for the sine benchmark in BENCHMARK.md."""

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def _validate_n(n: int) -> None:
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)):
        raise TypeError("n must be an integer number of interior points")
    if n < 1:
        raise ValueError("n must be at least 1")


def uniform_grid(n: int) -> FloatArray:
    """Return x_i = i/(n+1), including both endpoints, for n interior points."""
    _validate_n(n)
    return np.linspace(0.0, 1.0, n + 2)


def poisson_matrix(n: int) -> FloatArray:
    """Return the n by n matrix for -u'', with diagonal 2/h^2 and off-diagonal -1/h^2."""
    _validate_n(n)
    h = 1.0 / (n + 1)
    matrix = np.diag(np.full(n, 2.0))
    matrix -= np.diag(np.ones(n - 1), k=1)
    matrix -= np.diag(np.ones(n - 1), k=-1)
    return matrix / h**2


def exact_solution(x: FloatArray) -> FloatArray:
    """Evaluate u(x) = sin(pi*x) on an array of grid points."""
    return np.sin(np.pi * x)


def forcing(x: FloatArray) -> FloatArray:
    """Evaluate f(x) = pi^2*sin(pi*x), so that -u'' = f."""
    return np.pi**2 * np.sin(np.pi * x)


def solve_poisson(n: int) -> tuple[FloatArray, FloatArray]:
    """Solve the sine benchmark and return the full grid and solution.

    Both arrays have length n+2. The first and last solution entries are the
    prescribed zero boundary values; entries 1 through n solve A_h u_h = f_h.
    A dense solve keeps this small benchmark explicit.
    """
    x = uniform_grid(n)
    u = np.zeros_like(x)
    u[1:-1] = np.linalg.solve(poisson_matrix(n), forcing(x[1:-1]))
    return x, u
