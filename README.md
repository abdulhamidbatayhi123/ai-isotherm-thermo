# Hard shape constraints versus penalties for water isotherms of MOFs and COFs

Paper 3A of a research program on machine learning and physics for water sorption in metal-organic frameworks
(MOFs) and covalent organic frameworks (COFs). Paper 1 is at github.com/abdulhamidbatayhi123/ai-mof-cof-dynamics,
Paper 2 at github.com/abdulhamidbatayhi123/ai-kinetics-discoverability.

**Question.** Does building monotonicity in pressure and a Henry limit into an isotherm model (a positive mixture
of Langmuir and cooperative terms with van't Hoff affinities, written as the derivative of one convex potential)
make its temperature extrapolation of measured water isotherms better than the same function class with the
conditions as training penalties, an unconstrained network, a characteristic curve and dual-site Sips? Decided by a
test pre-registered and frozen before any confirmatory fit, on 13 materials (5 MOFs, 8 COFs).

**Status (2026-11-11).** Pre-registration frozen (tag `prereg-p3a-freeze`, commit 53cbc39). All confirmatory,
heat, sensitivity and diagnostic runs done. Manuscript in `paper/tex` (two internal review rounds applied).

**Results in one paragraph.** The hard-constrained model never produced a decreasing or negative isotherm (by
construction), while the penalty model at the weight chosen for accuracy did so in 9 of 26 extrapolations. Its
accuracy could not be separated from the penalty model's (error ratio 1.10, 95 % interval 0.93 to 1.65; the
pre-registered non-inferiority margin of 1.25 was not met) or from the other models. Its heats and capacities were
free to change sign with temperature; in 14 of 26 extrapolations its heat left 0 to 150 kJ/mol, and its worst
extrapolation came from that freedom. An exploratory sign-constrained variant (ledger X-6) is reported as a
hypothesis for a future test. Numbers: `results/verdicts.json` and the files named in `paper/tex/bindings.json`.

| Path | What it is |
|---|---|
| `PREREG_P3A.md`, `FREEZE_MANIFEST.json` | the frozen pre-registration and the SHA-256 of every frozen file |
| `CORRECTIONS_P3A.md` | the public ledger: defects before the freeze (P3A-1..25), analyses after the verdicts (X-1..6) |
| `src/p3a/` | models, fitting, thermodynamic evaluators, scoring |
| `scripts/run_confirmatory.py`, `scripts/run_synthetic_h2.py` | the frozen confirmatory runs (refuse to run if a frozen file changed) |
| `scripts/analyse.py`, `scripts/independent/cs_scorer.py` | the frozen analysis and the separately written second scorer |
| `scripts/descriptive_*.py`, `refit_diagnostics.py`, `step_position.py`, `explore_p_signs.py`, `diag_summary.py`, `sens_verdicts_sharded.py` | post-verdict descriptive and exploratory analyses (ledger X-1..X-6) |
| `results/`, `logs/` | every run record and every result file |
| `paper/` | figure scripts (`fig_*.py`, provenance in `paper/figures/*.prov.json`) and the manuscript build (`paper/tex/build_ms.py`) |
| `data/` | dataset summary, inclusion log, digitisation provenance and gates |

**Reproduce.** Python 3.12 with the versions in `requirements-lock.txt`; tests: `python -m pytest -q`. The
confirmatory runs need the local data set `data/raw/dataset/isotherms.csv`, which is not redistributed (it is
derived from third-party figures and database records); `scripts/digitise_sources.py` and
`scripts/build_dataset.py` regenerate it from the published sources, and its hash is in the freeze manifest. The
manuscript builds with `python paper/tex/build_ms.py --final`, which checks every number against its source file.

Licence: MIT for code. Third-party data keep their own licences (see `data/INVENTORY.md`).
