# Pre-registration, Paper 3A (DRAFT, not frozen)

**Status: DRAFT for the author's review, revised 2026-11-08 after an adversarial review
(`REVIEW_cs.md` in the AgentHub, at commit f0c98d4; the changes are listed in section 12 and in
CORRECTIONS_P3A.md P3A-10 to P3A-19). Nothing in this file binds until the freeze commit
"FREEZE PREREG_P3A". No confirmatory fit has been run. Before the freeze, the development
set (section 3.1) may be used to set the hyperparameters of section 5.4 and to check the
pipeline, and synthetic data may be used for the power analysis (7.3) and the
"can it fail" worlds (7.4). Those are the only uses allowed.**

Title (working): *Does a thermodynamically consistent learned potential extrapolate water
isotherms of MOFs and COFs in temperature? A pre-registered test against penalty,
unconstrained and classical models.*

## 1. Question

A model can learn one adsorbed-phase potential, the reduced grand potential (or spreading
pressure) psi(ln p, T), and obtain the water isotherm q*(p, T) as its derivative. Then
monotonicity in pressure and the Henry limit hold for every parameter value, and the
isosteric heat computed from the isotherm by Clausius-Clapeyron is defined everywhere,
because dq/ds > 0. (Clausius-Clapeyron consistency itself holds for every model in this
study, since each model's heat is computed from its own isotherm; what the potential adds is
a heat that is never undefined.)

Does this, combined with a thermodynamic temperature dependence, predict water uptake at
temperatures outside the training range better than:
- the same function class without the constraints;
- the same function class with the constraints as loss penalties;
- a generic neural network;
- the classical models: a dual-site Sips model with van't Hoff affinities, and the
  temperature-invariant characteristic curve?

A result in which a classical model wins, or in which the hard constraints buy admissibility
but no accuracy, is a pre-declared outcome with its own words (section 8). It will be
reported as prominently as any other.

## 2. Background facts this design rests on (sources in `research/`)

- No published model learns such a potential for adsorption with hard constraints.
  Penalty versions exist and leave violations (lit_3a_ml.md, gap statement). Blind spots:
  ChemRxiv was searched through its Crossref records (titles and abstracts, 180 records,
  nothing that narrows the gap), because its own interface refused automated queries; Liu et
  al. 2023 (J. Mater. Chem. A) is verified from its abstract only (a random forest, no
  constraint mentioned).
- The temperature-invariant Dubinin-Polanyi characteristic curve is the field default for
  water in MOFs. Its invariance is usually asserted visually, without an error number
  (lit_3a_classical.md, competitors). Multi-site Sips/Langmuir-Freundlich fits with van't
  Hoff affinities are the other common choice for heats.
- A synthetic diagnostic showed that convexity and the Henry limit alone do not make
  temperature extrapolation work; the temperature structure does (CORRECTIONS_P3A.md,
  P3A-2). The design therefore separates the two (section 4).
- No material in the confirmatory set has an independently measured (calorimetric) water
  heat (research/lit_3a_calorimetry.md; section 6.3).

## 3. Data

### 3.1 Development set (tuning and pipeline checks only, never confirmatory)

- CuBTC (HKUST-1) and MIL-100, Rezk et al. 2012, ISODB as digitised by NIST (9 temperatures,
  293 to 358 K). Rezk's records come as two series; the 9-temperature series on a common
  pressure grid (ISODB records 26 to 43) is used.
- MIL-160, Cadiau et al. 2015, ISODB (293, 303, 313 K).
- TFPPy-PDA-COF, Tan et al. 2021, Fig. 4 (283.15, 288.15, 298.15 K), digitised. Added
  2026-11-08 before any fit, so that the development set contains a COF (8 of the 13
  confirmatory materials are COFs). It was excluded from the confirmatory set by rule 2 alone
  (7 points at 288.15 K); rule 2 is relaxed to 5 points in the development set, which is
  never scored. Rules 1, 3, 4 and 5 apply.
- CAU-10-H (Frohlich et al. 2014) keeps only 2 usable temperatures (rule 5 at 298 K) and is
  excluded.

CuBTC degrades in water over repeated cycles; its isotherms are used only to choose
hyperparameters, never to judge a model.

### 3.2 Confirmatory set

**Applied 2026-11-03, all before any fit (`data/inclusion_log.csv`,
`data/digitisation_gate_log.csv`; revised 2026-11-09, still before any fit, see below).**
The confirmatory set is **13 materials, 5 MOFs and 8 COFs**:
- MOFs: Mg-SU-102 (9 temperatures, numeric source data), Co2Cl2(BTDD) (measured isotherms,
  SI Fig. S9), Al-fumarate, CALF-25, Zn2(bptc) (4 temperatures).
- COFs: COF-432, COF-482-hydrazide, PI-3-COF, NO-PI-3-COF, COF-SO3H, HFPTP-PDA-COF,
  HFPTP-DMePDA-COF, TFBCz-PDA-COF.

Excluded, with the rule that decided it:
- MOF-303 (Hanikel 2019 S17), AB-COF, COF-480-hydrazide, Py-COF-2D, HCOF-2, COF-309,
  COF-TP-43, HFPTP-BPDA-COF, TTA-TFB-COF and TPB-DMTP-COF: rule 5. Markers covered by other
  series leave fewer than 3 usable temperatures.
- MOF-801 (Kim 2018): rule 2, 7 points per isotherm. TFPPy-PDA-COF: rule 2 (now in the
  development set).
- MIL-160(Al) (Silva 2021): rules 1 and 2.
- MOF-801 and MOF-303 (Fathieh 2018, 9 temperatures each): 6 of 9 series pass the colour
  gate, but the overlay gate excludes both figures, because the adsorption steps of all nine
  temperatures coincide and are drawn over each other.
- CAU-23: the overlay gate (open markers covering most of the filled ones).
- Ni2X2(BTDD): rule 4.
- KMF-1 (Cho 2020): rule 4. Its digitised source, the characteristic curves of SI Fig. 18,
  plots the 20 C isotherm a second time as "30 C" (the two series coincide point by point in
  p/p_sat), while the measured isotherms of main-text Fig. 2a step at about 0.11 (20 C) and
  0.14 (30 C). Fig. 2a cannot replace it, because its 20 and 30 C pre-step markers are covered
  by the open 40 C desorption markers. Found 2026-11-09 by inspecting the data-overview figure,
  before any fit (P3A-20).
