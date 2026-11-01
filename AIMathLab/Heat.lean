module

public import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
# Local FTCS stability for the one-dimensional heat equation

For `0 ≤ μ ≤ 1/2`, the three weights are nonnegative and sum to one.
The local update therefore preserves every interval containing its three inputs.
These are the coefficients used by the production Python FTCS step.
-/

@[expose] public section

namespace AIMathLab.Heat

/-- Forward Euler in time with the centered positive second spatial difference. -/
noncomputable def ftcsUpdate (μ a b c : ℝ) : ℝ :=
  μ * a + (1 - 2 * μ) * b + μ * c

/-- Every FTCS weight is nonnegative in the stable maximum-principle regime. -/
theorem ftcs_weights_nonnegative (μ : ℝ) (hμ0 : 0 ≤ μ) (hμhalf : μ ≤ 1 / 2) :
    0 ≤ μ ∧ 0 ≤ 1 - 2 * μ ∧ 0 ≤ μ := by
  exact ⟨hμ0, by linarith, hμ0⟩

/-- The FTCS weights sum to one for every real parameter. -/
theorem ftcs_weights_sum (μ : ℝ) : μ + (1 - 2 * μ) + μ = 1 := by
  ring

/-- A shared upper bound on the three old values bounds the updated value. -/
theorem ftcs_update_upper_bound (μ a b c M : ℝ)
    (hμ0 : 0 ≤ μ) (hμhalf : μ ≤ 1 / 2)
    (ha : a ≤ M) (hb : b ≤ M) (hc : c ≤ M) :
    ftcsUpdate μ a b c ≤ M := by
  obtain ⟨hleft, hcenter, hright⟩ := ftcs_weights_nonnegative μ hμ0 hμhalf
  calc
    ftcsUpdate μ a b c ≤ μ * M + (1 - 2 * μ) * M + μ * M :=
      add_le_add
        (add_le_add (mul_le_mul_of_nonneg_left ha hleft)
          (mul_le_mul_of_nonneg_left hb hcenter))
        (mul_le_mul_of_nonneg_left hc hright)
    _ = (μ + (1 - 2 * μ) + μ) * M := by ring
    _ = M := by rw [ftcs_weights_sum, one_mul]

/-- A shared lower bound on the three old values bounds the updated value. -/
theorem ftcs_update_lower_bound (μ a b c L : ℝ)
    (hμ0 : 0 ≤ μ) (hμhalf : μ ≤ 1 / 2)
    (ha : L ≤ a) (hb : L ≤ b) (hc : L ≤ c) :
    L ≤ ftcsUpdate μ a b c := by
  obtain ⟨hleft, hcenter, hright⟩ := ftcs_weights_nonnegative μ hμ0 hμhalf
  calc
    L = (μ + (1 - 2 * μ) + μ) * L := by rw [ftcs_weights_sum, one_mul]
    _ = μ * L + (1 - 2 * μ) * L + μ * L := by ring
    _ ≤ ftcsUpdate μ a b c :=
      add_le_add
        (add_le_add (mul_le_mul_of_nonneg_left ha hleft)
          (mul_le_mul_of_nonneg_left hb hcenter))
        (mul_le_mul_of_nonneg_left hc hright)

/-- One stable FTCS update preserves any interval containing all three inputs. -/
theorem ftcs_preserves_interval (μ a b c L M : ℝ)
    (hμ0 : 0 ≤ μ) (hμhalf : μ ≤ 1 / 2)
    (ha : L ≤ a ∧ a ≤ M) (hb : L ≤ b ∧ b ≤ M) (hc : L ≤ c ∧ c ≤ M) :
    L ≤ ftcsUpdate μ a b c ∧ ftcsUpdate μ a b c ≤ M := by
  exact ⟨ftcs_update_lower_bound μ a b c L hμ0 hμhalf ha.1 hb.1 hc.1,
    ftcs_update_upper_bound μ a b c M hμ0 hμhalf ha.2 hb.2 hc.2⟩

end AIMathLab.Heat
