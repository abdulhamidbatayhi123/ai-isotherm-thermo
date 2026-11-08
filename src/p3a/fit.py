"""Least-squares fitting: Adam, then L-BFGS polishing. Deterministic given the torch seed."""
import torch


def fit(model, s, T, q, adam_steps=2000, lbfgs_steps=200, lr=1e-2, penalty=None,
        penalty_weight=0.0, q_scale=1.0, l2=0.0):
    """Minimise mean(((model(s, T) - q) / q_scale)^2) + penalty_weight * penalty(model)
    + l2 * mean(theta^2) over all parameters (weight decay; used for the MLP cells only,
    review B4), identically in the Adam and the L-BFGS phases.

    penalty is a callable model -> scalar tensor (for the Pen competitor). Returns the
    final data loss on the same scale (dimensionless when q_scale = q_ref).
    """

    def objective():
        loss = ((model(s, T) - q) / q_scale).pow(2).mean()
        if penalty is not None and penalty_weight > 0:
            loss = loss + penalty_weight * penalty(model)
        if l2 > 0:
            theta = torch.cat([p.flatten() for p in model.parameters()])
            loss = loss + l2 * theta.pow(2).mean()
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
        return ((model(s, T) - q) / q_scale).pow(2).mean().item()