- Co2Cl2(BTDD) is now digitised from its measured isotherms (SI Fig. S9, vector, absolute
  pressure) instead of the characteristic curves derived from them (Fig. S8): the two give the
  same uptakes, but Fig. S8's relative pressures differ from Fig. S9's by factors of 1.078,
  1.010 and 0.972 at 283, 293 and 298 K, so Fig. S8 was not computed with standard saturation
  pressures (P3A-20). Rule: measured isotherms take precedence over curves derived from them.
- Al-fumarate (25 C) and CALF-25 (303 K) keep 3 of 4 temperatures because one isotherm fails
  rule 5. Their tasks use the remaining temperatures.

Six of the excluded materials (MOF-303, AB-COF, COF-480-hydrazide, Py-COF-2D, HCOF-2,
COF-309) are lost only to digitisation. Numeric data from their authors would restore them.
Any such data arriving after the freeze enter a descriptive extension, never the
confirmatory set. The candidate list as first drafted (2026-10-13) is kept in the history
of this file.

### 3.3 Inclusion rules (applied before any model is fitted to the material)

A material and paper pair is included if all of the following hold. Each exclusion is
recorded with its reason in `data/inclusion_log.csv` by `scripts/build_dataset.py`.
1. There are adsorption-branch isotherms at 3 or more temperatures on the same sample.
2. Each isotherm has at least 8 points with 0 < p/p_sat <= 0.90.
3. The figure passes the digitisation quality gates (section 3.5).
4. The temperatures are unambiguous. A conflict between the main text and the SI (as for
   Ni2X2(BTDD)) excludes the set unless it can be resolved from the source.
5. Coverage (added 2026-11-03, before any fit; CORRECTIONS P3A-8). On the curve as published
   (before the 0.90 cut): no gap between consecutive points larger than 0.25 in p/p_sat; and
   the curve's start is present (first point at p/p_sat <= 0.10 or at an uptake of at most
   0.10 q_ref). A gap in uptake is not a criterion, because steep steps are physical.
6. Source (added 2026-11-09, before any fit; P3A-20): where a paper gives measured isotherms
   and curves derived from them (characteristic curves), the measured isotherms are used. A
   derived curve that contradicts the paper's measured isotherms makes the temperatures
   ambiguous (rule 4): if a "30 C" curve copies the 20 C one, the source cannot say which
   temperature even the 20 C curve belongs to.

Rules 1, 2 and 5 are applied per temperature: an isotherm that fails is dropped, and the
material stays if 3 or more temperatures remain.

Rule 5 needed three versions, each judged only on the digitised data, before any fit (P3A-8).
Its second version was revised after it excluded COF-432 at 25 C, so the rule was not blind
to material identity. A descriptive sensitivity analysis (section 6.4) therefore repeats the
H1 comparisons on every material whose membership changes under the earlier versions and
under a 7-point rule 2 (`build_dataset.py --variant rule5_v1 | rule5_v2 | rule5_none |
minpoints7`). Membership under each, computed 2026-11-09 without any model: 6, 9, 23 and 14
materials respectively (13 under the final rules).

A sample that loses capacity between runs, as reported for some TTI-COFs, is included, and
flagged. It is excluded in a pre-declared sensitivity analysis.

### 3.4 Preprocessing (identical for every model)

- Adsorption branch only. Points with p = 0, and points with p/p_sat > 0.90, are dropped.
  Above 0.90 intercrystalline condensation is common, and the equilibrium potential
  represents the framework's pores only.
- Pressure: p = (p/p_sat) x p_sat(T), with p_sat from IAPWS SR1-86 eq. (1) (`p3a.water`).
  A paper that reports absolute pressure is used as reported. Where the paper states that
  it used another p_sat, that is recorded, and a sensitivity analysis uses the paper's own
  value.
- Uptake is converted to mol/kg (M_water = 18.01528 g/mol; for cm3(STP)/g, 22.414 L/mol).
- T in K is the temperature in degrees C plus 273.15.
- q_ref for a material is its largest uptake with p/p_sat <= 0.90, over all temperatures. It
  is used only to score (E, violations, the heat window). No fit sees it: the scales of a fit
  come from its training temperatures (section 5.4; CORRECTIONS P3A-10).

### 3.5 Digitisation (before any fit; blind to model outputs)

- **Vector figures** (PyMuPDF drawing commands): markers are read by colour, size and
  shape. Series are assigned from the legend's colours. Axes are calibrated from text tick
  labels snapped to tick marks, or, without tick marks, from labels of the modal text
  length. The error is the plotting precision.
