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
    assert study.qst_error(TRUTH, TRUTH, m, 318.15) == pytest.approx(0.0, abs=1e-9)
