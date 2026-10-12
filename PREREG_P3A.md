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
  section 7). A dedicated calorimetry search is running (research/lit_3a_calorimetry.md),
  and section 6.3 depends on its result.

## 3. Data

### 3.1 Development set (tuning only, never confirmatory)

These come from ISODB, as digitised by NIST:
- CuBTC (HKUST-1) and MIL-100, Rezk et al. 2012 (9 temperatures, 293 to 358 K);
- CAU-10-H, Frohlich et al. 2014 (298, 313, 333 K);
- MIL-160, Cadiau et al. 2015 (293, 303, 313 K).

They are chosen because their provenance is documented and they are not needed for the
confirmatory comparison. If Rezk's duplicate curves per temperature cannot be resolved
into one adsorption branch, the material is dropped and the drop is recorded.

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

### 3.3 Inclusion rules (applied before any model is fitted to the material)

A material and paper pair is included if all of the following hold. Each exclusion is
recorded with its reason in `data/inclusion_log.csv`.
1. There are adsorption-branch isotherms at 3 or more temperatures on the same sample.
2. Each isotherm has at least 8 points with 0 < p/p_sat <= 0.90.
3. The figure passes the digitisation quality gate (section 3.5).
4. The temperatures are unambiguous. A conflict between the main text and the SI (as for
   Ni2X2(BTDD)) excludes the set unless it can be resolved from the source.

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
- **Raster figures:** the page is rendered at 600 dpi. The axes are calibrated on at least
  two labelled ticks per axis. Markers are located by colour segmentation in a script
  (`data/scripts/digitise_*.py`), and every extracted curve is plotted over the source
  image for a visual check. The script, the calibration points and the overlay image are
  kept. Point lists from closed or ND-licensed sources stay local; their fitted parameters
  and predictions are published.
- **Measured digitisation error:** Mg-SU-102 main Fig. 4 is digitised blind from its raster
  image, then compared with the numeric source data. The RMS and maximum deviation in
  uptake (as a fraction of the axis span) and in p/p_sat are the error model. They are used
  for the noise in section 6.3 and are reported next to every result on digitised data.
  This is done before any confirmatory fit.
- **Quality gate:** the axis-calibration residual must be below 0.5 % of the axis span, and
  the overlay check must show no missed or spurious points. If not, the set is excluded and
  the reason recorded.

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

- **Unit:** the material (n is about 25 confirmatory materials).
- **Test:** two-sided Wilcoxon signed-rank on d_m.
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

| Condition | Words |
|---|---|
| Holm-adjusted p < 0.05, R <= 0.8, upper 95 % bound of R < 1 | "P extrapolates better than X." |
| Holm-adjusted p < 0.05, R >= 1.25, lower 95 % bound of R > 1 | "X extrapolates better than P." |
| 90 % interval of R inside [0.8, 1.25] | "P and X are equivalent within 25 %." |
| Holm-adjusted p < 0.05, but R between 0.8 and 1.25 | "P and X differ, by less than 25 %." |
| none of the above | "Inconclusive: the data cannot tell P and X apart." |

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

- At the freeze, the SHA-256 of this file is written into `scripts/confirmatory_run.py`.
  The script refuses to run if the file changes.
- Any later change is an amendment with a date and reason, recorded in section 11 and in
  CORRECTIONS_P3A.md.
- Deviations found after confirmatory runs are reported as deviations, never edited away.

## 11. Amendments

None yet.
