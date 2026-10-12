"""Synthetic diagnostic (not confirmatory): how the temperature mode of the potential model
affects extrapolation to temperatures outside training.

Truth: a Henry site plus a cooperative step, both with van't Hoff affinities. This truth lies
inside the "vanthoff" family, so the comparison shows the cost of a free temperature network,
not an advantage on real data. Output: logs/diag_tmode_extrapolation.log
"""
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from p3a import fit, models, synthetic as syn  # noqa: E402

truth = syn.dual_site_sips([(4.0, syn.b0_from(0.05, 58e3), 58e3, 1.0),
                            (16.0, syn.b0_from(1 / 630.0, 50e3), 50e3, 4.0)])
s_tr = torch.cat([torch.linspace(3.0, 8.3, 40)] * 3)
T_tr = torch.cat([torch.full((40,), Tv) for Tv in (288.15, 298.15, 308.15)])
q_tr = truth(s_tr, T_tr)
s_te = torch.linspace(3.5, 8.6, 200)
for mode in ("nn", "vanthoff", "kirchhoff"):
    for seed in (0, 1, 2):
        torch.manual_seed(seed)
        m = models.PotentialIsotherm(n_henry=2, n_coop=4, hidden=8, t_mode=mode)
        mse = fit.fit(m, s_tr, T_tr, q_tr, adam_steps=3000, lbfgs_steps=300)
        errs = []
        for Tv in (278.15, 298.15, 318.15):
            T = torch.full_like(s_te, Tv)
            errs.append((m(s_te, T) - truth(s_te, T)).abs().max().item())
        print(f"mode={mode:9s} seed={seed} train_rmse={mse**0.5:.2e} "
              f"maxerr[278K]={errs[0]:.3f} maxerr[298K]={errs[1]:.3f} maxerr[318K]={errs[2]:.3f} mol/kg",
              flush=True)
