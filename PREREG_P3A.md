# Pre-registration, Paper 3A (DRAFT, not frozen)

**Status: DRAFT for the author's review, 2026-10-13. Nothing in this file binds until the
freeze commit "FREEZE PREREG_P3A". No confirmatory fit has been run. The development set
(section 3.1) may be used before the freeze to set the hyperparameters listed in section 5.4
and the minimum detectable effects in section 7.3. Those are the only uses allowed.**

Title (working): *Does a thermodynamically consistent learned potential extrapolate water
isotherms of MOFs and COFs in temperature? A pre-registered test against penalty,
unconstrained and classical models.*

## 1. Question

A model can learn one adsorbed-phase potential, the reduced grand potential (or spreading
pressure) psi(ln p, T), and obtain the water isotherm q*(p, T) and the isosteric heat Qst
from its derivatives. Then monotonicity in pressure, the Henry limit and
Clausius-Clapeyron consistency between the isotherm and the heat hold for every parameter
value. Does this, combined with a thermodynamic temperature dependence, predict water
uptake at temperatures outside the training range better than:
- the same functional form without the constraints;
- the same form with the constraints as loss penalties;
- a generic neural network;
- the classical models, including the temperature-invariant characteristic curve?

A result in which a classical model wins, or in which the hard constraints buy admissibility
but no accuracy, is a pre-declared outcome with its own words (section 8). It will be
reported as prominently as any other.

## 2. Background facts this design rests on (sources in `research/`)

- No published model learns such a potential for adsorption with hard constraints.
  Penalty versions exist and leave violations (lit_3a_ml.md, gap statement). The search
  has stated blind spots: ChemRxiv indexing, and one closed paper (Liu et al. 2023) still
  unread in full.
- The temperature-invariant Dubinin-Polanyi characteristic curve is the field default for
  water in MOFs. Its invariance is usually asserted visually, without an error number
  (lit_3a_classical.md, competitors).
- A synthetic diagnostic showed that convexity and the Henry limit alone do not make
  temperature extrapolation work. The temperature structure does (CORRECTIONS_P3A.md,
  P3A-2). The design therefore separates the two (section 4).
- No candidate data set has an independently measured water heat that has been verified
  so far. Every literature Qst is derived from the same isotherms (data/INVENTORY.md
  section 7). A dedicated calorimetry search found a verified calorimetric water heat for
  one usable MOF only, MOF-801, and none for any COF (research/lit_3a_calorimetry.md;
  consequences in section 6.3).

## 3. Data

### 3.1 Development set (tuning only, never confirmatory)

These come from ISODB, as digitised by NIST:
- CuBTC (HKUST-1) and MIL-100, Rezk et al. 2012 (9 temperatures, 293 to 358 K);
- CAU-10-H, Frohlich et al. 2014 (298, 313, 333 K);
- MIL-160, Cadiau et al. 2015 (293, 303, 313 K).

They are chosen because their provenance is documented and they are not needed for the
confirmatory comparison. If Rezk's duplicate curves per temperature cannot be resolved
into one adsorption branch, the material is dropped and the drop is recorded.

**Applied 2026-11-03 (`data/inclusion_log.csv`):**
- Rezk's records come as two series from different figures: one at 9 temperatures on a
  common pressure grid (ISODB records 26 to 43) and one at 5 temperatures. The 9-temperature
  series is used.
- CAU-10-H keeps only 2 usable temperatures (rule 5 at 298 K: a gap of 0.30 in p/psat), so
  it is excluded.
- The development set is CuBTC, MIL-100 and MIL-160.

### 3.2 Confirmatory set

**MOFs:**
- Mg-SU-102 (numeric source data, 9 temperatures, 15 to 55 C);
- MOF-303 (Hanikel 2019; 10, 25, 35, 50 C);
- MOF-801 (Kim 2018; 15, 25, 45, 65, 85 C);
- KMF-1 (20, 30, 40 C);
- CAU-23 (25, 40, 60 C);
- Co2Cl2(BTDD) (283, 293, 298 K);
- MIL-160(Al) (Silva 2021, ISODB; 303, 323, 343 K).

