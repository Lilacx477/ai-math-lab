"""Numerical and Python-Lean cross-validation checks for Benchmark 002."""

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

from ai_math_lab.heat import exact_sine_solution, ftcs_step, solve_heat, uniform_grid
from ai_math_lab.poisson import poisson_matrix


def test_one_step_formula_and_input_preservation():
    state = np.array([0.0, 2.0, -1.0, 4.0, 0.0])
    original = state.copy()
    # mu=1/4 gives weights (1/4, 1/2, 1/4) at every interior node.
    expected = np.array([0.0, 0.75, 1.0, 1.75, 0.0])
    assert_array_equal(ftcs_step(state, 0.25), expected)
    assert_array_equal(state, original)


def test_heat_update_has_opposite_sign_to_poisson_operator():
    state = np.array([0.0, 1.0, -2.0, 0.5, 3.0, -0.2, 1.0, -1.0, 0.0])
    n = state.size - 2
    h = 1.0 / (n + 1)
    mu = 0.4
    expected = state[1:-1] - mu * h**2 * (poisson_matrix(n) @ state[1:-1])
    assert_allclose(ftcs_step(state, mu)[1:-1], expected, rtol=0.0, atol=1e-14)


@pytest.mark.parametrize("mu", [0.0, 0.1, 0.5, 0.6])
def test_boundary_values_after_every_step(mu):
    state = np.array([0.0, 1.0, -2.0, 4.0, 0.0])
    for _ in range(12):
        state = ftcs_step(state, mu)
        assert_array_equal(state[[0, -1]], [0.0, 0.0])


@pytest.mark.parametrize("mu", [0.0, 0.1, 0.25, 0.4, 0.5])
@pytest.mark.parametrize(
    "state",
    [
        [0.0, 3.0, -2.0, 1.0, 0.0],
        [0.0, 1.0, 1.0, 1.0, 0.0],
        [0.0, -1.0, -3.0, -2.0, 0.0],
    ],
)
def test_stable_maximum_principle(state, mu):
    updated = ftcs_step(state, mu)
    # A small absolute tolerance allows only floating-point rounding of the convex sum.
    assert np.max(np.abs(updated)) <= np.max(np.abs(state)) + 1e-14


@pytest.mark.parametrize("mu", [0.0, 0.1, 0.25, 0.4, 0.5])
def test_production_weights_match_lean_convex_combination(mu):
    # Probe the central row using basis triples, through the production update.
    weights = []
    for triple in np.eye(3):
        state = np.concatenate(([0.0], triple, [0.0]))
        weights.append(ftcs_step(state, mu)[2])
    weights = np.array(weights)
    assert_allclose(weights, [mu, 1.0 - 2.0 * mu, mu], rtol=0.0, atol=1e-15)
    assert np.all(weights >= 0.0)
    assert_allclose(np.sum(weights), 1.0, rtol=0.0, atol=1e-15)


@pytest.mark.parametrize("mu", [0.0, 0.1, 0.25, 0.4, 0.5])
@pytest.mark.parametrize(
    "triple, lower, upper",
    [
        ((-2.0, 0.5, 3.0), -2.0, 3.0),
        ((1.0, 2.0, 4.0), 1.0, 4.0),
        ((-4.0, -2.0, -1.0), -4.0, -1.0),
        ((2.0, 2.0, 2.0), 2.0, 2.0),
        ((-3.0, -3.0, -3.0), -3.0, -3.0),
    ],
)
def test_local_interval_preservation_matches_lean(triple, lower, upper, mu):
    """Mirror AIMathLab.Heat.ftcs_preserves_interval at the central grid point."""
    # Only the central row sees this triple, so its interval need not contain zero.
    state = np.array([0.0, *triple, 0.0])
    value = ftcs_step(state, mu)[2]
    assert lower - 1e-14 <= value <= upper + 1e-14


@pytest.mark.parametrize("n, expected_steps", [(15, 7), (31, 26), (63, 103)])
def test_time_grid_and_full_evolution_boundary_values(n, expected_steps):
    final_time = 0.01
    result = solve_heat(n, final_time, mu_target=0.4)
    assert_array_equal(result.x, uniform_grid(n))
    assert result.x.shape == result.u.shape == (n + 2,)
    assert result.steps == expected_steps
    assert result.time == final_time
    assert result.dt == final_time / expected_steps
    assert_allclose(result.steps * result.dt, final_time, rtol=1e-15, atol=0.0)
    assert result.mu == result.dt / (1.0 / (n + 1)) ** 2
    assert 0.0 < result.mu <= 0.4
    assert_array_equal(result.u[[0, -1]], [0.0, 0.0])


