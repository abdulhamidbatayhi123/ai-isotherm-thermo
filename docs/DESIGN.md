# Paper 3A design: a learned adsorbed-phase potential for water isotherms

Started 2026-10-12. Status: design, before the literature review and data inventory have
returned. Sections marked OPEN are settled by those two steps and then by the
pre-registration, which is shown to the author before it is frozen.

## 1. Question

Can a model that learns one adsorbed-phase potential, and obtains the water isotherm
q*(p, T) and the isosteric heat Qst(q) from its derivatives, predict water uptake at
temperatures it was not trained on, and give better isosteric heats, than (a) the same
network without constraints, (b) the same network with the constraints as loss
penalties, and (c) the strongest classical models, including the temperature-invariant
characteristic curve?

The paper is a test, not an advertisement. A pre-declared outcome in which the classical
characteristic curve wins is a publishable result and is written down as such in advance.

## 2. Thermodynamics the model must respect

Water vapour at the pressures of interest (below about 10 kPa) is treated as an ideal gas,
so the gas chemical potential is mu = mu0(T) + RT ln p. The adsorbed-phase volume is
neglected next to the gas volume. Both approximations are stated and their size is
quantified from sources (compressibility factor of water vapour at a few kPa).

Let s = ln(p / 1 Pa) and tau = 1/T. The reduced spreading pressure (spreading pressure
times area over RT, per kg of adsorbent, in mol/kg) is

    psi(s, T) = integral from 0 to p of q*(p', T) / p' dp'      (Gibbs adsorption isotherm)

so that q*(s, T) = d psi / d s at constant T. Properties:

- P1 monotonicity: dq*/ds >= 0 at constant T if and only if psi is convex in s.
- P2 Henry limit: q*/p tends to a finite, positive K(T) as p tends to 0.
- P3 Clausius-Clapeyron consistency: the isosteric heat is the same object as the
  isotherm's temperature dependence,
      Qst(q, T) = -R (d ln p / d(1/T)) at constant q = R (dq*/dtau)_s / (dq*/ds)_tau.
  Any model that outputs q*(s, T) defines Qst this way. Inconsistency appears when the
  heat is learned or fitted separately, when isotherms at each temperature are fitted
  independently and differenced, or when dq*/ds changes sign so that Qst is undefined.
- P4 sign-correct kinetics: in the linear-driving-force law dq/dt = k (q* - q) with
  k >= 0 and q* strictly increasing in p, the uptake rate has the sign of
  mu_gas - mu_ads(q), so the entropy production (mu_gas - mu_ads) dq/dt is never negative.
  Paper 3A has no kinetic data. P4 is proved and unit-tested, and it is not a
  confirmatory hypothesis.

Honest limits, stated in the paper: for a pure gas, P3 does not by itself mean
"accurate". Its value is that the isotherm and the heat come from one object and cannot
disagree, and that a smooth, admissible temperature dependence may extrapolate better.
The second claim is the one that is tested.

## 3. The proposed model (P)

    psi(s, T) = sum over k of  c_k(T) / g_k * softplus( g_k * (s - theta_k(T)) )

    q*(s, T)  = sum over k of  c_k(T) * sigmoid( g_k * (s - theta_k(T)) )

- c_k(T) = softplus(network) >= 0: the capacity of term k.
- theta_k(T) = network output: the ln-pressure position of term k.
- g_k = 1 for the Henry terms. For cooperative terms g_k = 1.5 + softplus(parameter), so
  they stay distinct from the Henry terms. These terms give the S-shaped steps of water in MOFs.

What holds by construction, for every parameter value:
- P1: each term is increasing in s, so psi is convex and q* is strictly increasing.
- P2: as s tends to minus infinity, each Henry term tends to c_k exp(s - theta_k) and each
  cooperative term vanishes faster, so K(T) = sum over Henry terms of c_k exp(-theta_k) > 0.
- P2 is a limit. How low the pressure must be before q*/p is within a given
  tolerance of K(T) depends on the parameters, so the paper never says that the data
  reach the Henry regime unless they do.
- Bounded uptake: q* is at most the sum of c_k(T).
- P3: Qst is computed from the same function, by automatic differentiation.

Interpretation: with g_k = 1 the model is a learned adsorption-energy distribution over
Langmuir kernels, which the classical generalised adsorption isotherm uses. The
cooperative terms add lateral attraction, which is what makes water isotherms S-shaped.
A positive mixture of logistic functions approximates any bounded increasing function of
s, so the family is flexible enough for type I, IV and V shapes.

Temperature dependence enters only through c_k(T) and theta_k(T). Their inputs are
scaled 1/T. OPEN: whether the networks get the characteristic-curve coordinate as a
structural option. Decide after the classical review.

**Revision 2026-10-13 (CORRECTIONS_P3A.md, P3A-2).** A synthetic diagnostic showed that
convexity and the Henry limit do not make temperature extrapolation work. A free network
in 1/T fits the training temperatures and then bends the step position outside them. The
temperature dependence of P is therefore thermodynamic, set by `t_mode`:
- "vanthoff": theta_k(T) = theta_k0 - (Q_k/R)(1/T - 1/T_ref), so each term has a constant heat.
- "kirchhoff": adds a constant heat capacity, so Q_k(T) = Q_k - dc_k (T - T_ref).
- In both, c_k(T) = c_k0 exp(-alpha_k (T - T_ref)), for adsorbate expansion.
- "nn": the free network, kept for the ablation.

The number of terms is what makes P a flexible learned potential rather than a two-site
fit. It is a learned site-energy distribution with cooperative terms.

## 3a. The factorial design this implies

What the potential buys has two separate parts: the shape constraints (P1, P2) and the
temperature structure. The study crosses them, so each contribution is measured and none
is credited to the other:

| shape \ temperature | free network in 1/T | van't Hoff per term | characteristic curve A |
|---|---|---|---|
| none (MLP) | U | U-vH (OPEN: how to give an MLP this structure) | U-A: MLP of A |
| penalty | Pen | Pen-vH | Pen-A |
| hard (potential) | P-nn | **P** (vanthoff or kirchhoff) | C2-flex: monotone W(A) |

C1 (classical two-site Sips with van't Hoff) is a small-capacity member of the P column,
and a strong classical reference. The pre-registration fixes which cells are confirmatory
and which are descriptive.

## 4. Competitors (matched budget, at least three seeds, best configuration of each)

- U: an unconstrained MLP q(s, T), with Qst from the same implicit-derivative formula.
- Pen: the same MLP with penalty terms for P1 (negative dq/ds on collocation points) and
  P2 (low-pressure linearity). The penalty weights are tuned on validation data, giving
  the penalty approach its best chance.
- C1: a classical multi-site cooperative model, dual-site Sips/Langmuir-Freundlich with
  van't Hoff b(T).
- C2: the Dubinin-Polanyi characteristic curve q = W(A), A = RT ln(p0(T)/p), with a
  flexible monotone W. It is temperature-invariant by construction, and its
  Qst = A + L(T), where L(T) = -R d ln p0 / d(1/T).
- OPEN: GAB or another water-specific model if the classical review shows one is standard
  for MOFs.

## 5. Data (OPEN until data/INVENTORY.md is complete)

Real, measured, multi-temperature adsorption-branch water isotherms of MOFs and COFs,
from NIST ISODB and the primary literature. CoRE MOF 2024 is simulated, so at most it is a
secondary arm. COF-432 is a held-out COF if its data allow it. Digitised data carry a
stated digitisation error.

## 6. Tests the pre-registration will fix (OPEN wording)

- H1 temperature extrapolation: error at held-out temperatures, above and below the
  training range, P against U, Pen, C1 and C2.
- H2 isosteric heat: Qst against independent calorimetry where it exists. Otherwise
  Qst stability under removal of one training temperature. The inventory decides which.
- H3 physical violations: counts of P1 and P2 violations, of undefined or negative Qst,
  and of non-physical extrapolations on a dense grid. P has zero by construction. The
  test is how many U and Pen have.
- For each hypothesis: a smallest effect of interest, the paired test across materials and
  seeds, and the verdict sentences, all fixed before any confirmatory run.

## 7. Software

- src/p3a/water.py: p0(T) from the IAPWS saturation-pressure equation, and L(T).
- src/p3a/thermo.py: Qst by autodiff, the Henry-constant estimate, violation counters,
  and the LDF sign check.
- src/p3a/models.py: P, U, the Pen loss, C1, C2.
- src/p3a/synthetic.py: analytic isotherms with known Qst and K(T).
- tests/: known answers (Langmuir and Sips with van't Hoff: Qst = Q exactly;
  Dubinin-Astakhov: Qst = A + L(T)); autodiff against finite differences; P1, P2 and P4
  for random parameters; a small recovery fit on synthetic multi-temperature data.

Everything runs in float64 on the CPU. Fits are small (hundreds of points, thousands of
parameters). No confirmatory run happens before the freeze.

## 8. Rules carried from Papers 1 and 2

Pre-registration frozen before data are used for confirmation. Pre-declared verdict
words. Matched budgets. At least three seeds. The strongest competitor configuration.
No number without a script. A citation gate. A public correction ledger
(CORRECTIONS_P3A.md). Plain prose, almost no em dashes. The AI declaration in the
author's wording.