**COFs** (a class absent from the development set):
- COF-432 (10, 25, 40 C);
- COF-309 and HCOF-2 (25, 35, 45 C);
- AB-COF, COF-480-hydrazide, Py-COF-2D and COF-482-hydrazide (Nguyen 2022; 15, 25, 35 C);
- PI-3-COF and NO-PI-3-COF (15, 25, 35 C);
- the seven COFs of Tan et al. 2021 (283.15, 288.15, 298.15 K).

DOIs, licences and figure locations are listed in data/INVENTORY.md.

**Applied 2026-11-03 (`data/inclusion_log.csv`, `data/digitisation_gate_log.csv`; all before
any fit).** Candidates added before any fit: CALF-25 (Taylor et al. 2012) and Zn2(bptc)
(Lin et al. 2006), both rigid MOFs in ISODB; Al-fumarate (Hanikel et al. 2019, SI Fig. S19);
COF-SO3H (Schweng et al. 2024); COF-TP-43 (Abdulhalim et al. 2025). The confirmatory set
that results is **14 materials, 6 MOFs and 8 COFs**:
- MOFs: Mg-SU-102 (9 temperatures, numeric), Co2Cl2(BTDD), KMF-1, Al-fumarate, CALF-25,
  Zn2(bptc) (4 temperatures).
- COFs: COF-432, COF-482-hydrazide, PI-3-COF, NO-PI-3-COF, COF-SO3H, HFPTP-PDA-COF,
  HFPTP-DMePDA-COF, TFBCz-PDA-COF.

Excluded, with the rule that decided it:
- MOF-303 (S17), AB-COF, COF-480-hydrazide, Py-COF-2D, HCOF-2, COF-309, COF-TP-43,
  HFPTP-BPDA-COF, TTA-TFB-COF and TPB-DMTP-COF: rule 5. Markers covered by other series
  leave fewer than 3 usable temperatures.
- MOF-801 (Kim 2018) and TFPPy-PDA-COF: rule 2, 7 points per isotherm.
- MIL-160(Al) (Silva 2021): rules 1 and 2.
- MOF-801 and MOF-303 (Fathieh 2018): the colour gate (section 3.5).
- CAU-23: the overlay gate. The 502 x 409 px panel shows open markers covering most of the
  filled ones.
- Ni2X2(BTDD): rule 4.
- Some materials keep 3 of 4 temperatures because one isotherm fails rule 5 (Al-fumarate:
  25 C; CALF-25: 303 K). Their tasks use the remaining temperatures.

Six of the excluded materials (MOF-303, AB-COF, COF-480-hydrazide, Py-COF-2D, HCOF-2,
COF-309) are lost only to digitisation. Numeric data from their authors would restore them.
Any such data arriving after the freeze enter a descriptive extension, never the
confirmatory set.

### 3.3 Inclusion rules (applied before any model is fitted to the material)

A material and paper pair is included if all of the following hold. Each exclusion is
recorded with its reason in `data/inclusion_log.csv`.
1. There are adsorption-branch isotherms at 3 or more temperatures on the same sample.
2. Each isotherm has at least 8 points with 0 < p/p_sat <= 0.90.
3. The figure passes the digitisation quality gate (section 3.5).
4. The temperatures are unambiguous. A conflict between the main text and the SI (as for
   Ni2X2(BTDD)) excludes the set unless it can be resolved from the source.
5. Coverage (added 2026-11-03, before any fit, after the digitiser showed that markers
   covered by others can leave an isotherm with only its step; CORRECTIONS P3A-8). On the
   curve as published (before the 0.90 cut):
   - no gap between consecutive points is larger than 0.25 in p/psat (this catches a
     hidden plateau); and
   - the curve's start is present: the first point is at p/psat <= 0.10 or at an uptake
     of at most 0.10 q_ref.
   A gap in uptake is not a criterion, because steep steps are physical.

Rules 1, 2 and 5 are applied per temperature: an isotherm that fails is dropped, and the
material stays if 3 or more temperatures remain. Every decision is written by
`scripts/build_dataset.py` to `data/inclusion_log.csv`.

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
- q_ref for a material is its largest uptake with p/p_sat <= 0.90, over all temperatures.