- **Raster figures** (`src/p3a/digitise.py`, `scripts/digitise_sources.py`):
  - **Image:** the embedded image at native resolution; a soft mask, if present, is
    composited onto white.
  - **Axes:** frame lines located near positions read from a grid image
    (`scripts/raster_inspect.py`); each tick read by eye is snapped to the tick mark
    (centred between its edges, beyond the frame line's local thickness band, on the side
    the axis's ticks share by majority, nearest to the reading); the axis map is a
    least-squares line through the snapped ticks.
  - **Markers:** template matching with the figure's own marker footprint, cut from the
    legend marker (or an isolated data marker). A detection needs a fill fraction of at least
    0.6 of the template in the series colour (tolerance 0.18) and no white in the template's
    core. A detection centred on an open marker of the same colour (desorption) is vetoed.
    No physical prior is used to filter points.
  - **Outputs:** the script, the calibration points and an overlay image of every detection
    are kept. Point lists from closed or ND-licensed sources stay local; their fitted
    parameters and predictions are published.
- **Measured digitisation error.**
  - Mg-SU-102 Fig. 4a against its numeric source data (`scripts/digitisation_error.py`):
    vector extraction recovers 198 of 198 points (RMS 1e-5 g/g, 0.005 mbar); raster renders
    at 150, 300 and 600 dpi have recall 0.90, 0.94 and 0.94, no false detections, and RMS
    uptake errors of 0.16, 0.10 and 0.09 % of the axis.
  - Further real figures whose authors deposited the plotted numbers
    (`scripts/digitisation_validation.py`, `logs/digitisation_validation.json`; Nat. Commun.
    source data), digitised with the unmodified method, errors in % of the axis span:
    - raster, HKUST-1 F3@HK_30 SI Fig. 21a (298, 318 K) and Fig. 1a (pristine HKUST-1 and
      F3@HK_30, 298 K): RMS uptake error 0.11 to 0.19 % (largest single error 0.50 %), RMS
      pressure error 0.13 to 0.20 %, no false detections; relative to each isotherm's own
      largest uptake, the RMS uptake error is 0.0012 to 0.0034. Recall 0.74 to 0.92 of all
      truth points and 1.00 of the isolated markers, except pristine HKUST-1 in Fig. 1a
      (recall 0.26; 0.67 of isolated markers), whose semi-transparent markers turn darker
      where they overlap and fall outside the colour tolerance. Every isotherm has a small
      systematic shift: mean signed error +0.02 to +0.09 % in uptake and 0.00 to -0.18 % in
      pressure.
    - vector, EMM-8 Fig. 3a (25, 40, 50 C) and bnn-1-Co/Ni Fig. 3a, 3b (27, 60 C): recall 1.00,
      no false detections, RMS errors at most 0.085 % in uptake and 0.034 % in pressure.
    - This validation found a defect: open desorption markers drawn as separate outlines were
      taken as adsorption points by the vector extractor. It was fixed, and no confirmatory
      source had such an item (P3A-18).
  - The synthetic benchmark (`scripts/raster_benchmark.py`, `logs/raster_benchmark.log`):
    worst case recall 0.80 of visible markers (0.56 to 0.58 of all markers in the densest
    figures, where markers are hidden), at most 11 false detections in a figure, each within
    about 2.7 % of the axis of the curve (the desorption offset, P3A-7); curve error at most
    0.64 % RMS and 2.7 % maximum of the axis.
  - The synthetic noise of sections 6.3a and 7.4 is SIGMA_REL = 0.004 q_ref (Gaussian, in
    uptake only): the largest measured raster RMS relative to an isotherm's maximum (0.0034),
    rounded up (raised from 0.002, the Mg-SU-102 value, after the further figures; P3A-19).
    Systematic shifts are covered by the perturbation analysis of section 6.4, whose shift
    (2.7 % of the axis) is far larger than any measured one. ISODB sets digitised by NIST
    (CALF-25, Zn2(bptc), the development set) have an unknown digitisation error.
  - The floor of E set by digitisation is about 0.003 (log10 E about -2.5); it is reported
    next to the observed E.
- **Quality gates**, any failure excluding the set:
  - axis-calibration residual below 0.5 % of the tick span (all raster figures pass; the
    largest is 0.35 %);
  - colour: a series is digitised only if its colour differs from every other series colour
    in the figure, used or not, by at least 0.36 (twice the colour tolerance); a figure needs
    3 such temperature series (`scripts/check_colour_separability.py`, which also reports the
    CIE76 Delta E). Revised 2026-11-08 before any fit from "every pair of series" (review E3;
    P3A-17); no decision changed;
  - the overlay check shows no systematic misses or spurious points.

## 4. Models: a factorial of shape constraint and temperature structure

Every model is a function q(s, T) with s = ln(p / Pa). The Qst of every model is computed
by the same code, `p3a.thermo.isosteric_heat`. Rows are the shape constraint, columns the
temperature structure.

| Shape | Free in 1/T (F) | van't Hoff per term (V) | Characteristic curve in A (A) |
|---|---|---|---|
| none | F-none: `MLPIsotherm` | V-none: `PotentialIsotherm(constrained=False)` | A-none: `CharacteristicCurve(constrained=False)` |
| penalty | F-pen: MLP + penalties | V-pen: V-none + penalties | A-pen: A-none + penalty |
| hard | F-hard: `PotentialIsotherm(t_mode="nn")` | **P = V-hard**: `PotentialIsotherm(t_mode="vanthoff")` | A-hard: `CharacteristicCurve()` |

How the factorial is built:
- P is a positive mixture of Langmuir (g = 1) and cooperative Sips terms (g >= 1.5) with
  van't Hoff affinities and an adsorbate-expansion factor, written as the derivative of one
  convex potential.
- Within the V and A columns, the "none" and "penalty" models have the same function class
  without the constraints, the same initial function and the same tuned structure (term
  counts, optimiser steps) as P or A-hard (section 5.4). They optimise a different
  parametrisation (linear capacities and exponents), so their optimiser path differs; the
  training-loss gap between P and V-none is reported as an optimisation diagnostic.
- In the F column the architectures differ, because a free MLP has no constrained twin.
  F-none differs from P in architecture, constraints and temperature structure at once, so
  H1d is never credited to the constraints.

Other models:
- **C1 (classical reference):** dual-site Sips with van't Hoff affinities and free
  exponents (`MultiSiteSips(n_sites=2)`), as used in practice. It is a small member of P's
  function class without the potential's guarantees, and it is a confirmatory comparator
  (H1e).
- **F-rel (descriptive):** the MLP on (ln(p/p_sat), 1/T). Water isotherms of MOFs are nearly
  invariant in p/p_sat, so this is the natural generic competitor.
- **P-K (secondary):** `t_mode="kirchhoff"`, fitted only where at least 4 training
  temperatures exist (the heat-capacity term is not identifiable from 2).

**Penalties.** `monotonicity_penalty` (the mean of relu(-dq/ds)^2) and `henry_penalty`, the
scale-free relative difference (dq/ds - q)/(|dq/ds| + |q|) at p = 0.01 Pa, plus the same
relative measure of negative uptake (A-pen: monotonicity only, because the characteristic
curve has no Henry limit). They are evaluated on unlabelled collocation points: s from
ln(1 Pa) to ln(0.9 p_sat(T)), 60 points; T from T_min - 15 K to T_max + 15 K of the
material, 9 levels, so that the penalties also act at the held-out temperature.

## 5. Fitting

### 5.1 Tasks

For a material with temperatures T_1 < ... < T_k:
- **E-high:** train on T_1..T_{k-1}, predict T_k.
- **E-low:** train on T_2..T_k, predict T_1.
- **I-mid** (secondary): for k >= 3, hold out the middle temperature, or for even k the
  lower of the two middle ones.

### 5.2 Loss and optimiser

- Loss: the mean squared error of q / q_fit on the training points, where q_fit is the
  largest training uptake. Penalty models add lambda x penalty; the MLP cells add
  l2 x mean(theta^2) over their parameters when their tuned l2 > 0.
- Optimiser: Adam (lr 1e-2) for N_adam steps, then L-BFGS with strong-Wolfe line search for
  N_lbfgs = 300 iterations, in float64 on the CPU (`p3a.fit.fit`).
- Scaling, identical for every cell: ln p (for F-rel, ln(p/p_sat)) is centred on its
  training mean and scaled by its training standard deviation (at least 0.5); uptake is
  scaled by q_fit (`p3a.study.fit_cell`).

### 5.3 Seeds and selection

- Each model, material and task is fitted from 5 seeds.
- The reported fit is the seed with the lowest training data loss. The held-out error is
  never used for selection.
- The seed spread of the held-out error is reported.
- A check in code requires the initial parameter vectors to differ (CORRECTIONS P3A-3).

### 5.4 Hyperparameters, set on the development set only, then frozen

Two stages (`scripts/run_dev.py`; revised before the freeze, review B3 and B5):
- **Stage 1, cells that own a structure.** Grids: P: n_henry in {1, 2}, n_coop in {2, 4, 6},
  N_adam in {2000, 4000} (12). A-hard: n_terms in {3, 4, 6}, N_adam (6). F-hard: hidden in
  {8, 16}, n_henry, n_coop, N_adam (24). F-none and F-rel: hidden in {16, 32, 64}, depth in
  {2, 3}, N_adam, l2 in {0, 1e-5, 1e-4} (36). C1: N_adam (2). Each cell tries
  min(12, grid size) configurations, drawn uniformly without replacement with seed 20261013.
- **Stage 2, cells that inherit.** V-none and P-K take P's chosen configuration and A-none
  takes A-hard's (no search). V-pen, A-pen and F-pen take P's, A-hard's and F-none's chosen
  configuration and tune only lambda in {0.01, 0.1, 1, 10, 100}.
- Rule: for each cell, the configuration with the lowest mean development-set e (section
  6.1) over E-high and E-low; tuning fits use 3 seeds (0 to 2); a failed tuning fit scores as
  the worst observed log10 E plus one decade. Parameter counts are reported.
- The chosen configurations (`results/dev_best_configs.json`, frozen; tuning v2 finished
  2026-11-09):

| Cell | Chosen configuration | Configurations tried | Development mean log10 E |
|---|---|---|---|
| P | n_henry = 2, n_coop = 2, adam_steps = 2000 | 12 | -1.359 |
| V-none | n_henry = 2, n_coop = 2, adam_steps = 2000 | 1 | -1.305 |
| V-pen | n_henry = 2, n_coop = 2, adam_steps = 2000, lam = 0.01 | 5 | -1.309 |
| P-K | n_henry = 2, n_coop = 2, adam_steps = 2000 | 1 | -1.339 |
| F-hard | hidden = 8, n_henry = 1, n_coop = 2, adam_steps = 2000 | 12 | -1.402 |
| F-none | hidden = 32, depth = 3, adam_steps = 4000, l2 = 0.0001 | 12 | -1.277 |
| F-pen | hidden = 32, depth = 3, adam_steps = 4000, l2 = 0.0001, lam = 0.1 | 5 | -1.249 |
| F-rel | hidden = 32, depth = 3, adam_steps = 2000, l2 = 0 | 12 | -1.314 |
| A-hard | n_terms = 6, adam_steps = 4000 | 6 | -1.030 |
| A-none | n_terms = 6, adam_steps = 4000 | 1 | -0.833 |
| A-pen | n_terms = 6, adam_steps = 4000, lam = 0.1 | 5 | -1.019 |
| C1 | adam_steps = 4000 | 2 | -1.247 |

  On the development set F-hard scores best: two of its four materials have 9 temperatures,
  so E-high trains on 8, enough for a free temperature dependence to be learned.
- A first tuning run (v1, 396 fits) used the leaking scale of P3A-10 and one-stage tuning;
  it is kept in `results/superseded_tuning_v1/` and not used.

## 6. Outcomes

### 6.1 Primary outcome: temperature extrapolation error

- E = RMSE(q_pred - q_obs) / q_ref over the held-out isotherm's points.
- For each material m and model X: e_m(X) = mean of log10 E over the tasks E-high and E-low.
  If either task failed (E infinite or an error), e_m(X) is a failure (section 7.2); it is
  never the value of the surviving task.
- For a comparison between P and X: d_m = e_m(P) - e_m(X). A negative d_m means P is better.

### 6.2 Physical violations

- Dense grid G for each material: s from ln(1 Pa) to ln(0.95 p_sat(T)), 400 points; T from
  T_min - 20 K to T_max + 20 K in 2.5 K steps.
- Domains: "in" is the penalty collocation domain (T within T_min - 15 K to T_max + 15 K,
  p <= 0.90 p_sat); "out" is the rest of G (the extrapolated band).
- **Primary (H3) count, with a tolerance above the data's floor:** a fit violates if, in the
  "in" domain, any isotherm of G (fixed T) falls by more than 0.02 q_ref below its running
  maximum as p increases, or any point has q < -0.02 q_ref (`study.violation_counts`,
  `study.violates`). The tolerance is five times SIGMA_REL and about six times the largest
  measured raster RMS (0.0034 of an isotherm's maximum), so a model that follows the data's
  own scatter is not scored as violating, while a fall of 2 % of the capacity is plainly
  visible. (A first value of 0.01 q_ref was set when the error model was 0.002; it was raised
  with the error model, before any fit; P3A-19.)
- **Reported beside it:** the same count in the "out" band; strict counts on all of G
  (points with dq/ds < 0, q < 0, an undefined Qst, Qst outside 0 to 150 kJ/mol).
- P, F-hard, A-hard and P-K must show zero strict counts of dq/ds < 0 and q < 0 by
  construction, and P also of undefined Qst. A non-zero count for P is a bug, is reported
  as such, and halts the analysis until fixed (`analyse.py`). The count of Qst outside 0 to
  150 kJ/mol can be non-zero for P (near saturation dq/ds becomes small) and is not part of
  this rule or of H3.

### 6.3 Isosteric heat

- **(a) Synthetic benchmark with known heats (H2).** This always runs
  (`scripts/run_synthetic_h2.py`).
  - Five truth families, each sampled on every confirmatory material's own temperatures
    and pressure grid, with shape parameters fitted by bounded least squares (on q / q_ref)
    to that material's middle-temperature isotherm; the thermodynamic parameters are fixed:
    - **KS:** a Langmuir site (Q0 = 55 kJ/mol) plus a cooperative Sips site (Q0 = 48 kJ/mol,
      dc = 40 J/mol/K, exponent at least 1.5): inside P-K's family, near P's;
    - **DA:** Dubinin-Astakhov, q = W0 exp(-(A/E)^n), 1 <= n <= 6: inside A's family;
    - **FG:** Fowler-Guggenheim, Q0 = 45 kJ/mol, lateral attraction w between 0 and
      3.9 R T_min: inside neither;
    - **HS:** strong hydrophilic sites, a Langmuir site with Q = 80 kJ/mol holding at most
      0.3 q_ref plus a Sips site with Q = 46 kJ/mol: inside P's family, with a heat that
      falls strongly with loading;
    - **TC:** temperature-dependent capacity, a Sips isotherm with Q = 50 kJ/mol whose
      capacity falls by 0.2 % per K: inside P's family, outside A's. (0.5 % per K was tried
      first, on development materials only; near saturation the truth's heat,
      Q + R T^2 chi q / (dq/ds), then reached 248 kJ/mol inside the scored window.)
  - Gaussian noise of SIGMA_REL = 0.004 q_ref (section 3.5), with a fixed seed per material
    and family.
  - Cells: P, V-pen, A-hard and F-none, with the tuned configurations and 5 seeds, for
    E-high and E-low.
  - **Primary metric (loading-matched):** at each held-out state (p, T) where the model's
    own loading lies in 0.1 to 0.9 q_ref, the model's Qst there against the truth's Qst at
    the same loading and temperature (found by inverting the truth, which is monotone); the
    RMS difference in kJ/mol (`study.qst_error`). This compares Qst(q) curves without
    inverting a possibly non-monotone model.
  - **Secondary metric (state-matched):** the two heats at the observed states whose true
    loading lies in 0.1 to 0.9 q_ref.
  - A task fails (infinite error, ranked worst) if any compared Qst is undefined or not
    finite, if fewer than 3 states fall in the window, or if the truth cannot reach the
    model's loading at that temperature (the inversion does not return the loading to within
    1e-6 q_ref; review T3-12). This favours models whose heat is
    defined everywhere, which is part of what H2 tests.
- **(b) Calorimetry.** It would run if independent calorimetric water heats existed on at
  least 3 materials with multi-temperature isotherms. The search
  (research/lit_3a_calorimetry.md; Claude Science T2, 2026-11-08) found one: MOF-801 (Kim et
  al. 2016, one DSC integral value, 2960 kJ/kg, about 53.3 kJ/mol, over 19 to 20 wt%).
  MIL-101(Cr) (Khan and Mitra 2025) has a directly measured heat but is not verified against
  loading and has no multi-temperature set here; HKUST-1 (Wu and Navrotsky 2016) has a heat
  at 25 C only on a water-unstable sample. **(b) does not run.** A descriptive check uses
  MOF-801 (Kim 2018 isotherms, 7 points per temperature, from the `minpoints7` variant):
  each of P, V-pen, A-hard, F-none and C1 is fitted to all five temperatures, and its Qst(q)
  averaged over 19 to 20 wt% at 30 C (the temperature of the DSC value, K03) is reported against 53.3 kJ/mol. No claim about the heat
  of a real material is made from it (section 9).

### 6.4 Descriptive analyses (no hypothesis; fixed now)

- The temperature invariance of the characteristic curve per material: the spread of A(q)
  across temperatures, against the digitisation error. **Selection check (review E1):** the
  same spread computed from the visible points of the materials excluded by rule 5
  (occlusion; the overlay-gate figures were never digitised), against the included ones,
  only at loadings in 0.2 to 0.8 q_ref where every temperature has visible points, and next
  to the A error that a 0.002 shift in p/p_sat implies (review T3-6, A20-5). Occlusion happens
  where isotherms coincide in p/p_sat, close to where the characteristic curve holds, so
  exclusion may remove materials favourable to A-hard. The check is biased against finding
  this: hidden points are where curves coincide, so removing them raises the measured spread
  of the excluded set. Computed before the freeze from data only (`scripts/sensitivity.py
  aq-spread`, `results/sensitivity_aq_spread.json`): median spread 0.083 kJ/mol over the 13
  included materials and 0.137 kJ/mol over the 10 rule-5 exclusions with at least 2
  temperatures; the A error implied by digitisation is 0.007 to 0.088 kJ/mol per material
  (median of its points), smaller than the material's spread in every case (for example
  0.088 against 0.336 for Mg-SU-102, 0.010 against 0.025 for CALF-25). The excluded
  materials are not shown to be more invariant, but given the bias the concern is not
  refuted; it stays a caveat on H1c.
