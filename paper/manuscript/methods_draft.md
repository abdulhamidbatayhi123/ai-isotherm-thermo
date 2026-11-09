<!-- Paper 3A Methods, DRAFT written from PREREG_P3A.md before the freeze (2026-11-09).
Every number carries its source in an HTML comment. Re-check against the FROZEN prereg and the
result files before submission; the journal's format is applied after the journal is chosen. -->

# Methods

## Pre-registration

The design, the data, the models, the tuning rules, the metrics, the statistical tests and the
words of every verdict were fixed in a pre-registration (PREREG_P3A.md) and frozen before any
confirmatory fit. The freeze is a public, tagged commit (`prereg-p3a-freeze`) whose manifest holds
the SHA-256 of 71 files (the text, the data, the tuned configurations and the fits behind them,
the synthetic-world and power results, and every script that builds, fits or scores, including an
independently written second scorer) and the package versions; the confirmatory scripts refuse to
run if any of them differs. <!-- scripts/run_confirmatory.py FROZEN (71 entries, da2246c) --> Every defect found in the
design, code or data, before or after the freeze, is listed with its cause and fix in a public
ledger (CORRECTIONS_P3A.md). <!-- P3A-1 to P3A-24 at the time of writing; update at submission -->

## Data

**Sources and inclusion.** Water adsorption isotherms of MOFs and COFs measured at three or more
temperatures on one sample were collected from the primary literature and from ISODB (NIST).
A material entered the confirmatory set if, at three or more temperatures, its adsorption
isotherm had at least 8 points with 0 < p/p_sat <= 0.90, its figure passed the digitisation
quality gates, its temperatures were unambiguous, and its curve was covered (no gap above 0.25 in
p/p_sat, and a first point at p/p_sat <= 0.10 or at an uptake <= 0.10 of the largest).
<!-- PREREG 3.3 rules 1-5 --> Where a paper gave both measured isotherms and curves derived from
them (characteristic curves), the measured isotherms were used. <!-- P3A-20 --> The confirmatory
set has 13 materials, 5 MOFs and 8 COFs; every decision and its reason is in the inclusion log.
<!-- data/inclusion_log.csv; data/dataset_summary.json --> Four materials not needed for the test
(CuBTC, MIL-100, MIL-160 and TFPPy-PDA-COF) form a development set used only to choose
hyperparameters. <!-- PREREG 3.1 -->