### 3.5 Digitisation (before any fit; blind to model outputs)

- **Vector figures:** path coordinates are extracted from the PDF with PyMuPDF and mapped
  through the axis ticks. The error is the plotting precision.
- **Raster figures** (as implemented in `src/p3a/digitise.py` and `scripts/digitise_sources.py`):
  - **Image:** the embedded image is read at its native resolution. A soft mask, if
    present, is composited onto white.
  - **Axes:**
    - The frame lines are located near positions read from a grid image
      (`scripts/raster_inspect.py`).
    - Each tick read by eye is snapped to the tick mark. The mark is centred between its
      edges, beyond the frame line's local thickness band, on the side the axis's ticks
      share by majority, nearest to the reading.
    - The axis map is a least-squares line through the snapped ticks.
  - **Markers:** template matching with the figure's own marker footprint, cut from the
    legend marker (or from an isolated data marker where the panel has no legend). A
    detection needs a fill fraction of at least 0.6 of the template in the series colour
    (tolerance 0.18) and no white in the template's core. A detection centred on an open
    marker of the same colour (desorption) is vetoed. No physical prior is used to filter
    points.
  - **Outputs:** the script, the calibration points and an overlay image of every detection
    are kept. Point lists from closed or ND-licensed sources stay local. Their fitted
    parameters and predictions are published.
- **Vector figures** (PyMuPDF drawing commands): markers are read by colour, size and
  shape. Series are assigned from the legend's colours. Axes are calibrated from text tick
  labels snapped to tick marks, or, without tick marks, from labels of the modal text
  length.
- **Measured digitisation error** (`scripts/digitisation_error.py`, `logs/digitisation_error.json`).
  Mg-SU-102 Fig. 4a against its numeric source data:
  - Vector extraction recovers 198 of 198 points, with RMS errors of 1e-5 g/g and 0.005 mbar.
  - Raster at 150, 300 and 600 dpi has recall 0.90, 0.94 and 0.94, no false detections, and
    RMS uptake errors of 0.00063, 0.00040 and 0.00035 g/g (0.16, 0.10 and 0.09 % of the axis).
  - The synthetic benchmark (`scripts/raster_benchmark.py`, `logs/raster_benchmark.log`)
    covers sparse and dense figures; circle, square and triangle markers; 800 and 1400 px.
    Its worst case is recall 0.80 of visible markers, at most 11 false detections in a
    figure, and a curve error of at most 0.64 % RMS and 2.7 % maximum of the axis.
  - The error model for the synthetic noise in section 6.3a is SIGMA_REL = 0.002 q_ref,
    the raster RMS rounded up.
- **Quality gates**, any failure excluding the set:
  - axis-calibration residual below 0.5 % of the tick span (all raster figures pass; the
    largest is 0.35 %);
  - every pair of series colours at least 0.36 apart, twice the colour tolerance
    (`scripts/check_colour_separability.py`);
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
- Within the V and A columns, the "none" and "penalty" models have exactly P's or
  A-hard's functional form and initial function. Only the constraints differ, so these
  comparisons isolate the constraints.
- In the F column the architectures differ, because a free MLP has no constrained twin.
  This is stated wherever F is compared.

Other models:
- **C1 (classical reference):** dual-site Sips with van't Hoff affinities and free
  exponents (`MultiSiteSips(n_sites=2)`), as used in practice.
- **P-K (secondary):** `t_mode="kirchhoff"`. It is fitted only where at least 4 training
  temperatures exist, because the heat-capacity term is not identifiable from 2.

**Penalties.** These are `monotonicity_penalty` and `henry_penalty` (A-pen: monotonicity
only, because the characteristic curve has no Henry limit). They are evaluated on
unlabelled collocation points. The s grid runs from ln(1 Pa) to ln(0.9 p_sat(T)), 60
points. The T grid runs from T_min - 15 K to T_max + 15 K of the material, 9 levels, so
it includes the held-out temperature. Giving penalties points at the target temperature
gives the penalty approach its best chance.

## 5. Fitting

### 5.1 Tasks