- Step-position error at the held-out temperature: the error in p/p_sat at half of q at
  p/p_sat = 0.90.
- Subgroups: MOFs against COFs; materials with at least 3 training temperatures. The MOF
  subgroup has 5 materials, for which no exact 95 % Walsh interval exists (P(W+ = 0) = 1/32
  > 0.025), so it gets an estimate only (review A20-7). H1a (descriptive) is reported overall
  and for the materials with at least 3 training temperatures, as the comparison of a rigid
  (van't Hoff) with a free temperature dependence.
- d_m against the distance of the held-out temperature from the nearest training
  temperature (Spearman correlation).
- I-mid results; P against V-none (the pure effect of the constraints at equal structure);
  P against F-rel; P against P-K; the training-loss gap between P and V-none.
- Sensitivity analyses: the inclusion variants of section 3.3; unstable samples removed;
  the paper's own p_sat, including Co2Cl2(BTDD) from its characteristic curves (Fig. S8;
  variant `co2cl2_s8`, review A20-2); **digitisation perturbation:** each digitised isotherm
  shifted in p/p_sat by a random sign times 0.002, the largest measured systematic shift per
  isotherm (0.18 % of the axis; section 3.5), in two perturbed copies of the dataset (seeds 1
  and 2), with the H1 verdicts recomputed on each; verdict stability is reported. (The first
  draft used 0.027, the benchmark's false-detection offset, as a whole-curve shift with an
  independent sign per temperature, which would have created a spurious temperature
  dependence larger than the real one; review T3-5.)
