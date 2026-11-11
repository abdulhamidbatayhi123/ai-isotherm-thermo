# JCIM submission sheet (copy-paste for the ACS Publishing Center)

Generated from the built manuscript (paper/tex/main.pdf) so that the form matches it. Check against the PDF before
pasting.

## Files to upload (in this order)
1. Manuscript: `paper/tex/main.pdf` (the LaTeX source `paper/tex/main.tex` with figures, if the system asks for source)
2. Supporting Information: `paper/tex/si.pdf`
3. TOC graphic: `paper/submission/toc_graphic.tif` (3.25 x 1.75 in, 600 dpi, RGB)
4. Cover letter: `paper/submission/cover_letter_jcim.pdf`

## Form fields
- Journal: Journal of Chemical Information and Modeling
- Manuscript type: Article
- Title (12 words): Hard Constraints or Penalties? Temperature Extrapolation of MOF and COF Water Isotherms
- Author: Abdulhamid Batayhi (corresponding author)
  - Affiliation: Department of Mechatronics Engineering, Faculty of Mechanical Engineering, Yildiz Technical
    University, 34220 Istanbul, Türkiye
  - E-mail: abdulhamid.batayhi@std.yildiz.edu.tr (institutional address)
  - ORCID: 0009-0007-0374-6755 (link it in the ACS profile; JCIM asks that it not be typed into the manuscript)
- Funding: none (this research received no specific funding)
- Competing interests: none
- Preprint: none posted
- Previously submitted to JCIM: no
- Open access: subscription route (free). Optional: if open access is wanted, ask the YTU library whether the
  ACS-ANKOS read-and-publish agreement covers a student corresponding author (CC BY APC covered for affiliated
  corresponding authors; eligibility checked at acceptance).
- Do NOT request immediate posting of the accepted manuscript (that triggers ACS's article development charge).
- Suggested reviewers: optional (see `paper/submission/suggested_reviewers.md` if present)
- Generative AI: disclosed in the Acknowledgment (Claude Opus 5 and Opus 5.5, Anthropic, through Claude Code; drafting
  and language editing, code, bibliographic checks; the author designed the study and made every decision)

## Abstract (196 words, 4 sentences, as rendered)
Learned models of water isotherms in metal-organic and covalent organic frameworks (MOFs and COFs) can predict uptake that falls as pressure rises; monotonicity can be built into a model or added as a training penalty. In a pre-registered benchmark on 13 frameworks, each model predicted the isotherm at the highest or lowest measured temperature, 5 to 25 K beyond its training data, and a model monotone and linear at low pressure by construction, P, was compared with a relaxed, penalty-trained version of it, neural networks and classical models. At its accuracy-tuned weight the penalty version predicted falling or negative uptake in 9 of 26 extrapolations, and a weight chosen post hoc on development materials still left 4, while the accuracy comparisons were inconclusive (ratio of P’s error to the penalty version’s 1.10, 95% confidence interval 0.93 to 1.65; non-inferiority within 25% not shown) and characteristic-curve models had the lowest median errors. Because P’s heats were free in sign, its isosteric heat left 0 to 150 kJ mol-1 in 14 extrapolations, and the same freedom caused its worst error: shape constraints guarantee monotone isotherms without tuning a weight, but the temperature dependence needs constraints of its own.

## Data and software availability
Code, run records, results, pre-registration and freeze manifest: https://github.com/abdulhamidbatayhi123/ai-isotherm-thermo,
archived at https://doi.org/10.5281/zenodo.24148253 (v1.1.0). Isotherm point lists: 6 confirmatory and 1 development
materials with CC BY 4.0 sources are public in data/open; 6 confirmatory and 3 development materials are extracted by
the repository's scripts from free sources (NIST/ARPA-E database, open-access source data and supporting information);
COF-432 comes from a subscription article (list available to the editor and reviewers in confidence).
