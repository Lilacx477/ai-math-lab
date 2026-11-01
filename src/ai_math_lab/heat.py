"""Explicit FTCS evolution for the heat equation in BENCHMARK-002.md."""

from dataclasses import dataclass
from math import ceil

import numpy as np
from numpy.typing import ArrayLike

from ai_math_lab.poisson import FloatArray, uniform_grid


@dataclass(frozen=True)
class HeatSolution:
    """Full grid and final state, with the effective time-stepping parameters."""

    x: FloatArray
    u: FloatArray
    time: float
    dt: float
    steps: int
    mu: float


def _state_array(u: ArrayLike) -> FloatArray:
    state = np.asarray(u, dtype=float)
    if state.ndim != 1 or state.size < 3:
        raise ValueError("state must be one-dimensional with at least one interior point")
    if not np.all(np.isfinite(state)):
        raise ValueError("state must contain only finite values")
    if state[0] != 0.0 or state[-1] != 0.0:
        raise ValueError("state must have exactly zero Dirichlet boundary values")
    return state


def ftcs_step(u: ArrayLike, mu: float) -> FloatArray:
    """Return one step with weights (mu, 1-2*mu, mu), leaving the input unchanged.

    The full state includes two zero boundary values. Any finite mu >= 0 is
    allowed, including unstable examples; the maximum principle holds for
    0 <= mu <= 1/2. The returned boundary values are exactly zero.
    """
    if not np.isfinite(mu) or mu < 0.0:
        raise ValueError("mu must be finite and nonnegative")
    state = _state_array(u)
    updated = np.zeros_like(state)
    updated[1:-1] = (
        mu * state[:-2] + (1.0 - 2.0 * mu) * state[1:-1] + mu * state[2:]
    )
    return updated


def exact_sine_solution(x: FloatArray, t: float) -> FloatArray:
    """Evaluate exp(-pi^2*t)*sin(pi*x) for a finite, nonnegative time."""
    if not np.isfinite(t) or t < 0.0:
        raise ValueError("time must be finite and nonnegative")
    return np.exp(-np.pi**2 * t) * np.sin(np.pi * x)


def solve_heat(
    n: int,
    final_time: float,
    *,
    mu_target: float = 0.4,
    initial_state: ArrayLike | None = None,
) -> HeatSolution:
    """Evolve a full initial state on the shared grid h=1/(n+1).

    The default initial state is sin(pi*x), with endpoints set exactly to zero.
    A supplied state must have n+2 finite entries and exactly zero endpoints.
    For T > 0, use steps=ceil(T/(mu_target*h^2)) and dt=T/steps. A roundoff
    guard can add a step to ensure mu=dt/h^2 <= mu_target. The target must
    satisfy 0 < mu_target <= 1/2. At T=0, return a copy with no steps and dt=mu=0.
    """
    x = uniform_grid(n)
    if not np.isfinite(final_time) or final_time < 0.0:
        raise ValueError("final_time must be finite and nonnegative")
    if not np.isfinite(mu_target) or not 0.0 < mu_target <= 0.5:
        raise ValueError("mu_target must satisfy 0 < mu_target <= 1/2")

    if initial_state is None:
        u = exact_sine_solution(x, 0.0)
        u[[0, -1]] = 0.0
    else:
        u = _state_array(initial_state).copy()
        if u.shape != x.shape:
            raise ValueError("initial_state must have n+2 entries")

    if final_time == 0.0:
        return HeatSolution(x=x, u=u, time=0.0, dt=0.0, steps=0, mu=0.0)

    h = 1.0 / (n + 1)
    steps = max(1, ceil(final_time / (mu_target * h**2)))
    while True:
        dt = final_time / steps
        mu = dt / h**2
        if mu <= mu_target:
            break
        steps += 1
    for _ in range(steps):
        u = ftcs_step(u, mu)
    return HeatSolution(x=x, u=u, time=final_time, dt=dt, steps=steps, mu=mu)