- Failures per cell; the floor of E next to the observed E.

## 7. Hypotheses and tests

### 7.1 Confirmatory comparisons

Holm correction over the four confirmatory H1 tests (H1b to H1e):
- **H1a, temperature structure (descriptive since 2026-11-09):** P against F-hard. It is
  computed with the same estimate, intervals and words, and reported overall and for the
  materials with at least 3 training temperatures, but it is not a confirmatory test. The
  synthetic worlds (section 7.4) showed that it reads "P extrapolates better than F-hard" in
  every world, including one in which van't Hoff is wrong (FW, R = 0.33): with 2 training
  temperatures, which 11 of the 13 materials have, a free temperature dependence cannot be
  identified, so the comparison cannot fail (CORRECTIONS P3A-21).
- **H1b, hard against penalty at equal structure:** P against V-pen. Prediction: P no worse
  (equivalent or better). The accuracy claim for hard constraints rests on H1b only.
- **H1c, learned potential against characteristic curve:** P against A-hard. No direction
  predicted.
- **H1d, against a generic network:** P against F-none. Prediction: P better.
- **H1e, against the classical dual-site Sips:** P against C1. No direction predicted.

Holm correction over the fifteen H2 tests:
- **H2, heat (synthetic, section 6.3a):** P against V-pen, A-hard and F-none, for each of the
  five truth families. No direction predicted.