**Digitisation.** Isotherms published only as figures were digitised before any model was fitted.
Vector figures were read from the PDF drawing commands (marker centres mapped through the axis
ticks); raster figures by template matching with the figure's own marker footprint, with tick
marks located to sub-pixel precision and an open-marker veto against desorption points. No
physical prior was used to filter points. <!-- PREREG 3.5; src/p3a/digitise.py --> The method was
validated against published numeric data: on Mg-SU-102 the vector extraction recovered 198 of 198
points (RMS 1e-5 g/g) <!-- logs/digitisation_error.json -->, and on raster figures of HKUST-1 the
RMS uptake error was 0.11 to 0.19 % of the axis (0.0012 to 0.0034 of the isotherm's maximum), with
no false detections. <!-- logs/digitisation_validation.json -->

**Preprocessing.** Only adsorption branches with p/p_sat <= 0.90 were used. Relative pressures
were converted with the IAPWS saturation pressure; absolute pressures were used as reported.
Uptakes were converted to mol/kg. <!-- PREREG 3.4 -->

## Models

Every model is a function q(s, T) of s = ln(p/Pa) and temperature, and the isosteric heat of every
model is computed by the same code, Qst = -R T^2 (dq/dT)/(dq/ds), by automatic differentiation.
<!-- src/p3a/thermo.py -->

**The potential model (P).** P learns the reduced spreading pressure
psi(s, T) = sum_k c_k(T)/g_k softplus(g_k (s - theta_k(T))) and predicts q* = d psi/d s =
sum_k c_k(T) sigmoid(g_k (s - theta_k(T))), with capacities c_k > 0, Henry terms (g = 1) and
cooperative terms (g >= 1.5), van't Hoff positions theta_k(T) = theta_k0 - (Q_k/R)(1/T - 1/T_ref)
and an adsorbate-expansion factor. For every parameter value, q* is strictly increasing in p,
q*/p tends to a positive Henry constant as p -> 0, and the heat is defined everywhere.
<!-- src/p3a/models.py PotentialIsotherm -->

**Factorial comparators.** The models form a 3 x 3 factorial of shape constraint (none, penalty,
hard) and temperature structure (a free network in 1/T, van't Hoff per term, or the
temperature-invariant characteristic curve in A = RT ln(p_sat/p)). In the van't Hoff and
characteristic-curve columns, the unconstrained and penalised models have P's or the hard
characteristic curve's function class without the constraints, the same initial function and the
same tuned structure; the penalty models add monotonicity and (except for the characteristic
curve) a scale-free Henry-limit penalty on collocation points that reach the held-out temperature.
A dual-site Sips model with van't Hoff affinities (C1) is the classical comparator; an MLP on
(ln(p/p_sat), 1/T) and a Kirchhoff variant of P with a heat capacity per term are reported
descriptively. <!-- PREREG 4; src/p3a/study.py build -->

## Fitting and tuning

Each model was fitted by Adam followed by L-BFGS on the mean squared error of q scaled by the
largest training uptake, in double precision, from 5 seeds; the fit with the lowest training loss
was kept, never selected on held-out error. Every scale of a fit came from the training
temperatures only. <!-- PREREG 5.2-5.3; P3A-10 --> Hyperparameters were chosen on the
development set alone, in two stages: the structural models tried up to 12 configurations each,
and the unconstrained and penalised models inherited the chosen structure, the penalty models
tuning only the penalty weight over 1e-4 to 100; every chosen weight lay inside that grid.
<!-- PREREG 5.4; results/dev_best_configs.json; P3A-23 -->

## Tasks and outcomes

For a material with temperatures T_1 < ... < T_k, E-high trains on T_1..T_(k-1) and predicts
T_k; E-low trains on T_2..T_k and predicts T_1. The primary outcome is the held-out error
E = RMSE(q_pred - q_obs)/q_ref, summarised per material as the mean of log10 E over the two tasks.
<!-- PREREG 5.1, 6.1 --> Physical violations were counted on a dense grid: a fit violated if an
isotherm fell by more than 2 % of q_ref below its running maximum, or went below -2 % of q_ref,
inside the domain where the penalties act; violations were counted over the fits of the two
extrapolation tasks. <!-- PREREG 6.2, 7.1; study.VIOL_TOL; analyse.H3_TASKS --> Because no material
here has a calorimetric water heat, the heat was tested on synthetic isotherms with exact heats,
built on every material's own temperatures and pressures from five truth families, with noise of
0.4 % of q_ref. <!-- PREREG 6.3a; scripts/run_synthetic_h2.py SIGMA_REL -->

## Statistics

The unit is the material (n = 13). For each comparison of P with a model X, d_m = e_m(P) - e_m(X)
was tested with the exact two-sided Wilcoxon signed-rank test, with Holm correction over the four
confirmatory comparisons (penalty model, characteristic curve, generic network, dual-site Sips); the
effect is the Hodges-Lehmann estimate with exact distribution-free
95 % and 90 % intervals, reported as the error ratio R = 10^d. A failed fit was ranked worst, never
dropped. The words of each verdict follow a table fixed in advance, with a smallest effect of
interest of 25 % (R = 0.8 or 1.25). The one declared primary claim, that the hard constraints cost
no more than 25 % in accuracy against the penalty model, was judged by non-inferiority: the upper
exact 95 % bound of R below 1.25 (one-sided 2.5 %), with the 98.75 % bound reported beside it.
<!-- PREREG 7.1-7.3, 8; scripts/analyse.py --> Before the freeze, the power of each verdict was
simulated with the analysis code itself, and the whole pipeline was run on five synthetic worlds,
with an expected outcome written for each before it ran, to show which verdicts can fail; three of
the expectations were missed and are reported as missed, and the comparison of a free with a van't
Hoff temperature dependence was made descriptive because it could not fail.
<!-- PREREG 7.3, 7.4; results/mde.json; results/worlds_check.json; P3A-21, P3A-22 -->

## Data and code availability

Code, the pre-registration, the freeze manifest, the corrections ledger, the digitisation
provenance and all results are public (github.com/abdulhamidbatayhi123/ai-isotherm-thermo; an
archived release with a DOI will be cited). Digitised point lists from sources whose licence does
not permit redistribution are kept locally; their provenance, fitted parameters and predictions
are published.

## Use of AI tools

<!-- Use the user's saved wording (memory: ai-declaration-wording) verbatim at submission:
AI as a tool; the author designed the study, made every decision and takes responsibility. -->
