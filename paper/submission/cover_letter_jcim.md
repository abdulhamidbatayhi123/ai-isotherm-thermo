<!-- Cover letter for J. Chem. Inf. Model. Every number is the bound value in paper/tex/main.tex (build_ms.py checks
those against the results files); the X-7/X-8 numbers are in results/vpen_weight_summary.json, results/cell_summary.json
and results/isostere_baseline.json. Editor-in-Chief and address as given in the live JCIM author guidelines
(researcher-resources.acs.org, read 2026-11-11). Re-check the numbers against the final build before submitting. -->

12 November 2026

Prof. Kenneth M. Merz, Jr.\
Editor-in-Chief, Journal of Chemical Information and Modeling

Dear Prof. Merz,

I submit the Article "Hard Constraints or Penalties? Temperature Extrapolation of MOF and COF Water Isotherms" for consideration in the Journal of Chemical Information and Modeling.

Machine-learning models of chemical data are increasingly given physical conditions, either built into the
architecture or added to the training loss as penalties. Which of the two to use is usually argued, not tested. The
manuscript is a pre-registered benchmark of these constraint strategies on a task that matters for water sorbents
in heat pumps and water harvesters: predicting the water isotherm of a metal-organic or covalent organic framework
at a temperature where none was measured.

The JCIM guidelines rightly caution against new models whose results are similar to existing methods. This paper
does not propose a model that wins. It asks whether a constraint strategy changes the outcome, and it was designed so
that a null answer could be told apart from an inconclusive one; here the accuracy comparison was inconclusive, and
the paper says so. The comparisons, an equivalence margin, the words of every possible outcome (including a classical
model that wins) and the analysis code were frozen before any confirmatory fit, and synthetic data checked beforehand
that each verdict could fail. On 13 frameworks (5 MOFs, 8 COFs), in a factorial design crossing the shape constraint
(none, penalty, hard) with the temperature structure, the results are:

- The hard constraints gave monotone, non-negative isotherms in every fit, whereas the penalty at its accuracy-tuned
  weight left shape violations in 9 of 26 extrapolations. In post hoc refits, a far heavier weight removed every
  violation above the counting tolerance without a clear change in the error ratio, but only a weight found on the
  test materials did so: the lightest weight that removed the violations on the development materials left
  violations in 4 of 26 test extrapolations. The hard constraint gives the guarantee without that choice; no accuracy advantage was found.
- The accuracy comparisons were inconclusive. Against the penalty model the error ratio was 1.10 (95% confidence
  interval 0.93 to 1.65), so the pre-registered non-inferiority claim was not shown. The characteristic curves had the
  lowest median errors, and a classical isostere extrapolation could not be told apart from the hard model, although
  its isosteres crossed in 15 of 26 extrapolations.
- The temperature dependence, left free in sign, produced heats outside 0 to 150 kJ mol⁻¹ in 14 of 26 extrapolations
  and the worst single extrapolation, which points to constraints on the temperature dependence as the next step.

For the JCIM reader the transferable parts are the benchmark protocol, which applies to any learned model of
scientific data with physical constraints, a table of every model in the design, and a short set of recommendations
for learned isotherm models in the Discussion. The work also matches the journal's data and software policy: the
frozen pre-registration and its hash manifest, a public ledger of every deviation and every analysis added after the
verdicts, a separately written second scorer, all run records, and a manuscript build that checks every number in
the text against its source file are public (github.com/abdulhamidbatayhi123/ai-isotherm-thermo; archived at
doi:10.5281/zenodo.24167591). Following the journal's 2020 editorial on data sharing, the isotherm point lists
from openly licensed sources are public, the repository's scripts extract those of all but one other material from
freely available sources, and the remaining list, from a subscription article, is available to the editor and
reviewers in confidence.

The manuscript has not been published and is not under consideration elsewhere, and it has not been posted as a
preprint. I have no competing interests. The use of a generative AI assistant as a tool is disclosed in the
Acknowledgment and the Methods.

Sincerely,

Abdulhamid Batayhi\
Department of Mechatronics Engineering, Faculty of Mechanical Engineering\
Yildiz Technical University, 34220 Istanbul, Türkiye\
abdulhamid.batayhi@std.yildiz.edu.tr
