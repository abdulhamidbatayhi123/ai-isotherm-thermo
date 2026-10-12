"""Properties that the proposed potential model must have for EVERY parameter value."""
import pytest
import torch

from p3a import models, thermo, synthetic as syn
from p3a.constants import R

SEEDS = range(12)
MODES = ("vanthoff", "kirchhoff", "nn")
T_GRID = torch.linspace(273.15, 373.15, 11)
S_GRID = torch.linspace(-2.0, 12.0, 701)


def _random_potential(seed, mode="vanthoff"):
    torch.manual_seed(seed)
    m = models.PotentialIsotherm(n_henry=2, n_coop=6, hidden=16, t_mode=mode)
    with torch.no_grad():  # push far from the initialisation so the test is not a lucky draw
        for p in m.parameters():
            p.add_(3.0 * torch.randn_like(p))
    return m


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("seed", SEEDS)
def test_potential_model_is_strictly_monotone_and_positive(seed, mode):
    m = _random_potential(seed, mode)
    v = thermo.violations(m, s_grid=S_GRID, T_grid=T_GRID)
    assert v["nonmonotone_points"] == 0
    assert v["negative_uptake_points"] == 0


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("seed", SEEDS)
def test_potential_model_uptake_is_derivative_of_its_potential(seed, mode):
    m = _random_potential(seed, mode)
    s = torch.linspace(0.0, 10.0, 50).requires_grad_(True)
    T = torch.full((50,), 300.0)
    psi = m.potential(s, T)
    dpsi = torch.autograd.grad(psi.sum(), s)[0]
    assert torch.allclose(dpsi, m(s.detach(), T), rtol=1e-10, atol=1e-12)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("seed", SEEDS)
def test_potential_model_has_exact_henry_limit(seed, mode):
    m = _random_potential(seed, mode)
    T = torch.tensor([280.0, 320.0, 360.0])
    K_formula = m.henry_constant(T)
    assert torch.all(K_formula > 0)
    # the limit p -> 0 itself; how fast it is approached depends on the parameters
    s_low = torch.full((3,), -300.0)
    ratio = m(s_low, T) / torch.exp(s_low)
    assert torch.allclose(ratio, K_formula, rtol=1e-8)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("seed", SEEDS)
def test_potential_model_isosteric_heat_is_finite_everywhere(seed, mode):
    m = _random_potential(seed, mode)
    S, T = torch.meshgrid(S_GRID[::10], T_GRID, indexing="ij")
    qst = thermo.isosteric_heat(m, S.reshape(-1), T.reshape(-1))
    assert torch.isfinite(qst).all()


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("seed", SEEDS)
def test_ldf_rate_has_the_sign_of_the_chemical_potential_difference(seed, mode):
    m = _random_potential(seed, mode)
    g = torch.Generator().manual_seed(1000 + seed)
    n = 500
    s = -2 + 14 * torch.rand(n, generator=g)
    T = 273.15 + 100 * torch.rand(n, generator=g)
    qmax = m(torch.full((n,), 40.0), T)
    q = qmax * torch.rand(n, generator=g)
    k = models.LDFRate(hidden=8)
    rate = k(q, s, T) * (m(s, T) - q)
    # mu_gas - mu_ads(q) = RT (s - s_eq(q)), with s_eq the equilibrium ln p at loading q
    s_eq = thermo.invert_isotherm(m, q, T, lo=-80.0, hi=60.0, iters=80)
    dmu = R * T * (s - s_eq)
    assert torch.all(rate * dmu >= 0)


def test_unconstrained_mlp_can_violate_monotonicity():
    """The counter is not vacuous: a randomly initialised MLP does violate P1."""
    found = False
    for seed in range(10):
        torch.manual_seed(seed)
        u = models.MLPIsotherm(hidden=32)
        v = thermo.violations(u, s_grid=S_GRID, T_grid=T_GRID)
        found = found or v["nonmonotone_points"] > 0
    assert found


