<!-- Draft cover letter for J. Chem. Inf. Model. Every number is the bound value in paper/tex/main.tex (build_ms.py
checks those against the results files). Editor-in-Chief and address as given in the live JCIM author guidelines
(researcher-resources.acs.org, read 2026-11-11). Re-check the numbers against the final build before submitting. -->

Prof. Kenneth M. Merz, Jr.
Editor-in-Chief, Journal of Chemical Information and Modeling

Dear Prof. Merz,

I submit the Article "Hard Shape Constraints versus Penalties for Temperature Extrapolation of MOF and COF Water
Isotherms" for consideration in the Journal of Chemical Information and Modeling.

Machine-learning models of adsorption isotherms are increasingly built with physical conditions, either enforced by
the architecture or added to the training loss as penalties. Whether the hard version is worth its restrictions is
usually argued, not tested. This manuscript tests it for a task that matters for water sorbents in heat pumps and
water harvesters: predicting the water isotherm of a metal-organic or covalent organic framework at a temperature
where none was measured.

The test was pre-registered and frozen before any confirmatory fit. A positive mixture of Langmuir and cooperative
terms, written as the derivative of one convex potential so that uptake always rises with pressure, was compared in
a factorial design with the same function class trained with penalties, unconstrained networks, a characteristic
curve and dual-site Sips, on 13 frameworks (5 MOFs, 8 COFs). The results are mixed and reported as they came out:

- the hard constraints removed shape violations (0 of 26 extrapolations, against 9 of 26 for the penalty model);
- they did not buy accuracy: the error ratio against the penalty model was 1.10 (95 % interval 0.93 to 1.65), so
  the pre-registered non-inferiority claim was not shown, and the characteristic curve had the lowest median error;
- the temperature dependence, left free in sign, produced heats outside 0 to 150 kJ/mol in 14 of 26 extrapolations
  and the worst single extrapolation, which points to constraints on the temperature dependence as the next step.

I believe the work suits JCIM because it is a methodological test of physics-constrained machine learning on
chemical data, with an emphasis on reproducibility that matches the journal's data and software policy: the frozen
pre-registration and its hash manifest, a public ledger of every deviation and every analysis added after the
verdicts, a separately written second scorer, all run records, and a manuscript build that checks every number in
the text against its source file are public (github.com/abdulhamidbatayhi123/ai-isotherm-thermo; archived release
doi:10.5281/zenodo.24120765).

The manuscript has not been published and is not under consideration elsewhere. I have no competing interests. The
use of a generative AI assistant as a tool is disclosed in the Acknowledgment and the Methods.

Sincerely,

Abdulhamid Batayhi
Department of Mechatronics Engineering, Faculty of Mechanical Engineering
Yildiz Technical University, 34220 Istanbul, Türkiye
abdulhamid.batayhi@std.yildiz.edu.tr
