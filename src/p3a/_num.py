"""Numerically stable building blocks.

torch.sigmoid's gradient is computed as y(1 - y), which rounds to exactly zero once
|z| exceeds about 37. A saturated isotherm would then report dq/ds = 0 and an undefined
isosteric heat. exp(logsigmoid(z)) has exact gradients across the float64 range.
"""
import torch
import torch.nn.functional as F


def sigmoid(z):
    return torch.exp(F.logsigmoid(z))


def softplus(z):
    """log(1 + e^z), with gradient equal to sigmoid(z) to machine precision (no threshold)."""
    return torch.logaddexp(torch.zeros_like(z), z)
