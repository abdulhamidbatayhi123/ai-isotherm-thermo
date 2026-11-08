# Pre-registration, Paper 3A (DRAFT, not frozen)

**Status: DRAFT for the author's review, revised 2026-11-08 after an adversarial review
(`REVIEW_cs.md` in the AgentHub, at commit f0c98d4; the changes are listed in section 12 and in
CORRECTIONS_P3A.md P3A-10 to P3A-17). Nothing in this file binds until the freeze commit
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
  2026-11-08 before any fit, so that the development set contains a COF (8 of the 14
  confirmatory materials are COFs). It was excluded from the confirmatory set by rule 2 alone
  (7 points at 288.15 K); rule 2 is relaxed to 5 points in the development set, which is
  never scored. Rules 1, 3, 4 and 5 apply.
- CAU-10-H (Frohlich et al. 2014) keeps only 2 usable temperatures (rule 5 at 298 K) and is
  excluded.

CuBTC degrades in water over repeated cycles; its isotherms are used only to choose
hyperparameters, never to judge a model.

### 3.2 Confirmatory set

**Applied 2026-11-03, all before any fit (`data/inclusion_log.csv`,
`data/digitisation_gate_log.csv`).** The confirmatory set is **14 materials, 6 MOFs and 8
COFs**:
- MOFs: Mg-SU-102 (9 temperatures, numeric source data), Co2Cl2(BTDD), KMF-1, Al-fumarate,
  CALF-25, Zn2(bptc) (4 temperatures).
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

Rules 1, 2 and 5 are applied per temperature: an isotherm that fails is dropped, and the
material stays if 3 or more temperatures remain.

Rule 5 needed three versions, each judged only on the digitised data, before any fit (P3A-8).
Its second version was revised after it excluded COF-432 at 25 C, so the rule was not blind
to material identity. A descriptive sensitivity analysis (section 6.4) therefore repeats the
H1 comparisons on every material whose membership changes under the earlier versions and
under a 7-point rule 2 (`build_dataset.py --variant rule5_v1 | rule5_v2 | rule5_none |
minpoints7`). Membership under each, computed 2026-11-08 without any model: 6, 10, 24 and 15
materials respectively (14 under the final rules).

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
  - Further real figures with published numeric values (`scripts/digitisation_validation.py`,
    `logs/digitisation_validation.json`), in both axes, with the mean signed error per
    isotherm (a systematic shift): [to be filled from the log before the freeze].
  - The synthetic benchmark (`scripts/raster_benchmark.py`, `logs/raster_benchmark.log`):
    worst case recall 0.80 of visible markers (0.56 to 0.58 of all markers in the densest
    figures, where markers are hidden), at most 11 false detections in a figure, each within
    about 2.7 % of the axis of the curve (the desorption offset, P3A-7); curve error at most
    0.64 % RMS and 2.7 % maximum of the axis.
  - The synthetic noise of sections 6.3a and 7.4 is SIGMA_REL = 0.002 q_ref (Gaussian, in
    uptake only), the raster RMS rounded up. ISODB sets digitised by NIST (CALF-25,
    Zn2(bptc), the development set) have an unknown digitisation error.
  - The floor of E set by digitisation is about 0.002 (log10 E about -2.7); it is reported
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
- The chosen configurations, written to `results/dev_best_configs.json` (frozen): [to be
  filled from the file before the freeze].
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
  "in" domain, any isotherm of G (fixed T) falls by more than 0.01 q_ref below its running
  maximum as p increases, or any point has q < -0.01 q_ref (`study.violation_counts`,
  `study.violates`). The tolerance is five times the synthetic noise level and above the
  measured digitisation error.
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
  - Gaussian noise of SIGMA_REL = 0.002 q_ref, with a fixed seed per material and family.
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
    finite, or if fewer than 3 states fall in the window. This favours models whose heat is
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
  averaged over 19 to 20 wt% at 25 C is reported against 53.3 kJ/mol. No claim about the heat
  of a real material is made from it (section 9).

