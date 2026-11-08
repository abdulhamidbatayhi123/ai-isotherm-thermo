"""The study runner on a small synthetic material."""
import numpy as np
import pytest
import torch

from p3a import study, synthetic as syn

TRUTH = syn.dual_site_sips([(4.0, syn.b0_from(0.05, 58e3), 58e3, 1.0),
                            (16.0, syn.b0_from(1 / 630.0, 50e3), 50e3, 4.0)])


def _material(temps=(288.15, 298.15, 308.15, 318.15)):
    T, s = [], []
    for Tv in temps:
        sv = np.linspace(3.0, 8.0, 20)
        s.append(sv)
        T.append(np.full_like(sv, Tv))
    T, s = np.concatenate(T), np.concatenate(s)
    q = TRUTH(torch.as_tensor(s), torch.as_tensor(T)).numpy()
    return study.Material("synthetic", T, s, q)


def test_tasks_hold_out_the_extremes_and_the_middle():
    m = _material()
    t = study.tasks(m)
    assert t["E-high"] == ([288.15, 298.15, 308.15], 318.15)
    assert t["E-low"] == ([298.15, 308.15, 318.15], 288.15)
    assert t["I-mid"] == ([288.15, 308.15, 318.15], 298.15)


@pytest.mark.parametrize("cell", study.CELLS)
def test_every_cell_builds_fits_and_evaluates(cell):
    m = _material()
    cfg = study.Config(adam_steps=30, lbfgs_steps=5, hidden=8, n_coop=2, n_terms=3)
    train_T, T_out = study.tasks(m)["E-high"]
    res = study.fit_cell(cell, cfg, m, train_T, seeds=(0, 1))
    assert len(res) == 2 and res[0].train_loss <= res[1].train_loss
    E = study.error_E(res[0].model, m, T_out)
    assert np.isfinite(E) or E == float("inf")
    v = study.violation_counts(res[0].model, m)
    assert v["points"] > 0


@pytest.mark.parametrize("cell", ["P", "F-hard", "A-hard", "P-K"])
def test_hard_cells_never_violate_monotonicity_on_the_dense_grid(cell):
    m = _material()
    cfg = study.Config(adam_steps=30, lbfgs_steps=5, hidden=8, n_coop=2, n_terms=3)
    res = study.fit_cell(cell, cfg, m, study.tasks(m)["E-high"][0], seeds=(0, 1))
    v = study.violation_counts(res[0].model, m)
    assert v["nonmonotone"] == 0 and v["negative_q"] == 0


def test_identical_initialisations_are_refused(monkeypatch):
    m = _material()
    cfg = study.Config(adam_steps=2, lbfgs_steps=0)
    monkeypatch.setattr(torch, "manual_seed", lambda s: torch.random.default_generator.manual_seed(0))
    with pytest.raises(RuntimeError, match="same parameters"):
        study.fit_cell("P", cfg, m, study.tasks(m)["E-high"][0], seeds=(0, 1))


def test_qst_error_is_zero_for_the_truth_itself():
    m = _material()
    prim, sec = study.qst_error(TRUTH, TRUTH, m, 318.15)
    assert prim == pytest.approx(0.0, abs=1e-6) and sec == pytest.approx(0.0, abs=1e-9)


def test_qst_error_primary_compares_heats_at_equal_loading():
    """A model shifted in pressure has the truth's Qst(q) curve exactly (the shift is
    temperature independent), so the loading-matched error is ~0 while the state-matched
    error is not (review F1)."""
    m = _material()
    shifted = lambda s, T: TRUTH(s + 0.3, T)  # noqa: E731
    prim, sec = study.qst_error(shifted, TRUTH, m, 318.15)
    assert prim == pytest.approx(0.0, abs=1e-3)
    assert sec > 0.1


def test_qst_error_fails_when_too_few_states_are_in_the_window():
    m = _material()
    empty = lambda s, T: 0.0 * s  # noqa: E731
    assert study.qst_error(empty, TRUTH, m, 318.15)[0] == float("inf")


def test_fit_scale_uses_training_temperatures_only(monkeypatch):
    """The held-out isotherm never sets a scale of the fit (CORRECTIONS P3A-10)."""
    m = _material()
    seen = {}
    real_build = study.build

    def spy(cell, cfg, s_center, s_scale, q_scale):
        seen["q_scale"] = q_scale
        return real_build(cell, cfg, s_center, s_scale, q_scale)

    monkeypatch.setattr(study, "build", spy)
    train_T, T_out = study.tasks(m)["E-low"]  # the held-out lowest temperature has the largest q
    study.fit_cell("P", study.Config(adam_steps=2, lbfgs_steps=0), m, train_T, seeds=(0,))
    q_train_max = m.q[np.isin(m.T, train_T)].max()
    assert seen["q_scale"] == pytest.approx(q_train_max)
    assert seen["q_scale"] < m.q_ref


def test_tolerant_violations_ignore_tiny_wiggles_and_flag_real_drops():
    m = _material()
    wiggle = lambda s, T: TRUTH(s, T) - 2e-3 * m.q_ref * torch.sin(50 * s)  # noqa: E731  (drop <= 0.4 %)
    drop = lambda s, T: TRUTH(s, T) - 0.05 * m.q_ref * torch.sigmoid(10 * (s - 6.0))  # noqa: E731
    vw = study.violation_counts(wiggle, m)
    vd = study.violation_counts(drop, m)
    assert vw["nonmonotone"] > 0 and not study.violates(vw)          # strict sees it, tolerant does not
    assert study.violates(vd)                                         # a 5 % fall is a violation
    vt = study.violation_counts(TRUTH, m)
    assert not study.violates(vt) and not study.violates(vt, "out") and not study.p_bug(vt)