For a material with temperatures T_1 < ... < T_k:
- **E-high:** train on T_1..T_{k-1}, predict T_k.
- **E-low:** train on T_2..T_k, predict T_1.
- **I-mid** (secondary): for k >= 3, hold out the middle temperature, or for even k the
  lower of the two middle ones.

### 5.2 Loss and optimiser

- Loss: the mean squared error of q / q_ref on the training points. Penalty models add
  lambda x penalty.
- Optimiser: Adam (lr 1e-2) for N_adam steps, then L-BFGS with strong-Wolfe line search for
  N_lbfgs iterations, in float64 on the CPU (`p3a.fit.fit`).

### 5.3 Seeds and selection

- Each model, material and task is fitted from 5 seeds.
- The reported fit is the seed with the lowest training loss. The held-out error is never
  used for selection.
- The seed spread of the held-out error is reported.
- A check in code requires the 5 initial parameter vectors to differ (CORRECTIONS P3A-3).

### 5.4 Hyperparameters, set on the development set only, then frozen

- Number of terms: n_henry in {1, 2}, n_coop in {2, 4, 6} for the V models. n_terms in
  {3, 4, 6} for the A models. Hidden width {16, 32} and depth {2} for the MLP. Hidden
  {8, 16} for F-hard.
- lambda for penalty models in {0.01, 0.1, 1, 10, 100}.
- N_adam in {2000, 4000}, N_lbfgs = 300.
- Matched tuning budget: each model tries exactly 6 configurations, drawn uniformly
  without replacement from its own grid with seed 20261013, or all of them if its grid has
  6 or fewer. A model whose grid has fewer than 6 configurations is not topped up.
- Rule: for each model, the configuration with the lowest mean development-set e (section
  6.1) over the E-high and E-low tasks. Parameter counts are reported.
- Implementation: `scripts/run_dev.py`. The grids are listed there (GRIDS), F-hard also
  varies n_henry and n_coop, and C1 varies only N_adam. Tuning fits use 3 seeds (0 to 2),
  where confirmatory fits use 5. A failed tuning fit scores as the worst observed log10 E
  plus one decade. The chosen configurations are written to `results/dev_best_configs.json`,
  whose SHA-256 is frozen with this file.
- Every cell's scaling is set from its own training data, identically for all cells: ln p
  is centred on its mean and scaled by its standard deviation (at least 0.5), and uptake is
  scaled by q_ref (`p3a.study.fit_cell`).

## 6. Outcomes

### 6.1 Primary outcome: temperature extrapolation error

- E = RMSE(q_pred - q_obs) / q_ref over the held-out isotherm's points.
- For each material m and model X: e_m(X) = mean of log10 E over the tasks E-high and E-low.
- For a comparison between P and X: d_m = e_m(P) - e_m(X). A negative d_m means P is better.

### 6.2 Physical violations

- Dense grid G for each material: s from ln(1 Pa) to ln(0.95 p_sat(T)), 400 points; T from
  T_min - 20 K to T_max + 20 K in 2.5 K steps.
- Counts per fitted model, on G (`p3a.thermo.violations`):
  - points with dq/ds < 0;
  - points with q < 0;
  - points with an undefined Qst;
  - points with Qst outside 0 to 150 kJ/mol.
- A fit "violates" if any count is above zero.
- P must show zero on the first three by construction. A non-zero count for P is a bug,
  is reported as such, and halts the analysis until fixed.

### 6.3 Isosteric heat (choice fixed now; which branch runs depends on data)