### 6.4 Descriptive analyses (no hypothesis; fixed now)

- The temperature invariance of the characteristic curve per material: the spread of A(q)
  across temperatures, against the digitisation error. **Selection check (review E1):** the
  same spread computed from the visible points of the materials excluded by rule 5 or the
  overlay gate, against the included ones. Occlusion happens where isotherms coincide in
  p/p_sat, which is close to where the characteristic curve holds, so exclusion may remove
  materials favourable to A-hard; the direction is reported with H1c. Computed before the
  freeze from data only (`scripts/sensitivity.py aq-spread`,
  `results/sensitivity_aq_spread.json`): the mean spread of A(q) over 0.2 to 0.8 q_ref has a
  median of 0.091 kJ/mol over the 14 included materials and 0.137 kJ/mol over the 12 excluded
  confirmatory candidates with at least 2 temperatures, so the excluded materials are not more
  temperature-invariant than the included ones. Caveat: the excluded materials' spreads come
  from their visible points only.
- Step-position error at the held-out temperature: the error in p/p_sat at half of q at
  p/p_sat = 0.90.
- Subgroups: MOFs against COFs; materials with at least 3 training temperatures.
- d_m against the distance of the held-out temperature from the nearest training
  temperature (Spearman correlation).
- I-mid results; P against V-none (the pure effect of the constraints at equal structure);
  P against F-rel; P against P-K; the training-loss gap between P and V-none.