- **H3, violations:** for each cell, the fraction of its fits (all tasks) that violate by the
  primary rule of section 6.2. Prediction (revised 2026-11-09, P3A-21): penalties leave
  violations that the hard constraints remove, i.e. V-pen reads "violates in some fits" or
  "violates in at least 20 % of fits" (section 8), and P reads "no violations detected". The
  first wording ("at least one of F-none, V-none and V-pen") could not fail, because the
  unconstrained MLP violated in 20 to 26 of 26 fits in every synthetic world; F-none, F-pen,
  F-rel and V-none are reported with the same words, descriptively.

### 7.2 Statistics

- **Unit:** the material (n = 13).
- **Failures:** a fit that fails (E infinite, or an exception) is never dropped. A material
  whose E-high or E-low fit failed has a failed e_m; for each comparison, a failed e_m is set
  to that comparison's worst finite e plus one decade, so it ranks worst. The same failed
  fit can therefore get different values in different comparisons; if both models fail on a
  material, d_m = 0 and the material drops out of the signed-rank test as a zero. Failures
  are counted per cell. The worst finite e of a comparison is taken over both models'
  finite values; if neither has one, every d_m is 0. The material set is every material in
  the run file, and for the confirmatory run it must equal the 13 materials of the frozen
  `data/dataset_summary.json`; all five H2 families must be present. A missing record, a
  duplicated record, a different material set, a missing H2 family, or an error value of
  zero or below (which can only be a bug) stops the analysis. The P-violation check of
  section 6.2 runs before any verdict is computed or written. Descriptive comparisons carry
  the prefix "Descriptive (unadjusted, not a test):" before their words (review T3-8, T3-10,
  T3-11).
- **Test:** the exact two-sided Wilcoxon signed-rank test on d_m: exactly zero differences
  dropped (no tolerance; review T3-13)
  (Wilcoxon's method), mid-ranks for ties (ties are exact equality of |d_m|, without
  rounding), and the null distribution of the signed-rank sum enumerated exactly; the null is
  symmetric, so the two-sided p is P(|W+ - mu| >= |w - mu|) (`analyse.wilcoxon_exact`; it
  does not depend on a library default).
- **Estimate:** the Hodges-Lehmann estimate of d (the median of the n(n+1)/2 Walsh averages,
  i <= j), with exact distribution-free 95 % and 90 % intervals [W_(C+1), W_(M-C)] from the
  sorted Walsh averages, where C is the largest c with P(W+ <= c) <= alpha/2 under the
  signed-rank null without ties for all n materials (zeros included); if no c qualifies the
  interval is unbounded (`analyse.hl_ci_exact`; the interval always contains the estimate).
  A percentile bootstrap interval of HL (10,000 resamples of materials, numpy default_rng
  seed 20261013) is reported as secondary.
- **Ratio:** R = 10^d, P's error relative to X's.
- **Smallest effect of interest:** a 25 % change in error, R = 0.8 or R = 1.25
  (|d| = 0.097).
- Significance uses the Holm-adjusted p; the intervals are not adjusted. Equivalence uses
  the 90 % interval, i.e. two one-sided tests at alpha 0.05 per comparison.
- **H2:** for each truth family and comparison, d_m = mean over E-high and E-low of
  log10 RMSE_Qst(P) - log10 RMSE_Qst(X), with the same failure rule, test, estimate,
  intervals and words, and "estimates the isosteric heat better than" in place of
  "extrapolates better than".
- **H3:** a proportion with a Wilson 95 % interval. Its denominator is the cell's fitted
  models over all tasks; a failed fit has no model to judge, so it is left out of the
  denominator and reported separately (its failure already counts in H1). The primary count
  uses the tolerant "in" counts of `study.violation_counts`.
- These rules were written into the text before the freeze after an independent scorer,
  written from this text alone (Claude Science, `cs_scorer.py`), listed the points the text
  left open (TG1 to TG10); both scorers are run on the development check and the worlds, and
  any disagreement is resolved in the text before the freeze.

### 7.3 Power and minimum detectable effect

The verdict itself is simulated with the frozen analysis code (`scripts/mde.py`, 2000
simulations per setting, seed 20261013) for n = 13, a spread sigma of d_m across materials
in {0.10, 0.15, 0.20, 0.30, 0.50} decades, normal and Student-t (3 df) shapes, at Holm's
strictest step for the four confirmatory H1 tests (alpha 0.0125) and at alpha 0.05.
Reported: the probability of "equivalent within 25 %" when the true d is 0, and the
smallest true effect at which "P extrapolates better than X" is reached with probability
0.80, given as the error ratio R that must hold (`results/mde.json`, computed 2026-11-09;
an independent re-simulation by Claude Science gave P(equivalent | d = 0) = 0.395 at
sigma 0.15, normal, n = 13, against 0.40 here):