def test_penalty_loss_is_zero_for_a_monotone_isotherm_and_positive_otherwise():
    s_col = torch.linspace(0.0, 10.0, 200)
    T_col = torch.full((200,), 300.0)
    ok = syn.langmuir(20.0, 1e-9, 45e3)
    assert models.monotonicity_penalty(ok, s_col, T_col).item() == 0.0

    def bad(s, T):
        return -s

    assert models.monotonicity_penalty(bad, s_col, T_col).item() > 0.0


def test_characteristic_curve_is_temperature_invariant_in_A():
    torch.manual_seed(0)
    c = models.CharacteristicCurve(n_terms=4)
    from p3a import water
    A = torch.tensor([2e3, 5e3, 9e3])
    out = []
    for Tv in (290.0, 320.0, 350.0):
        T = torch.full((3,), Tv)
        s = torch.log(water.p_sat(T)) - A / (R * T)
        out.append(c(s, T))
    assert torch.allclose(out[0], out[1], rtol=1e-12) and torch.allclose(out[0], out[2], rtol=1e-12)


def test_potential_model_recovers_a_held_out_temperature_on_synthetic_data():
    """Small recovery fit: train at 3 temperatures, predict a 4th; the heat must match.

    Uses t_mode="vanthoff". With t_mode="nn" the same fit extrapolates with errors above
    1 mol/kg (scratch diagnostic, 2026-10-13); that comparison belongs to the study, not here.
    """
    truth = syn.dual_site_sips([(4.0, syn.b0_from(0.05, 58e3), 58e3, 1.0),
                                (16.0, syn.b0_from(1 / 630.0, 50e3), 50e3, 4.0)])
    s_tr, T_tr = [], []
    for Tv in (288.15, 298.15, 308.15):
        s = torch.linspace(3.0, 8.3, 40)
        s_tr.append(s)
        T_tr.append(torch.full_like(s, Tv))
    s_tr, T_tr = torch.cat(s_tr), torch.cat(T_tr)
    q_tr = truth(s_tr, T_tr)
    torch.manual_seed(0)
    m = models.PotentialIsotherm(n_henry=2, n_coop=4, s_center=6.0, s_scale=2.0, t_mode="vanthoff")
    from p3a import fit
    fit.fit(m, s_tr, T_tr, q_tr, adam_steps=3000, lbfgs_steps=300)
    s_te = torch.linspace(3.5, 8.6, 30)
    for Tv in (278.15, 318.15):  # below and above the training range
        T_te = torch.full_like(s_te, Tv)
        err = (m(s_te, T_te) - truth(s_te, T_te)).abs().max().item()
        assert err < 0.5, (Tv, err)  # mol/kg, on a 20 mol/kg isotherm
    # heat in the step region, where the cooperative site dominates
    s_mid = torch.tensor([6.2])
    T_mid = torch.tensor([303.15])
    assert thermo.isosteric_heat(m, s_mid, T_mid).item() == pytest.approx(
        thermo.isosteric_heat(truth, s_mid, T_mid).item(), rel=0.05)


@pytest.mark.parametrize("mode", ("vanthoff", "kirchhoff"))
def test_unconstrained_twin_starts_from_the_same_function(mode):
    s = torch.linspace(0.0, 10.0, 50)
    T = torch.full((50,), 310.0)
    torch.manual_seed(3)
    hard = models.PotentialIsotherm(t_mode=mode)
    torch.manual_seed(3)
    free = models.PotentialIsotherm(t_mode=mode, constrained=False)
    assert torch.allclose(hard(s, T), free(s, T), rtol=1e-12)
    torch.manual_seed(3)
    ch = models.CharacteristicCurve()
    torch.manual_seed(3)
    cf = models.CharacteristicCurve(constrained=False)
    assert torch.allclose(ch(s, T), cf(s, T), rtol=1e-12)


def test_unconstrained_twin_can_violate_monotonicity_and_the_hard_model_cannot():
    torch.manual_seed(0)
    free = models.PotentialIsotherm(constrained=False)
    with torch.no_grad():
        free.c_lin[3] = -2.0  # a negative capacity: allowed in the twin
    assert thermo.violations(free, s_grid=S_GRID, T_grid=T_GRID)["nonmonotone_points"] > 0
    with pytest.raises(ValueError):
        free.henry_constant(T_GRID)