- **(a) Synthetic benchmark with known heats.** This always runs.
  - Three truth families:
    - multi-site Kirchhoff-Sips, which is inside P's family;
    - Dubinin-Astakhov, which is inside A's;
    - Fowler-Guggenheim with lateral attraction, which is inside neither.
  - Each truth is sampled on every confirmatory material's own temperatures and pressure
    grid. The truth parameters are chosen so that the step position and capacity match
    that material's measured isotherm at its middle temperature, by a fixed fitting
    script.
  - Gaussian noise is added, with the measured digitisation error as its standard
    deviation (section 3.5).
  - The same E-high and E-low fits are run.
  - Metric: RMSE of Qst(q) against the exact Qst, in kJ/mol, over loadings from 0.1 to
    0.9 q_ref at the held-out temperature.
  - Implementation (`scripts/run_synthetic_h2.py`), fixed now:
    - **KS truth:** a Langmuir site (Q0 = 55 kJ/mol, dc = 0) plus a cooperative Sips site
      (Q0 = 48 kJ/mol, dc = 40 J/mol/K, exponent at least 1.5).
    - **DA truth:** q = W0 exp(-(A/E)^n), with n from 1 to 6.
    - **FG truth:** Q0 = 45 kJ/mol, lateral attraction w between 0 and 3.9 R T_min.
    - **Truth fitting:** only shape parameters are fitted, by bounded least squares on
      q / q_ref, to the middle-temperature isotherm.
    - **Noise:** SIGMA_REL = 0.002 q_ref, with a fixed seed per material and family.
    - **Cells:** P, V-pen, A-hard and F-none, with the tuned configurations and 5 seeds.
  - The heat is compared at the held-out isotherm's own (p, T) states whose true loading
    lies in 0.1 to 0.9 q_ref (`p3a.study.qst_error`). It is not compared at a loading found
    by inverting each model, because a non-monotone model has no unique inverse; comparing
    at observed states treats every cell alike.
- **(b) Calorimetry.** Runs if research/lit_3a_calorimetry.md finds independent calorimetric
  water heats on the same material for at least 3 materials with multi-temperature
  isotherms. Then: RMSE of Qst(q) from each model against the calorimetric heat over the
  measured loading range. Otherwise (b) is not run, and only a descriptive comparison with
  the papers' isotherm-derived Qst is given, labelled as such.
  **Search result (2026-10-13, research/lit_3a_calorimetry.md):**
  - **(b) does not run.** Only MOF-801 has a verified calorimetric water heat with
    multi-temperature isotherms on the same material.
  - **MOF-801** (Kim et al. 2016, Sci. Rep.): one DSC/TGA integral value, 2960 kJ/kg
    (about 53.3 kJ/mol) over 19 to 20 wt%. It becomes a descriptive check: each model's
    Qst(q), averaged over the same loading window.
  - **MIL-101(Cr)** (Khan and Mitra 2025) may have heat against loading, but is unread
    (publisher 403). It is not in the confirmatory set.
  - **HKUST-1** (Wu and Navrotsky 2016) has heat at 25 C only, on a water-unstable
    sample. It is mentioned, not used.
  - **No COF** has a calorimetric water heat.
  - **Update 2026-11-03:** MOF-801 left the dataset (section 3.2: Kim 2018 fails rule 2,
    and Fathieh 2018 fails the colour gate). So even the descriptive MOF-801 check cannot
    run. No claim about the heat of a real material is made (section 9).

### 6.4 Descriptive analyses (no hypothesis)

- The temperature invariance of the characteristic curve per material: the spread of A(q)
  across temperatures, against the digitisation error.
- Step-position error at the held-out temperature: the error in p/p_sat at half of q at
  p/p_sat = 0.90.
- Subgroups: MOFs against COFs.
- I-mid results.
- P-K against P.
- Sensitivity analyses: unstable samples removed; the paper's own p_sat.

## 7. Hypotheses and tests

### 7.1 Confirmatory comparisons (Holm correction over the four H1 tests)

- **H1a, temperature structure:** P against F-hard. Prediction: P better.
- **H1b, hard against penalty at equal structure:** P against V-pen. Prediction: P no worse
  (equivalent or better).
- **H1c, learned potential against characteristic curve:** P against A-hard. No direction
  predicted.
- **H1d, against a generic network:** P against F-none (MLP). Prediction: P better.
- **H2, heat (synthetic, section 6.3a):** P against V-pen, A-hard and F-none, per truth
  family. No direction predicted. Holm correction over these 9 tests.
- **H3, violations:** for each non-hard model, the fraction of material-task fits that
  violate (section 6.2). Prediction: at least one of F-none, V-none and V-pen violates in
  20 % or more of fits; P in none.

### 7.2 Statistics

- **Unit:** the material (n = 14 confirmatory materials; section 3.2).
- **Failures:** a fit that fails (E infinite, or an exception) is never dropped. Its log10 E
  is set to the comparison's worst finite value plus one decade, so it ranks worst
  (`scripts/analyse.py`).