| shape | sigma | P(equivalent \| d = 0), alpha 0.0125 | verdict MDE R, alpha 0.0125 | verdict MDE R, alpha 0.05 | test-only MDE R, alpha 0.0125 |
|---|---|---|---|---|---|
| normal | 0.10 | 0.88 | 0.751 | 0.757 | 0.776 |
| normal | 0.15 | 0.40 | 0.682 | 0.725 | 0.684 |
| normal | 0.20 | 0.10 | 0.602 | 0.671 | 0.602 |
| normal | 0.30 | 0.00 | 0.468 | 0.551 | 0.468 |
| normal | 0.50 | 0.00 | 0.282 | 0.370 | 0.282 |
| t3 | 0.10 | 0.93 | 0.759 | 0.770 | 0.796 |
| t3 | 0.15 | 0.71 | 0.707 | 0.750 | 0.710 |
| t3 | 0.20 | 0.39 | 0.634 | 0.719 | 0.634 |
| t3 | 0.30 | 0.08 | 0.505 | 0.624 | 0.505 |
| t3 | 0.50 | 0.00 | 0.320 | 0.457 | 0.320 |

The spread expected in the confirmatory data is, per comparison, the largest of the
development-set estimate (4 materials), the estimates from the synthetic worlds (13
materials each) and 0.15 decades (`results/mde.json`, "spread_estimates"):

| Comparison | Development | Worlds, largest | Spread used | Verdict MDE R (normal, alpha 0.0125) |
|---|---|---|---|---|
| H1b P vs V-pen | 0.106 | 0.081 | 0.15 | 0.68; P(equivalent \| d = 0) 0.40 |
| H1c P vs A-hard | 0.548 | 0.336 | 0.55 | below 0.28 |
| H1d P vs F-none | 0.096 | 0.393 | 0.39 | about 0.37 |
| H1e P vs C1 | 0.098 | 0.161 | 0.16 | about 0.66; P(equivalent \| d = 0) about 0.3 |

Caveats: the worlds have independent noise and no digitisation systematics, so their
spreads may be smaller than the real ones (review T3-16); the simulation has no exact zero
differences, which the failure rule can create when both models fail (T3-17).

**Estimation first, decided now (review T3-2).** The rule written in the first draft (report
estimates when the minimum detectable R is weaker than 0.8 or P(equivalent | d = 0) is below
0.5) is met for every confirmatory comparison by the 0.15 floor alone. The paper therefore
reports, for every H1 comparison, the Hodges-Lehmann ratio R with its exact 95 % and 90 %
intervals as the primary result; the verdict words of section 8 are a secondary layer. A
non-significant comparison reads "Inconclusive at this sample size: the data cannot tell P
and X apart." (the one wording, in section 8 and in `scripts/analyse.py`), never "no
difference". H1b's prediction "P no worse" is judged by non-inferiority: it is met if the
upper exact 95 % bound of R is below 1.25 (`analyse.py`, "H1b_prediction").

### 7.4 Can each verdict fail? (pre-freeze check, `scripts/verdict_worlds.py`)

Before the freeze, the whole pipeline (tuned configurations, fitting with 5 seeds, violation
counts, the analysis code) is run in four synthetic worlds that share no uptake data with the
confirmatory set. Each world has 13 materials; material i uses the temperatures of
confirmatory material i on a 25-point grid in p/p_sat from 0.02 to 0.90, with noise
SIGMA_REL x q_ref. Shapes are drawn from a declared distribution (seed 20261108).
- **KS0:** two-site Sips with van't Hoff affinities (dc = 0), exactly inside P's family.
  Expected: H1c "P extrapolates better than A-hard"; H1b equivalent, differing by less than
  25 %, or P better.
- **DA:** Dubinin-Astakhov, exactly inside A-hard's family. Expected: H1c "A-hard
  extrapolates better than P".
