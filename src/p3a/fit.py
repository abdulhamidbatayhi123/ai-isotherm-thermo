"""Least-squares fitting: Adam, then L-BFGS polishing. Deterministic given the torch seed."""
import torch


def fit(model, s, T, q, adam_steps=2000, lbfgs_steps=200, lr=1e-2, penalty=None,
        penalty_weight=0.0):
    """Minimise mean((model(s, T) - q)^2) + penalty_weight * penalty(model).

    penalty is a callable model -> scalar tensor (for the Pen competitor). Returns the
    final data loss (mean squared error, (mol/kg)^2).
    """

    def objective():
        loss = (model(s, T) - q).pow(2).mean()
        if penalty is not None and penalty_weight > 0:
            loss = loss + penalty_weight * penalty(model)
        return loss

    opt = torch.optim.Adam(model.parameters(), lr=lr)
    for _ in range(adam_steps):
        opt.zero_grad()
        loss = objective()
        loss.backward()
        opt.step()

    if lbfgs_steps:
        lb = torch.optim.LBFGS(model.parameters(), max_iter=lbfgs_steps,
                               line_search_fn="strong_wolfe", tolerance_grad=1e-12,
                               tolerance_change=1e-15)

        def closure():
            lb.zero_grad()
            loss = objective()
            loss.backward()
            return loss

        lb.step(closure)

    with torch.no_grad():
        return (model(s, T) - q).pow(2).mean().item()