- Sensitivity analyses: the inclusion variants of section 3.3; unstable samples removed;
  the paper's own p_sat; **digitisation perturbation:** each digitised isotherm shifted in
  p/p_sat by a random sign times 0.027 (the benchmark's largest systematic offset), two
  perturbed copies of the dataset (seeds 1 and 2), and the H1 verdicts recomputed on each;
  verdict stability is reported.
- Failures per cell; the floor of E next to the observed E.

## 7. Hypotheses and tests

### 7.1 Confirmatory comparisons

Holm correction over the five H1 tests:
- **H1a, temperature structure:** P against F-hard. Prediction: P better.
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
  primary rule of section 6.2. Prediction: at least one of F-none, V-none and V-pen reads
  "violates in at least 20 % of fits" (section 8), and P reads "no violations detected".

### 7.2 Statistics

- **Unit:** the material (n = 14).
- **Failures:** a fit that fails (E infinite, or an exception) is never dropped. A material
  whose E-high or E-low fit failed has a failed e_m; for each comparison, a failed e_m is set
  to that comparison's worst finite e plus one decade, so it ranks worst. The same failed
  fit can therefore get different values in different comparisons; if both models fail on a
  material, d_m = 0 and the material drops out of the signed-rank test as a zero. Failures
  are counted per cell. A missing record stops the analysis.
- **Test:** the exact two-sided Wilcoxon signed-rank test on d_m: zero differences dropped
  (Wilcoxon's method), mid-ranks for ties, and the null distribution enumerated exactly
  (`analyse.wilcoxon_exact`; it does not depend on a library default).
- **Estimate:** the Hodges-Lehmann estimate of d, with exact distribution-free 95 % and 90 %
  intervals from the order statistics of the Walsh averages (`analyse.hl_ci_exact`; the
  interval always contains the estimate). A bootstrap interval (10,000 resamples, seed
  20261013) is reported as secondary.
- **Ratio:** R = 10^d, P's error relative to X's.
- **Smallest effect of interest:** a 25 % change in error, R = 0.8 or R = 1.25
  (|d| = 0.097).
- Significance uses the Holm-adjusted p; the intervals are not adjusted. Equivalence uses
  the 90 % interval, i.e. two one-sided tests at alpha 0.05 per comparison.
- **H2:** for each truth family and comparison, d_m = mean over E-high and E-low of
  log10 RMSE_Qst(P) - log10 RMSE_Qst(X), with the same failure rule, test, estimate,
  intervals and words, and "estimates the isosteric heat better than" in place of
  "extrapolates better than".
- **H3:** a proportion with a Wilson 95 % interval.

### 7.3 Power and minimum detectable effect

The verdict itself is simulated with the frozen analysis code (`scripts/mde.py`, 2000
simulations per setting, seed 20261013) for n = 14, a spread sigma of d_m across materials
in {0.10, 0.15, 0.20, 0.30, 0.50} decades, normal and Student-t (3 df) shapes, at Holm's
strictest step (alpha 0.01) and at alpha 0.05. Reported: the probability of "equivalent
within 25 %" when the true d is 0, and the smallest true effect at which "P extrapolates
better than X" is reached with probability 0.80. Results (`results/mde.json`): [to be filled
before the freeze].

The spread expected in the confirmatory data is the largest of the development-set
estimate, the synthetic-world estimates (section 7.4) and 0.15 decades. Because "P better"
also requires R <= 0.8 and a 95 % interval below 1, the verdict needs a true R well below
0.8 even when the test alone has power; and "equivalent" becomes unreachable as sigma grows.
Therefore: wherever the expected spread makes the minimum detectable R weaker than 0.8, or
P(equivalent | d = 0) below 0.5, the paper reports the estimate and its interval as the
result, and a non-significant comparison is worded "inconclusive at this sample size",
never "no difference".

### 7.4 Can each verdict fail? (pre-freeze check, `scripts/verdict_worlds.py`)

Before the freeze, the whole pipeline (tuned configurations, fitting with 5 seeds, violation
counts, the analysis code) is run in four synthetic worlds that share no uptake data with the
confirmatory set. Each world has 14 materials; material i uses the temperatures of
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
- **FLAT:** one weakly curved Langmuir site. Expected: H1b equivalent or differing by less
  than 25 %; H3: P "no violations detected", and V-pen, V-none and F-none not "at least
  20 %".

Outcomes (`results/worlds_check.json`): [to be filled before the freeze]. A world that misses
its expectation stops the freeze until the cause is found and recorded, and this section is
revised.

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
| none of the above | "Inconclusive: the data cannot tell P and X apart." |

For H2 the same rows apply, with "estimates the isosteric heat better than" in place of
"extrapolates better than".

For H3, per cell, with k violating fits of n and the Wilson 95 % interval [lo, hi]; rows in
order (exhaustive; brute-force test over n up to 60):

| Condition | Words |
|---|---|
| lo >= 0.20 | "X violates in at least 20 % of fits (k/n)." |
| k = 0 | "No violations detected for X (0/n; upper 95 % bound hi)." |
| hi < 0.20 | "X violates in fewer than 20 % of fits (k/n)." |
| otherwise | "X violates in some fits (k/n); whether the rate reaches 20 % is uncertain." |

Program-level summary sentences, chosen by rule from the H1 classes; all that apply are
reported, and the brute-force test over all 7776 combinations checks that no two contradict:
- H1a "P better" and H1b "P better", "equivalent" or "differ by less than 25 %": "The
  temperature structure carries the accuracy, and the hard constraints give admissibility at
  no accuracy cost larger than 25 %."
- H1a "F-hard better": "A free temperature dependence extrapolates better than the van't Hoff
  structure."
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
  `.gitattributes`, and writes `FREEZE_MANIFEST.json`: the SHA-256 of 32 files (this file;
  the lock; the tuned configurations; the power and world results; the dataset, which stays
  local, its inclusion log, its summary and the gate log; every module and script that
  digitises, builds, fits or scores, including `run_confirmatory.py` itself, hashed with its
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
  digitisation-perturbation sensitivity analysis (E4);
- the heat metric is loading-matched, with two further truth families (F1, F2; P3A-15);
- four synthetic worlds with expectations fixed in advance (G1);
- a complete manifest with an environment lock and `.gitattributes` (H1);
- a COF in the development set (I1); extrapolation distance and subgroups (I2); text fixes
  (A4, B2, I3, I4).