def test_custom_initial_state_evolution():
    initial = np.array([0.0, -2.0, 0.0])
    result = solve_heat(1, 0.25, initial_state=initial)
    # For a single interior node, every step multiplies by 1-2*mu.
    expected = -2.0 * (1.0 - 2.0 * result.mu) ** result.steps
    assert_allclose(result.u[1], expected, rtol=1e-14, atol=0.0)
    assert_array_equal(result.u[[0, -1]], [0.0, 0.0])
    assert_array_equal(initial, [0.0, -2.0, 0.0])


def test_zero_time_returns_a_copy_without_steps():
    initial = np.array([0.0, 1.0, -2.0, 3.0, 0.0])
    result = solve_heat(3, 0.0, initial_state=initial)
    assert_array_equal(result.u, initial)
    assert not np.shares_memory(result.u, initial)
    assert result.steps == 0
    assert result.time == result.dt == result.mu == 0.0


def test_exact_sine_solution_at_positive_time():
    x = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    amplitude = np.exp(-np.pi**2 * 0.01)
    expected = amplitude * np.array([0.0, np.sqrt(0.5), 1.0, np.sqrt(0.5), 0.0])
    assert_allclose(exact_sine_solution(x, 0.01), expected, rtol=0.0, atol=1e-15)


def test_numerical_solution_matches_exact_sine_at_positive_time():
    result = solve_heat(63, 0.01)
    exact = exact_sine_solution(result.x, result.time)
    # Along this stable path the expected maximum error is about 2.5e-5.
    assert np.max(np.abs(result.u[1:-1] - exact[1:-1])) < 3e-5


def test_second_order_convergence_along_stable_refinement_path():
    errors = []
    for n in [15, 31, 63]:
        result = solve_heat(n, 0.01, mu_target=0.4)
        exact = exact_sine_solution(result.x, result.time)
        errors.append(np.max(np.abs(result.u[1:-1] - exact[1:-1])))
    errors = np.array(errors)
    assert np.all(errors > 0.0)
    assert np.all(errors[1:] < errors[:-1])
    orders = np.log(errors[:-1] / errors[1:]) / np.log(2.0)
    # Halving h gives dt=O(h^2). Integer step rounding affects the coarsest order;
    # require each order to be within 0.2 of two, and strictly above 1.8.
    assert np.all(orders > 1.8)
    assert_allclose(orders, 2.0, rtol=0.0, atol=0.2)


def test_specified_high_frequency_unstable_mode():
    n = 63
    mu = 0.6
    state = np.zeros(n + 2)
    state[1:-1] = np.sin(n * np.pi * np.arange(1, n + 1) / (n + 1))
    amplification = 1.0 - 4.0 * mu * np.sin(n * np.pi / (2.0 * (n + 1))) ** 2
    assert abs(amplification) > 1.0
    updated = ftcs_step(state, mu)
    # Allow rounding in the sampled high-frequency sine, whose phase reaches 63*pi.
    assert_allclose(updated, amplification * state, rtol=0.0, atol=1e-13)
    ratio = np.max(np.abs(updated)) / np.max(np.abs(state))
    assert ratio > 1.0
    assert_allclose(ratio, abs(amplification), rtol=0.0, atol=1e-13)


@pytest.mark.parametrize(
    "state",
    [[0.0, 0.0], [[0.0, 1.0, 0.0]], [1.0, 2.0, 0.0], [0.0, np.nan, 0.0]],
)
def test_invalid_states_are_rejected(state):
    with pytest.raises(ValueError):
        ftcs_step(state, 0.4)


@pytest.mark.parametrize("mu", [-0.1, np.nan, np.inf])
def test_invalid_step_parameters_are_rejected(mu):
    with pytest.raises(ValueError, match="mu"):
        ftcs_step([0.0, 1.0, 0.0], mu)


@pytest.mark.parametrize("final_time", [-0.01, np.nan, np.inf])
def test_invalid_final_times_are_rejected(final_time):
    with pytest.raises(ValueError, match="final_time"):
        solve_heat(7, final_time)


@pytest.mark.parametrize("mu_target", [0.0, -0.1, 0.6, np.nan, np.inf])
def test_invalid_stable_targets_are_rejected(mu_target):
    with pytest.raises(ValueError, match="mu_target"):
        solve_heat(7, 0.01, mu_target=mu_target)


def test_initial_state_must_match_grid_size():
    with pytest.raises(ValueError, match=r"n\+2"):
        solve_heat(7, 0.01, initial_state=[0.0, 1.0, 0.0])
