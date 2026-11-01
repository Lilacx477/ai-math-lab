"""Numerical acceptance checks for Benchmark 001."""

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from ai_math_lab.poisson import (
    exact_solution,
    forcing,
    poisson_matrix,
    solve_poisson,
    uniform_grid,
)


@pytest.mark.parametrize("n", [1, 2, 7, 31])
def test_matrix_dimensions(n):
    assert poisson_matrix(n).shape == (n, n)


def test_matrix_entries_and_sign_convention():
    # Three interior points give h=1/4, hence 1/h^2=16.
    expected = np.array([[32.0, -16.0, 0.0], [-16.0, 32.0, -16.0], [0.0, -16.0, 32.0]])
    assert_array_equal(poisson_matrix(3), expected)
    assert_array_equal(poisson_matrix(1), [[8.0]])


def test_matrix_is_symmetric_positive_definite():
    matrix = poisson_matrix(7)
    assert_array_equal(matrix, matrix.T)
    assert np.all(np.linalg.eigvalsh(matrix) > 0.0)


@pytest.mark.parametrize("n", [1, 2, 7, 31])
def test_returned_grid_and_boundary_conditions(n):
    x, u = solve_poisson(n)
    assert x.shape == u.shape == (n + 2,)
    assert x[0] == 0.0
    assert x[-1] == 1.0
    assert np.all((x[1:-1] > 0.0) & (x[1:-1] < 1.0))
    assert_allclose(x, np.arange(n + 2) / (n + 1), rtol=0.0, atol=1e-15)
    assert_allclose(np.diff(x), 1.0 / (n + 1), rtol=0.0, atol=1e-15)
    assert_array_equal(u[[0, -1]], [0.0, 0.0])


def test_manufactured_solution_and_forcing():
    x = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    expected = np.array([0.0, np.sqrt(0.5), 1.0, np.sqrt(0.5), 0.0])
    assert_allclose(exact_solution(x), expected, rtol=0.0, atol=1e-15)
    assert_allclose(forcing(x), np.pi**2 * expected, rtol=0.0, atol=1e-14)


def test_single_interior_point_solution():
    # At x=1/2 the equation is 8*u_1 = pi^2, not the continuous value u=1.
    _, u = solve_poisson(1)
    assert_allclose(u[1], np.pi**2 / 8.0, rtol=1e-14, atol=0.0)


@pytest.mark.parametrize("n", [1, 7, 31, 63])
def test_discrete_residual_relative_to_forcing(n):
    x, u = solve_poisson(n)
    rhs = forcing(x[1:-1])
    residual = poisson_matrix(n) @ u[1:-1] - rhs
    # Allow rounding from the dense solve; the residual must be tiny on the RHS scale.
    assert np.linalg.norm(residual, ord=np.inf) <= 1e-11 * np.linalg.norm(rhs, ord=np.inf)


def test_solution_matches_exact_sine():
    x, u = solve_poisson(31)
    error = np.max(np.abs(u[1:-1] - exact_solution(x[1:-1])))
    assert error < 1e-3


def test_error_decreases_with_second_order_convergence():
    # N -> 2*N+1 halves h exactly. Use the maximum error over interior nodes.
    counts = [15, 31, 63, 127]
    errors = []
    for n in counts:
        x, u = solve_poisson(n)
        errors.append(np.max(np.abs(u[1:-1] - exact_solution(x[1:-1]))))
    errors = np.array(errors)
    assert np.all(errors > 0.0)
    assert np.all(errors[1:] < errors[:-1])
    orders = np.log(errors[:-1] / errors[1:]) / np.log(2.0)
    # On these grids the asymptotic order must be within 0.05 of 2 (hence above 1.8).
    assert_allclose(orders, 2.0, rtol=0.0, atol=0.05)


@pytest.mark.parametrize("builder", [uniform_grid, poisson_matrix, solve_poisson])
@pytest.mark.parametrize("n", [0, -1])
def test_nonpositive_interior_count_is_rejected(builder, n):
    with pytest.raises(ValueError, match="at least 1"):
        builder(n)


@pytest.mark.parametrize("builder", [uniform_grid, poisson_matrix, solve_poisson])
@pytest.mark.parametrize("n", [2.5, True])
def test_noninteger_interior_count_is_rejected(builder, n):
    with pytest.raises(TypeError, match="integer"):
        builder(n)
