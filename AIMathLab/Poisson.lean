module

public import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

/-!
# Quadratic benchmark for the one-dimensional Poisson operator

The negative centered second difference of `q(x) = x(1-x)/2` is exactly one
for every real evaluation point and every nonzero real spacing.
-/

@[expose] public section

namespace AIMathLab

/-- The quadratic manufactured solution from `BENCHMARK.md`. -/
noncomputable def quadratic (x : ℝ) : ℝ := x * (1 - x) / 2

/-- Exact identity with the same sign convention as the Python discrete operator. -/
theorem quadratic_centered_difference (x h : ℝ) (hh : h ≠ 0) :
    (-quadratic (x - h) + 2 * quadratic x - quadratic (x + h)) / h ^ 2 = 1 := by
  unfold quadratic
  field_simp [hh]
  ring

end AIMathLab