- **Test:** two-sided Wilcoxon signed-rank on d_m (scipy default handling of zero
  differences).
- **H2:** for each truth family and comparison, d_m = mean over tasks of
  log10 RMSE_Qst(P) - log10 RMSE_Qst(X). The same test, estimate, interval and words apply,
  with "estimates the isosteric heat better" in place of "extrapolates better". Holm
  correction over the 9 tests.
- **Estimate:** the Hodges-Lehmann estimate of d, with a 95 % bootstrap interval (10,000
  resamples of materials, seed 20261013) and a 90 % interval for equivalence.
- **Ratio:** R = 10^d, P's error relative to X's.
- **Smallest effect of interest:** a 25 % change in error, R = 0.8 or R = 1.25
  (|d| = 0.097).
- **H3:** reported as a proportion with a Wilson 95 % interval.

### 7.3 Minimum detectable effect

Computed before the freeze from the development set's spread of d (a simulation of the
Wilcoxon test at n = the confirmatory count, alpha after Holm). It is written here at the
freeze. If the minimum detectable R is weaker than 0.8, a null result is worded as
"inconclusive at this sample size", never as "no difference".

## 8. Verdict words (fixed now)

For each comparison of P with X:

The rows are evaluated top to bottom. They are exhaustive and do not overlap, which a
brute-force test over more than 10,000 outcome combinations checks
(`tests/test_analysis.py::test_verdict_table_is_exhaustive_consistent_and_never_contradicts_the_numbers`).
"Significant" means a Holm-adjusted p below 0.05. "Inside" means the 90 % interval of R
lies within [0.8, 1.25].

| Condition | Words |
|---|---|
| significant, R <= 0.8, upper 95 % bound of R < 1 | "P extrapolates better than X." |
| significant, R >= 1.25, lower 95 % bound of R > 1 | "X extrapolates better than P." |
| significant and inside | "P and X differ, by less than 25 %." |
| not significant and inside | "P and X are equivalent within 25 %." |
| significant, none of the above | "P and X differ; the size of the difference is uncertain." |
| none of the above | "Inconclusive: the data cannot tell P and X apart." |

For H2 the same rows apply, with "estimates the isosteric heat better than" in place of
"extrapolates better than". (Revised 2026-11-08, before the freeze: the first draft let
"equivalent" and "differ" overlap, and allowed "by less than 25 %" without an interval
supporting it.)

For H3:
- "Penalties do not remove violations" if the V-pen violation fraction has a lower Wilson
  bound above 0.
- "No violations detected for X" if X has zero violating fits. Then the Wilson upper bound
  is reported with it.

Program-level summary sentences, chosen by rule:
- If H1a is "better" and H1b is "equivalent" or "better": "The temperature structure
  carries the accuracy, and the hard constraints carry admissibility at no accuracy cost."
- If H1b is "X better": "The hard constraints cost accuracy."
- If H1c is "X better": "The temperature-invariant characteristic curve beats the learned
  potential."

## 9. What is not claimed

- The Henry limit cannot be tested on these data, because no isotherm reaches the Henry
  regime (Mg-SU-102 already holds about 0.08 g/g at 20 Pa). P2 is a property of the model,
  not a validated prediction.
- P4 (sign-correct LDF kinetics) is proved and unit-tested, not tested on data.
- An equilibrium potential represents one branch. Hysteresis and framework breathing are
  outside its scope.
- Without calorimetry (section 6.3b), no claim is made that P's Qst is closer to the true
  heat of a real material.

## 10. Freeze mechanics and deviations

- At the freeze, the SHA-256 of this file and of `results/dev_best_configs.json` are written
  into `scripts/run_confirmatory.py`. That script and `scripts/run_synthetic_h2.py` refuse to
  run if either file changes.
- The freeze commit is tagged `prereg-p3a-freeze` and pushed to the public repository
  before the first confirmatory fit, so its date is public.
- Any later change is an amendment with a date and reason, recorded in section 11 and in
  CORRECTIONS_P3A.md.
- Deviations found after confirmatory runs are reported as deviations, never edited away.

## 11. Amendments

None yet.