- **FW:** Kirchhoff-Sips with a large heat capacity (dc = 250 J/mol/K), so van't Hoff is
  wrong. Expected: H1a is not "P extrapolates better than F-hard". (With 2 training
  temperatures no model can identify a non-van't-Hoff dependence, so a stronger expectation
  would not be fair; this world tests that H1a does not reward van't Hoff when it is wrong.)
  As the review noted before the run (T3-3), "P better" here could also come from the free
  network's instability rather than from van't Hoff being rewarded; read together with KS0
  (same shapes, van't Hoff exact) it is a paired calibration: F-hard loses by R 0.17 in KS0
  and 0.33 in FW, so the van't Hoff error costs P about a factor of two, but not the
  comparison.
- **FLAT:** one weakly curved Langmuir site. Expected: H1b equivalent or differing by less
  than 25 %; H3: P "no violations detected", and V-pen, V-none and F-none not "at least
  20 %".

- **SUB** (added 2026-11-09 after the first four, P3A-21): a sub-linear Sips isotherm
  (exponent 0.5 to 0.9, a heterogeneous surface) with van't Hoff affinity, outside P's family
  (exponents 1 or at least 1.5) and inside V-pen's. Expected: H1b "V-pen extrapolates better
  than P", which shows that H1b can fail.

A world that misses its expectation stops the freeze until the cause is found and recorded,
and this section is revised.

**Outcomes of the first four worlds** (`results/worlds_check.json`,
`results/verdicts_worlds_*.json`; 13 materials, 5 seeds; computed 2026-11-09):

| Comparison | KS0 | DA | FW | FLAT |
|---|---|---|---|---|
| H1a P vs F-hard | P better (R 0.17) | P better (0.14) | P better (0.33) | P better (0.26) |
| H1b P vs V-pen | equivalent (0.98) | equivalent (0.95) | equivalent (0.97) | equivalent (0.98) |
| H1c P vs A-hard | **P better (0.52)** | **A-hard better (1.26)** | inconclusive (0.95) | P better (0.16) |
| H1d P vs F-none | P better (0.29) | P better (0.30) | inconclusive (0.54) | P better (0.25) |
| H1e P vs C1 | inconclusive (1.15) | inconclusive (0.93) | equivalent (1.01) | equivalent (1.12) |
| H3 P | none | none | none | none |
| H3 V-pen | some (4/26) | none | none | none |
| H3 F-none | often (25/26) | often (20/26) | often (26/26) | often (24/26) |

- Met: KS0 (H1c "P better", H1b equivalent), DA (H1c "A-hard better"), FLAT (H1b, H3 for P,
  V-pen and V-none). H1c discriminates in both directions.
- Missed: FW (H1a read "P better"; expected otherwise) and FLAT (F-none read "at least 20 %";
  expected otherwise). Cause, found from the numbers: the free temperature network cannot
  extrapolate from 2 training temperatures, and the unconstrained MLP violates physics outside
  the data in every world. Consequence: H1a is descriptive and the H3 prediction is restated
  (section 7.1); the FW and FLAT expectations are kept as recorded, unmet.
- H1b read "equivalent" in all four worlds, so the SUB world was added to show it can fail.
  Outcome of SUB: [to be filled when it finishes].
- The two scorers (`scripts/analyse.py` and the independent `cs_scorer.py`) agree on every
  class, p-value, estimate and interval in the development check and the four worlds (210
  comparisons; their class labels differ only in name).

## 8. Verdict words (fixed now)

For each comparison of P with X, the rows are evaluated in order, top to bottom; every
outcome falls in exactly one row, which a brute-force test over more than 10,000 outcome
combinations checks (`tests/test_analysis.py`). "Significant" means a Holm-adjusted p below
0.05. "Inside" means the 90 % interval of R lies within [0.8, 1.25].

| Condition | Words |
|---|---|
| significant, R <= 0.8, upper 95 % bound of R < 1 | "P extrapolates better than X." |
| significant, R >= 1.25, lower 95 % bound of R > 1 | "X extrapolates better than P." |
| significant and inside | "P and X differ, by less than 25 %." |
| not significant and inside | "P and X are equivalent within 25 %." |
| significant, none of the above | "P and X differ; the size of the difference is uncertain." |
| none of the above | "Inconclusive at this sample size: the data cannot tell P and X apart." |

For H2 the same rows apply, with "estimates the isosteric heat better than" in place of
"extrapolates better than".

For H3, per cell, with k violating fits of n and the Wilson 95 % interval [lo, hi]; rows in
order (exhaustive; brute-force test over n up to 60):

| Condition | Words |
|---|---|
| lo >= 0.20 | "X violates in at least 20 % of fits (k/n)." |
| k = 0 | "No violations detected for X (0/n; upper 95 % bound hi, two decimals)." |
| hi < 0.20 | "X violates in fewer than 20 % of fits (k/n)." |
| otherwise | "X violates in some fits (k/n); whether the rate reaches 20 % is uncertain." |

Program-level summary sentences, chosen by rule from the classes of the four confirmatory
H1 tests; all that apply are reported, and the brute-force test over all 1296 combinations
checks that no two contradict (the sentences that used H1a were removed with it, P3A-21):
- H1b "P better", "equivalent" or "differ by less than 25 %": "The hard constraints give
  admissibility at no accuracy cost larger than 25 %."
- H1b "V-pen better": "The hard constraints cost accuracy."
- H1c "A-hard better": "The temperature-invariant characteristic curve extrapolates better
  than the learned potential."
- H1e "C1 better": "A dual-site Sips model with van't Hoff affinities extrapolates better
  than the learned potential."
- H1c, H1d and H1e all "P better": "The learned potential extrapolates better than the
  characteristic curve, the dual-site Sips model and a generic network."
- None of these: "No program-level sentence applies; each comparison is reported on its
  own."

## 9. What is not claimed

- The Henry limit cannot be tested on these data, because no isotherm reaches the Henry
  regime (Mg-SU-102 already holds about 0.08 g/g at 20 Pa). P2 is a property of the model,
  not a validated prediction, and no claim is made about how well the penalties enforce it.
- P4 (sign-correct LDF kinetics) is proved and unit-tested, not tested on data.
- An equilibrium potential represents one branch. Hysteresis and framework breathing are
  outside its scope.
- Without calorimetry (section 6.3b), no claim is made that any model's Qst is closer to the
  true heat of a real material.

## 10. Freeze mechanics and deviations

- `python scripts/run_confirmatory.py --prepare-freeze` writes `requirements-lock.txt`
  (Python and the exact versions of torch, numpy, scipy, pandas, PyMuPDF and Pillow),
  converts every frozen file to LF without a byte-order mark, marks them `-text` in
  `.gitattributes`, and writes `FREEZE_MANIFEST.json`: the SHA-256 of 45 files (this file;
  the lock; the tuned configurations; the power and world results; the dataset, which stays
  local, its inclusion log, its summary, the gate log and the digitisation validation log; every module and script that
  digitises, gates, builds, fits, scores or runs a declared descriptive analysis, including `run_confirmatory.py` itself, hashed with its
  manifest line blanked) and the environment.
- The manifest's hash is written into `run_confirmatory.py`. That script and
  `run_synthetic_h2.py` refuse to run if any frozen file or the installed versions differ.
- The freeze commit is tagged `prereg-p3a-freeze` and pushed to the public repository before
  the first confirmatory fit, so its date is public.
- Any later change is an amendment with a date and reason, recorded in section 11 and in
  CORRECTIONS_P3A.md. Deviations found after confirmatory runs are reported as deviations,
  never edited away. If the scorer and this text disagree, this text governs, and the
  discrepancy is reported.

## 11. Amendments

None yet.

## 12. Revisions before the freeze (2026-11-08)

An adversarial review of the draft at f0c98d4 (Claude Science, `REVIEW_cs.md`) found ten
blocking points. Changes, with the review item:
- the fit scale no longer includes the held-out isotherm (A3; P3A-10); tuning rerun;
- a failed task is a failure, never averaged away (A1; P3A-11);
- every scorer exists and is frozen: H2, H3 words, summary sentences (A2; P3A-16);
- P against C1 is confirmatory (H1e); P against V-none is descriptive (B1);
- the twins share P's or A-hard's tuned structure; penalties tune lambda inside it; budgets
  matched (B3, B5; P3A-13); F-rel and weight decay added (B4);
- H3 with a tolerance, a domain and four word classes (C1; P3A-14); scale-free Henry
  penalty (C2; P3A-12);
- power simulated on the verdict itself, with the rule for reporting estimates (D1); exact
  tests and intervals (D2); the failure rule stated in full (D3); "evaluated in order" (D4);
- selection checks: A(q) spread of excluded materials (E1), inclusion variants (E2),
  per-series colour gate (E3; P3A-17), more real figures with numeric truth and a
  digitisation-perturbation sensitivity analysis (E4), which found a vector-digitiser defect
  (P3A-18, no effect on the data) and a too optimistic error model (P3A-19: SIGMA_REL 0.004,
  H3 tolerance 0.02 q_ref);
- the heat metric is loading-matched, with two further truth families (F1, F2; P3A-15);
- four synthetic worlds with expectations fixed in advance (G1);
- a complete manifest with an environment lock and `.gitattributes` (H1);
- a COF in the development set (I1); extrapolation distance and subgroups (I2); text fixes
  (A4, B2, I3, I4).
