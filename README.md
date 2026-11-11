# Hard constraints or penalties? Temperature extrapolation of MOF and COF water isotherms

Code, results and pre-registration for the manuscript "Hard Constraints or Penalties? Temperature Extrapolation of MOF and COF Water Isotherms" (A. Batayhi, submitted to the Journal of Chemical Information and
Modeling). Archived at doi:10.5281/zenodo.24148253. Paper 3A of a research program on machine learning and physics
for water sorption in metal-organic frameworks (MOFs) and covalent organic frameworks (COFs); Paper 1 is at
github.com/abdulhamidbatayhi123/ai-mof-cof-dynamics, Paper 2 at github.com/abdulhamidbatayhi123/ai-kinetics-discoverability.

**Question.** Does building monotonicity in pressure and a Henry limit into an isotherm model (a positive mixture
of Langmuir and cooperative terms with van't Hoff affinities, written as the derivative of one convex potential)
make its temperature extrapolation of measured water isotherms better than a relaxed version of the same model with
the conditions as training penalties, an unconstrained network, characteristic curves and dual-site Sips? Decided by
a test pre-registered and frozen before any confirmatory fit, on 13 materials (5 MOFs, 8 COFs).

**Results in one paragraph.** The hard-constrained model never produced a decreasing or negative isotherm (by
construction), while the penalty model at the weight chosen for accuracy did so in 9 of 26 extrapolations. The
accuracy comparison was inconclusive: error ratio 1.10 against the penalty model, 95 % interval 0.93 to 1.65, so the
pre-registered non-inferiority margin of 1.25 was not met; the characteristic curves had the lowest median errors
among the models fitted to every material. In post hoc refits (ledgers X-7, X-8), a far heavier penalty weight removed every
violation above the counting tolerance without a clear change in the error ratio, but a weight chosen on the
development materials left violations in 4 of 26; a classical isostere extrapolation could not be told apart from
the hard model, but its isosteres crossed in 15 of 26. The hard model's heats were free in
sign; in 14 of 26 extrapolations its heat left 0 to 150 kJ/mol, and its worst extrapolation came from that freedom.
Numbers: `results/verdicts.json`, `results/vpen_weight_summary.json` and the files named in `paper/tex/bindings.json`.

| Path | What it is |
|---|---|
| `PREREG_P3A.md`, `FREEZE_MANIFEST.json` | the frozen pre-registration (tag `prereg-p3a-freeze`, commit 53cbc39) and the SHA-256 of every frozen file |
| `CORRECTIONS_P3A.md` | the public ledger: defects found before the freeze (P3A-1..25) and every analysis added after the verdicts (X-1..X-8) |
| `src/p3a/` | models, fitting, thermodynamic evaluators, scoring |
| `scripts/run_confirmatory.py`, `scripts/run_synthetic_h2.py` | the frozen confirmatory runs (they refuse to run if a frozen file changed) |
| `scripts/analyse.py`, `scripts/independent/cs_scorer.py` | the frozen analysis and the separately written second scorer |
| `scripts/descriptive_*.py`, `refit_diagnostics.py`, `step_position.py`, `explore_p_signs.py`, `explore_vpen_weight.py`, `analyse_vpen_weight.py`, `isostere_baseline.py`, `heat_window_real.py`, `cell_summary.py`, `diag_summary.py`, `sens_verdicts_sharded.py` | post-verdict descriptive and exploratory analyses (ledger X-1..X-8) |
| `scripts/launch/` | the command files that started the long runs (see its README) |
| `results/`, `logs/` | every run record and every result file |
| `paper/` | figure scripts (`fig_*.py`, provenance in `paper/figures/*.prov.json`), the manuscript and SI sources and their build (`paper/tex/build_ms.py`), submission files |
| `data/` | dataset summary, inclusion log, digitisation provenance and gates |

**Reproduce.**
- Environment: Python 3.12 with the versions in `requirements-lock.txt`; tests: `python -m pytest -q`.
- Data: the confirmatory runs need the local data set `data/raw/dataset/isotherms.csv`, which is not redistributed
  (it is digitised from third-party figures under publisher copyright and from database records).
  `scripts/digitise_sources.py` and `scripts/build_dataset.py` regenerate it from the source figures, which are
  obtained from the cited publications (`data/INVENTORY.md`); its SHA-256 is in the freeze manifest, so a
  regenerated copy can be checked against the one used.
- Results: every result file is rebuilt from the run records by the analysis scripts above; the figures by
  `paper/fig_*.py`; the tables by `paper/tex/make_tables.py`.
- Manuscript: `python paper/tex/build_ms.py --final` (needs the `tectonic` LaTeX engine on PATH, or `TECTONIC` set to
  it) compiles the article and the SI and checks every number in the text against its source file.

Licence: MIT for code. Third-party data keep their own licences (see `data/INVENTORY.md`).
