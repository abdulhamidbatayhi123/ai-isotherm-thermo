# A learned adsorbed-phase potential for water isotherms of MOFs and COFs

Paper 3A of a research program on machine learning that explains water sorption in
metal-organic frameworks (MOFs) and covalent organic frameworks (COFs), and does not only
fit it. Paper 1 (the transfer of surrogate models to unseen materials) is at
github.com/abdulhamidbatayhi123/ai-mof-cof-dynamics. Paper 2 (when kinetic equations can be
discovered) is at github.com/abdulhamidbatayhi123/ai-kinetics-discoverability.

**Question.** A model learns one adsorbed-phase potential, the reduced spreading pressure
psi(ln p, T). The water isotherm and the isosteric heat follow from its derivatives. So
monotonicity in pressure, the Henry limit and Clausius-Clapeyron consistency between the
isotherm and the heat hold by construction. Does this predict uptake at unseen temperatures,
and give better isosteric heats, than an unconstrained network, the same network with the
constraints as penalties, and the strongest classical models? The answer is decided by a
pre-registered test on real multi-temperature water isotherms. A classical model winning is
one of the pre-declared outcomes.

**Status (2026-10-13).** Design, literature review, data inventory and a tested code harness
are in progress. The pre-registration is not yet frozen. No confirmatory run has been made.

| Path | What it is |
|---|---|
| `docs/DESIGN.md` | the design and the thermodynamics the model must respect |
| `research/` | literature journals; every source opened live, with URL and read date |
| `data/INVENTORY.md` | multi-temperature water isotherms per material, and their licences |
| `src/p3a/` | the models (proposed and competitors), thermodynamic evaluators, fitting |
| `tests/` | known-answer tests on analytic isotherms; properties for random parameters |
| `scripts/`, `logs/` | every number quoted anywhere comes from a script here and its log |
| `CORRECTIONS_P3A.md` | the public correction ledger |

Run the tests with `python -m pytest -q` (Python 3.12, torch 2.12 CPU; see pyproject.toml).

Licence: MIT for code. Third-party data keep their own licences (see data/INVENTORY.md).
