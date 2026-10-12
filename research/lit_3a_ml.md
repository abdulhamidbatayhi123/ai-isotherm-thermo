# Paper 3A literature journal: physics-constrained ML for adsorption isotherms

Read date for every entry: 2026-10-12 (unless stated). Every source below was opened live (arXiv abs/html, publisher page, Crossref API, OpenAlex API or full-text PDF). No archived copies were used. Entries labelled SEEN-ONLY were seen in a search result but could not be opened and are not evidence.

Question: what exists on ML models of adsorption isotherms that are physics-constrained, thermodynamically consistent, monotone, convex or derivative-based, and where exactly is the gap for a network that learns an adsorbed-phase potential whose derivatives give q*(p,T) and Qst with monotonicity, Clausius-Clapeyron consistency, Henry limit and sign-correct LDF kinetics by construction.

## A. Physics-informed and derivative-based ML isotherm models (closest family)

### L01. Lin, Wang, Deng 2025, IsothermODE
- Citation: Emily Lin, Evelyn Wang, Sili Deng (2025). Neural ordinary differential equations (ODEs) for smooth, high-accuracy isotherm reconstruction, interpolation, and extrapolation. npj Computational Materials 11, 348. DOI 10.1038/s41524-025-01819-8.
- URLs opened: https://api.crossref.org/works/10.1038/s41524-025-01819-8 (title, authors, venue confirmed); https://api.openalex.org/works/doi:10.1038/s41524-025-01819-8 (abstract, gold OA); full-text PDF https://www.nature.com/articles/s41524-025-01819-8.pdf (downloaded to scratch, text extracted and searched).
- What was read: full text (keyword-level reading of methods and results).
- Supports: a neural ODE learns the derivative dq/dlnp of CO2 uptake for MOFs (GCMC data from QMOF, CoRE MOF 2019, hMOF) and integrates it to reconstruct the isotherm from five pressure points; a second NODE (N-ODE-H) predicts the heat of adsorption curve, trained on GCMC enthalpies and guided by the uptake prediction. The paper writes down the Gibbs adsorption equation via the grand potential (dOmega relation) and interprets the learned derivative thermodynamically, and compares dq/dp at low pressure with the Henry constant post hoc. Monotonicity is observed, not imposed: the vector field uses SiLU, which the authors call "non-monotonic", and they state dq/dp "should theoretically always be" non-negative and mark that boundary in latent maps. Single temperature (CO2, isothermal GCMC); heat is learned as a separate output, not derived from the isotherm by Clausius-Clapeyron; no Henry limit imposed; simulated data only, no water.
- Relevance: HIGH. It is the closest derivative-based ML isotherm paper and it already invokes the grand potential and Gibbs adsorption equation, so Paper 3A cannot claim to be the first to "connect neural isotherms to the grand potential". It does not learn a potential, does not span temperature, does not tie heat to isotherm, and guarantees none of the constraints. Narrows the gap in wording, not in substance.

### L02. Nooraiepour, Masoudi, Song, Hellevang 2026 (H2 PINN)
- Citation: Mohammad Nooraiepour, Mohammad Masoudi, Zezhang Song, Helge Hellevang (2026). Physics-Informed Neural Networks for Predicting Hydrogen Sorption in Geological Formations: Thermodynamically Constrained Deep Learning Integrating Classical Adsorption Theory. arXiv:2603.28328 [cs.LG], submitted 30 Mar 2026. DOI 10.48550/arXiv.2603.28328. No journal ref listed.
- URLs opened: https://arxiv.org/abs/2603.28328 ; https://arxiv.org/html/2603.28328 (first 100k characters of full text).
- What was read: abstract and methods/results (partial full text).
- Supports: PINN predicts H2 uptake directly in clays, shales and coals (1,987 isotherm measurements). Monotonicity dQ/dp >= 0 is a weighted loss term computed by autodiff; saturation via a penalty on lithology-specific Langmuir limits; non-negativity by Softplus output (the only architectural guarantee). Abstract says constraints are enforced "via penalty weighting". Reports "98.6% monotonicity satisfaction", i.e. 1.4% of held-out cases violate monotonicity. Van't Hoff dependence is said to be embedded in the loss but the listed loss terms do not show it explicitly; Henry limit described only as something that "can be enforced through penalty terms"; isosteric heat from classical per-sample fits, not from the network; no potential learned.
- Relevance: HIGH as the soft-penalty foil. Its own reported 1.4% monotonicity violation is direct evidence for the Paper 3A argument that penalties do not guarantee physics.

### L03. Nooraiepour, Song, Li, Perez 2026 (CH4 PINN transfer)
- Citation: Mohammad Nooraiepour, Zezhang Song, Wei Li, Sarah Perez (2026). Physics-Informed Neural Networks for Methane Sorption: Cross-Gas Transfer Learning, Ensemble Collapse Under Physics Constraints, and Monte Carlo Dropout Uncertainty Quantification. arXiv:2604.13992 [cs.LG], submitted 15 Apr 2026. DOI 10.48550/arXiv.2604.13992.
- URL opened: https://arxiv.org/abs/2604.13992
- What was read: abstract and metadata.
- Supports: transfers the H2 PINN to CH4 on coal (993 measurements, 114 experiments) with Elastic Weight Consolidation and a curriculum that "progressively balances transfer preservation with thermodynamic fine-tuning"; R2 0.932; deep ensembles degrade under physics constraints, MC dropout best calibrated.
- Relevance: MEDIUM. Same soft-constraint family as L02; the "ensemble collapse under physics constraints" observation is a useful point that penalty constraints interact badly with training.

### L04. Daou, Fang, Boulfelfel, Ravikovitch, Sholl 2024 (ML + Clausius-Clapeyron + IAST, zeolites)
- Citation: Alan S. S. Daou, Hanjun Fang, Salah Eddine Boulfelfel, Peter I. Ravikovitch, David S. Sholl (2024). Machine Learning and IAST-Aided High-Throughput Screening of Cationic and Silica Zeolites for Alkane Capture, Storage, and Separations. J. Phys. Chem. C 128, 6089-6105. DOI 10.1021/acs.jpcc.4c00066 (Crossref confirms title, authors, venue).
- URLs opened: https://api.crossref.org/works/10.1021/acs.jpcc.4c00066 ; OpenAlex abstract; accepted manuscript https://www.osti.gov/pages/servlets/purl/2351063 (PDF text extracted and searched).
- What was read: full text (keyword-level reading of the methods).
- Supports: a random-forest classifier screens out negligible adsorption, then two separate regression models (gradient-boosting family, trained on GCMC with coupled-cluster-quality force fields) predict loading at 300 K and the loading-dependent heat Qst(q). Isotherms at other temperatures come from the integrated Clausius-Clapeyron relation, ln(f1/f2) = (Qst/R)(1/T2 - 1/T1), with T1 = 300 K, assuming Qst depends on loading only; mixtures by IAST. Quote: the two quantities "can then be combined to generate isotherms at arbitrary temperatures".
- Relevance: HIGH. This is the closest prior "ML + Clausius-Clapeyron by construction" pipeline. Temperature dependence is consistent with the supplied Qst(q) by construction, but (i) the 300 K isotherm model and the Qst model are independent learners, so no relation forces them to agree with each other or with the Gibbs adsorption equation; (ii) Qst is assumed temperature-independent; (iii) monotonicity and Henry limit are not guaranteed; (iv) no potential is learned; (v) simulated alkanes in zeolites, not water. Paper 3A must cite it and explain that a learned potential makes q and Qst two derivatives of one function instead of two independent regressors glued by a constant-Qst integration.

### L05. Alimin et al. 2025 (surfactant PINN)
- Citation: Achmad Anggawirya Alimin, Kattariya Srasamran, Wanutchaya Yuenyong, Ampira Charoensaeng, Bor-Jier Shiau, Uthaiporn Suriyapraphadilok (2025). Surfactant representation using COSMO screened charge density for adsorption isotherm prediction using Physics-Informed Neural Network (PINN). J. Cheminformatics 17, 84. DOI 10.1186/s13321-025-01027-y.
- URLs opened: Crossref and OpenAlex records (abstract). Publisher page redirected to link.springer.com; not read beyond abstract.
- What was read: abstract.
- Supports: "PINN" built by "integrating adsorption isotherm into artificial neural networks"; 56 isotherms of 20 surfactants on sand and silica; temperature is an input.
- Relevance: LOW-MEDIUM. Liquid-phase surfactant adsorption; structure appears to be an ANN feeding a classical isotherm form (hybrid), not a learned potential. Shows "PINN" is used loosely in the adsorption literature.

### L06. Bannoud et al. 2026 (IgG PINN)
- Citation: Mohamad A. Bannoud, Antonio O. S. Junior, Gabriel Y. Ottaiano, Mariana A. de Moraes, Igor T. L. Bresolin, Tiago D. Martins (2026). Modeling equilibrium adsorption isotherms of human immunoglobulin G onto fibroin microparticles using machine learning and physics-informed neural networks. Chemical Papers (published 9 Sep 2026). DOI 10.1007/s11696-026-05468-z.
- URLs opened: Crossref and OpenAlex records (abstract).
- What was read: abstract.
- Supports: on 15 experimental isotherms, plain ML had the lowest error but "often produced physically inconsistent curves"; PINNs with monotonicity, concavity and saturation constraints had higher error but realistic shapes; frames a trade-off between accuracy and consistency.
- Relevance: MEDIUM as motivation. Recent (Sep 2026) evidence that the adsorption community currently treats physical consistency as a penalty that costs accuracy. Paper 3A can test whether hard construction removes that trade-off.

## B. Hard-constrained thermodynamic ML in neighbouring fields (templates)

### L07. Rosenberger, Barros, Germann, Lubbers 2022 (learned free energy EOS)
- Citation: David Rosenberger, Kipton Barros, Timothy C. Germann, Nicholas Lubbers (2022). Machine learning of consistent thermodynamic models using automatic differentiation. Phys. Rev. E 105, 045301. DOI 10.1103/PhysRevE.105.045301. arXiv:2108.04904.
- URL opened: arXiv API record for 2108.04904 (abstract, journal ref).
- What was read: abstract.
- Supports: an ANN models the free energy; properties are learned as its autodiff derivatives; better accuracy than learning properties directly and "exact preservation of the Maxwell relations"; demonstrated on van der Waals and Lennard-Jones data.
- Relevance: HIGH as template. Learns a potential and differentiates it. Bulk fluid, not adsorption.

### L08. Chaparro and Mueller 2023 (FE-ANN EoS)
- Citation: Gustavo Chaparro, Erich A. Mueller (2023). Development of thermodynamically consistent machine-learning equations of state: Application to the Mie fluid. J. Chem. Phys. (published 10 May 2023). DOI 10.1063/5.0146634.
- URL opened: Crossref search result record (title, authors, venue, date confirmed). Content from search summary only.
- What was read: metadata only (content SEEN-ONLY via search snippet: Helmholtz energy ANN trained on first and second derivative data).
- Relevance: MEDIUM as template (learned Helmholtz energy); cite with care, content not opened.

### L09. Hinz et al. 2024 (physics-informed EOS)
- Citation: Hinz, Yu, Pandey, Sapkota, Yu, Mihaylov, Karasiev, Hu (2024). The development of thermodynamically consistent and physics-informed equation-of-state model through machine learning. APL Machine Learning. DOI 10.1063/5.0192447.
- URL opened: Crossref search record.
- What was read: metadata only.
- Relevance: LOW-MEDIUM, another learned-free-energy EOS; confirms that potential-based EOS learning is an active area.

### L10. Rittig, Felton, Lapkin, Mitsos 2023 (Gibbs-Duhem-informed, soft)
- Citation: Jan G. Rittig, Kobi C. Felton, Alexei A. Lapkin, Alexander Mitsos (2023). Gibbs-Duhem-Informed Neural Networks for Binary Activity Coefficient Prediction. Digital Discovery. DOI 10.1039/D3DD00103B. arXiv:2306.07937.
- URL opened: arXiv API record (abstract).
- What was read: abstract.
- Supports: Gibbs-Duhem added "explicitly in the loss function"; consistency "serves as regularization".
- Relevance: HIGH as a clean soft-versus-hard precedent: the same group then moved to a hard construction (L11). Paper 3A mirrors this step for adsorption.

### L11. Rittig and Mitsos 2024 (GE-GNN, hard)
- Citation: Jan G. Rittig, Alexander Mitsos (2024). Thermodynamics-consistent graph neural networks. Chem. Sci. 15, 18504-18512. DOI 10.1039/D4SC04554H. arXiv:2407.18372.
- URLs opened: arXiv API record; Crossref and OpenAlex records.
- What was read: abstract.
- Supports: the network predicts molar excess Gibbs energy and obtains activity coefficients by automatic differentiation; "we do not require additional loss terms" for consistency.
- Relevance: HIGH template. Learns a potential and differentiates it. Liquid mixtures, isothermal binaries.

### L12. Specht et al. 2024 (HANNA v1, activity coefficients)
- Citation: Thomas Specht, Mayank Nagda, Sophie Fellenz, Stephan Mandt, Hans Hasse, Fabian Jirasek (2024). HANNA: hard-constraint neural network for consistent activity coefficient prediction. Chem. Sci. 15, 19777-19786. DOI 10.1039/D4SC05115G. arXiv:2407.18011.
- URL opened: arXiv API record (abstract, journal ref).
- What was read: abstract.
- Supports: "first hard-constraint neural network for predicting activity coefficients"; Gibbs-Duhem and pure-component limits hard-coded in the architecture; 317,421 data points.
- Relevance: HIGH template, including its explicit pure-component limit, which is the analogue of hard-coding the Henry limit.

### L13. Hoffmann et al. 2026 (HANNA, excess Gibbs energy)
- Citation: Marco Hoffmann, Thomas Specht, Quirin Goettl, Jakob Burger, Stephan Mandt, Hans Hasse, Fabian Jirasek (2026). Thermodynamically consistent machine learning model for excess Gibbs energy. Nat. Commun. 17, 3485 (published 14 Apr 2026). DOI 10.1038/s41467-026-71430-y. arXiv:2509.06484 (v1 Sep 2025 titled "A machine-learned expression for the excess Gibbs energy").
- URLs opened: arXiv API record; Crossref record (title, volume 17, article 3485 confirmed); full-text PDF https://www.nature.com/articles/s41467-026-71430-y.pdf (text extracted and searched).
- What was read: full text (methods keyword-level).
- Supports: learns g^E(T, x) with hard constraints; excess enthalpy is obtained from the learned potential by the Gibbs-Helmholtz relation, h^E = -R T^2 d(g^E/RT)/dT, computed by automatic differentiation and trained end-to-end on calorimetric data; second derivatives for LLE stability also by autodiff; Lipschitz regularization.
- Relevance: VERY HIGH as template. It is the exact mathematical analogue of Paper 3A's isosteric heat from a learned potential's temperature derivative, trained jointly on equilibrium and calorimetric data. Paper 3A should cite it as the template and state that the adsorption analogue (q from mu-derivative, Qst from T-derivative of a learned grand potential) has not been built.

### L14. Masi, Stefanou, Vannucci, Maffi-Berthier 2021 (TANN)
- Citation: Filippo Masi, Ioannis Stefanou, Paolo Vannucci, Victor Maffi-Berthier (2021). Thermodynamics-based Artificial Neural Networks for constitutive modeling. J. Mech. Phys. Solids 147, 104277. DOI 10.1016/j.jmps.2020.104277. arXiv:2005.12183.
- URL opened: arXiv API record.
- What was read: abstract.
- Supports: free energy and dissipation rate are network outputs; stress and internal-variable evolution are their autodiff derivatives, "hardwired in the network"; predictions stay consistent "even for unseen data".
- Relevance: HIGH template, and the closest analogue to the LDF-kinetics part of Paper 3A (a dissipation potential guaranteeing a sign-correct rate).

### L15. Amos, Xu, Kolter 2017 (ICNN)
- Citation: Brandon Amos, Lei Xu, J. Zico Kolter (2017). Input Convex Neural Networks. Proc. ICML 2017 (PMLR 70). arXiv:1609.07152.
- URL opened: arXiv API record.
- What was read: abstract.
- Supports: scalar networks with parameter constraints that make the output convex in chosen inputs.
- Relevance: HIGH building block. A grand potential that is convex (or concave) in mu gives a monotone isotherm by construction (dq/dmu = -d2Omega/dmu2 >= 0).

### L16. Wehenkel and Louppe 2019 (UMNN)
- Citation: Antoine Wehenkel, Gilles Louppe (2019). Unconstrained Monotonic Neural Networks. NeurIPS 2019. arXiv:1908.05164.
- URL opened: arXiv API record.
- What was read: abstract.
- Supports: a function is monotone if its derivative is positive; parametrize the derivative by a free network with positive output and integrate.
- Relevance: HIGH building block; this is the alternative route (positive integrand) to a monotone isotherm, and the IsothermODE vector field (L01) could have used it but did not.

### L17. Runje and Shankaranarayana 2023 (constrained monotonic networks)
- Citation: Davor Runje, Sharath M. Shankaranarayana (2023). Constrained Monotonic Neural Networks. arXiv:2205.11775 (v4 May 2023; ICML 2023).
- URL opened: arXiv API record.
- What was read: abstract.
- Supports: sign-constrained weights with paired activation functions give universal monotone approximators.
- Relevance: MEDIUM building block.

### L18. You et al. 2017 (deep lattice networks)
- Citation: Seungil You, David Ding, Kevin Canini, Jan Pfeifer, Maya Gupta (2017). Deep Lattice Networks and Partial Monotonic Functions. NeurIPS 2017. arXiv:1709.06680.
- URL opened: arXiv API record.
- What was read: abstract.
- Relevance: LOW-MEDIUM, alternative monotone architecture.

### L19. Liu, Han, Zhang, Liu 2020 (certified monotonic networks)
- Citation: Xingchao Liu, Xing Han, Na Zhang, Qiang Liu (2020). Certified Monotonic Neural Networks. NeurIPS 2020. arXiv:2011.10219.
- URL opened: arXiv API record.
- What was read: abstract.
- Supports: penalty-trained networks are not provably monotone; monotonicity is certified post hoc by MILP.
- Relevance: MEDIUM. Useful citation for the claim that penalty training "cannot provably guarantee" monotonicity.

### L20. Klein, Fernandez, Martin, Neff, Weeger 2022 (polyconvex ICNN hyperelasticity)
- Citation: Dominik K. Klein, Mauricio Fernandez, Robert J. Martin, Patrizio Neff, Oliver Weeger (2022). Polyconvex anisotropic hyperelasticity with neural networks. J. Mech. Phys. Solids 159, 104703. DOI 10.1016/j.jmps.2021.104703. arXiv:2106.14623.
- URL opened: arXiv API record.
- What was read: abstract.
- Supports: ICNN-based strain-energy potentials whose derivatives are stresses; polyconvexity by construction.
- Relevance: MEDIUM template (learned potential + convexity by construction).

### L21. Linka and Kuhl 2023 (CANN)
- Citation: Kevin Linka, Ellen Kuhl (2023). A new family of Constitutive Artificial Neural Networks towards automated model discovery. Comput. Methods Appl. Mech. Eng. 403, 115731. DOI 10.1016/j.cma.2022.115731. arXiv:2210.02202.
- URL opened: arXiv API record.
- What was read: abstract.
- Supports: input, output and activations designed so thermodynamic consistency and polyconvexity hold inherently; generalizes classical closed-form models, which parallels a learned potential that contains Langmuir/Toth as special cases.
- Relevance: MEDIUM template.

### L22. Winter, Rehner, Esper, Schilling, Bardow 2025 (SPT-PC-SAFT)
- Citation: Benedikt Winter, Philipp Rehner, Timm Esper, Johannes Schilling, Andre Bardow (2025). Understanding the language of molecules: predicting pure component parameters for the PC-SAFT equation of state from SMILES. Digital Discovery (2025, issue 5). arXiv:2309.12404.
- URL opened: arXiv API record.
- What was read: abstract.
- Supports: PC-SAFT embedded in the network so training runs on experimental vapor pressure and density through a physical Helmholtz model; "machine learning models are often not able to handle thermodynamic constraints adequately".
- Relevance: MEDIUM. Hybrid route (network predicts parameters of a physical potential) as opposed to learning the potential itself; the adsorption analogue would be a network predicting Toth/DA parameters, which is consistent but shape-limited.

## C. ML for isosteric heat, multi-temperature isotherms, temperature extrapolation

### L23. Rzepa et al. 2024 (NN for Qst, entropy, Henry constant in zeolites)
- Citation: Christopher Rzepa, Devin Dabagian, Daniel W. Siderius, Harold W. Hatch, Vincent K. Shen, Jeetain Mittal, Srinivas Rangarajan (2024). Elucidating Thermodynamically Driven Structure-Property Relations for Zeolite Adsorption Using Neural Networks. JACS Au 4, 4673-4690. DOI 10.1021/jacsau.4c00429.
- URLs opened: Crossref and OpenAlex records (abstract).
- What was read: abstract.
- Supports: bootstrapped NNs predict adsorption entropy, isosteric heat (MAE 3.14 kJ/mol) and log K_H for more than 3500 adsorbate-zeolite pairs from simulation; each quantity is a separate target.
- Relevance: MEDIUM. ML of Qst exists, but as independent scalar targets at infinite dilution, not as a derivative of a learned isotherm surface.

### L24. Dong, Wu, Cai 2025 (multi-temperature CH4 isotherms, MOFs)
- Citation: Meng-en Dong, Xuanjun Wu, Weiquan Cai (2025). Prediction of Methane Adsorption Isotherms in Metal-Organic Frameworks by Neural Networks: Two-Dimensional Energy Gradient Feature and Masked Learning Mechanism. J. Phys. Chem. B 129, 11333-11349. DOI 10.1021/acs.jpcb.5c05384.
- URLs opened: Crossref and OpenAlex records (abstract).
- What was read: abstract.
- Supports: multi-output NN predicts uptakes at 21 pressures and extended-Langmuir parameters for 17,644 MOFs at 278-338 K (cDFT data); extrapolation to 268 and 358 K "essentially consistent" with cDFT; significant deviations on four experimental MOFs.
- Relevance: MEDIUM. Temperature is a plain input; no Clausius-Clapeyron link, no isosteric heat, no monotonicity guarantee for the 21-point output. Shows temperature transfer is done today by unconstrained regression.

### L25. Anderson, Biong, Gomez-Gualdron 2020 (one NN, many adsorbates)
- Citation: Ryther Anderson, Achay Biong, Diego A. Gomez-Gualdron (2020). Adsorption Isotherm Predictions for Multiple Molecules in MOFs Using the Same Deep Learning Model. J. Chem. Theory Comput. 16, 1271-1283. DOI 10.1021/acs.jctc.9b00940.
- URLs opened: Crossref and OpenAlex records (abstract).
- What was read: abstract.
- Supports: MLP predicts full isotherms of unseen small nonpolar adsorbates in MOFs from alchemical force-field descriptors.
- Relevance: LOW-MEDIUM. Unconstrained pointwise regression baseline family.

### L26. Zhang, Tang, Wang, Lyu, Jiang, Jiang 2023 (ML water adsorption in MOFs)
- Citation: Zhiming Zhang, Hongjian Tang, Mao Wang, Bohui Lyu, Zhongyi Jiang, Jianwen Jiang (2023). Metal-Organic Frameworks for Water Harvesting: Machine Learning-Based Prediction and Rapid Screening. ACS Sustainable Chem. Eng. 11, 8148-8160. DOI 10.1021/acssuschemeng.3c01233.
- URLs opened: Crossref and OpenAlex records (abstract).
- What was read: abstract.
- Supports: compiles experimental MOF water isotherms, trains ML on structural, chemical and operating-condition descriptors to predict water adsorption properties; screens 8000 CoRE MOFs.
- Relevance: MEDIUM. Closest ML work on experimental MOF water isotherms; predicts summary properties, not a thermodynamically consistent q(p,T) surface or Qst.

### L27. Trezza, Bergamasco, Fasano, Chiavazzo 2022 (water, Polanyi rescaling)
- Citation: Giovanni Trezza, Luca Bergamasco, Matteo Fasano, Eliodoro Chiavazzo (2022). Minimal crystallographic descriptors of sorption properties in hypothetical MOFs and role in sequential learning optimization. npj Comput. Mater. 8 (published 3 Jun 2022). DOI 10.1038/s41524-022-00806-7 (Crossref title; the arXiv:2111.09602 title is slightly different: "Minimal set of crystallographic descriptors for sorption properties in hypothetical Metal Organic Frameworks: Role in sequential learning optimization").
- URLs opened: arXiv API record (abstract); Crossref record.
- What was read: abstract; search snippet (not opened) states the Polanyi potential was used to rescale water isotherms to other temperatures.
- Supports: ML on hypothetical MOFs for CO2 and H2O; notes isotherms over full coverage and isosteric heats are often unavailable, which blocks energy-storage objective functions.
- Relevance: MEDIUM. Temperature transfer through the classical Polanyi characteristic curve (a hard physical invariance, but rigid) rather than learned.

### L28. Lin, Zhong, Chen, Deng 2025 (IsothermNet: uptake and heat by GNN)
- Citation: Emily Lin, Yang Zhong, Gang Chen, Sili Deng (2025). Unified physio-thermodynamic descriptors via learned CO2 adsorption properties in metal-organic frameworks. npj Comput. Mater. 11, 225. DOI 10.1038/s41524-025-01700-8.
- URLs opened: Crossref and OpenAlex records (abstract). The code repository (github.com/emilylin3/IsothermNet) was listed in a search but not opened.
- What was read: abstract.
- Supports: CGCNN plus graph attention predicts uptake and heat of adsorption at pressures 0-50 bar for MOFs (GCMC); describes Hads inference as "an unexplored area of study".
- Relevance: MEDIUM. Same group as L01; uptake and heat are separate outputs at one temperature, so nothing forces them to agree.

### L29. Kim, Kim, Bae 2020 (CH4 isotherms at varied temperatures, experimental adsorbents)
- Citation: Seo-Yul Kim, Seung-Ik Kim, Youn-Sang Bae (2020). Machine-Learning-Based Prediction of Methane Adsorption Isotherms at Varied Temperatures for Experimental Adsorbents. J. Phys. Chem. C 124, 19538-19547. DOI 10.1021/acs.jpcc.0c01757.
- URL opened: https://api.crossref.org/works/10.1021/acs.jpcc.0c01757 (title, authors, pages confirmed).
- What was read: metadata only. No abstract was available: the ACS page was not fetched, the OpenAlex quota was used up and the paper is not in Europe PMC.
- Relevance: MEDIUM. An early ML multi-temperature isotherm model for real adsorbents. It must be cited as prior art on temperature transfer. We do not know how it handles constraints.

### L30. Liu, Shen, Cai, Tu, Li 2023 (ML water isotherms and cooling performance)
- Citation: Zhilu Liu, Dongchen Shen, Shanshan Cai, Zhengkai Tu, Song Li (2023). Machine learning-assisted prediction of water adsorption isotherms and cooling performance. J. Mater. Chem. A 11 (36), 19455-19464. DOI 10.1039/d3ta03586g.
- URLs attempted: Crossref record opened (title, authors, year). The RSC landing page returned HTTP 403 to WebFetch and showed a Cloudflare challenge in the browser pane, which was not bypassed.
- What was read: metadata only.
- Relevance: POTENTIALLY HIGH and UNREAD. It is the closest ML work on water isotherms for sorption cooling, which is the Paper 3A application. Read it before submission to confirm whether it handles temperature, Qst or constraints.

### L31. Li, Zhang, Jin, Smit 2026 (MLP for water in Al-MOFs)
- Citation: Y. Li, X. Zhang, X. Jin, B. Smit (2026). Generalized Machine Learning Potentials for Predicting Low-Pressure Water Adsorption in Flexible Al-Based Metal-Organic Frameworks. J. Chem. Theory Comput. DOI 10.1021/acs.jctc.6c01162.
- URL opened: Europe PMC record (abstract).
- What was read: abstract.
- Supports: a fine-tuned MACE potential reproduces experimental water heats of adsorption and Henry coefficients for Al-MOFs. Framework flexibility is essential. UFF underestimates water enthalpies by more than 10 kJ/mol for 74% of materials.
- Relevance: MEDIUM. Works at a different level: an atomistic ML potential, not an isotherm-level potential. Useful as the simulation-route alternative and as evidence that low-pressure water Qst and Henry data in Al-MOFs are hard targets.

### L32. Wu, Cao, Lu, Cai 2023 (NN with physical constraint for Langmuir parameters)
- Citation: Xuanjun Wu, Zijian Cao, Xiuyang Lu, Weiquan Cai (2023). Prediction of methane adsorption isotherms in metal-organic frameworks by neural network synergistic with classical density functional theory. Chem. Eng. J. 459, 141612. DOI 10.1016/j.cej.2023.141612.
- URL opened: Crossref record.
- What was read: metadata only. A search summary, not opened, says the network predicts Langmuir parameters at 298 K with a physical constraint embedded in the loss.
- Relevance: LOW-MEDIUM. Predecessor of L24.

### L33. Anderson and Gomez-Gualdron 2021 (deep learning + IAST)
- Citation: Ryther Anderson, Diego A. Gomez-Gualdron (2021). Deep learning combined with IAST to screen thermodynamically feasible MOFs for adsorption-based separation of multiple binary mixtures. J. Chem. Phys. 154, 234102. DOI 10.1063/5.0048736.
- URL opened: Crossref record (title, venue, article number confirmed).
- What was read: metadata only. A search snippet says an MLP predicts single-component isotherms that feed IAST, and that low-pressure accuracy was critical.
- Relevance: MEDIUM. Mixture consistency comes from IAST, but the pure-component MLP isotherms are unconstrained. The spreading-pressure integral of an unconstrained MLP is not guaranteed to be well behaved, which is a direct argument for a model with a correct Henry limit.

### L34. Dasgupta, R S, Maiti 2025 (mixed-gas ML)
- Citation: Subhadeep Dasgupta, Amal R S, Prabal K. Maiti (2025). Unifying mixed gas adsorption in molecular sieve membranes and MOFs using machine learning. Sep. Purif. Technol. 353, 128477. DOI 10.1016/j.seppur.2024.128477. arXiv:2406.13389.
- URL opened: arXiv API record; Crossref record.
- What was read: abstract.
- Relevance: LOW. Unconstrained regression of pure and binary isotherms.

### L35. Verma and Joshi 2025 (MH-PCTpro)
- Citation: A. Verma, K. Joshi (2025). MH-PCTpro: A machine learning model for rapid prediction of pressure-composition-temperature (PCT) isotherms. iScience, 112251. DOI 10.1016/j.isci.2025.112251.
- URL opened: Europe PMC record (abstract).
- What was read: abstract.
- Supports: ML trained on 237 experimental metal-hydride PCT isotherms (263-653 K). Hydride formation enthalpy and entropy are recovered afterwards from Van't Hoff plots of the predicted plateau pressures.
- Relevance: MEDIUM. A neighbouring sorption field where heats are extracted after the fact from unconstrained multi-temperature predictions. This is the post-hoc Van't Hoff step that Paper 3A replaces with exact derivatives.

### L36. Mayer, Rehner, Seiler, Schilling, Gross, Bardow 2024 (cDFT/PC-SAFT temperature extrapolation)
- Citation: F. Mayer, P. Rehner, J. Seiler, J. Schilling, J. Gross, A. Bardow (2024). Adsorption Modeling Based on Classical Density Functional Theory and PC-SAFT: Temperature Extrapolation and Fluid Transfer. Ind. Eng. Chem. Res. DOI 10.1021/acs.iecr.4c01395.
- URL opened: Europe PMC record (abstract).
- What was read: abstract.
- Supports: a physics-based 1D-DFT/PC-SAFT model parametrized on a single isotherm extrapolates to other temperatures better than Langmuir or Toth, for N2, CH4 and CO2 in MOFs. The abstract calls it a "thermodynamically consistent approach".
- Relevance: HIGH as the non-ML competitor for temperature extrapolation (one isotherm in, other temperatures out). Paper 3A should compare against this idea. This route needs a molecular model of the fluid and pore, and water with hydrogen bonding and MOF steps is a harder case for it.

### L37. Stierle, Bauer, Thiele, Bursik, Rehner, Gross 2024 (3D cDFT with autodiff)
- Citation: R. Stierle, G. Bauer, N. Thiele, B. Bursik, P. Rehner, J. Gross (2024). Classical density functional theory in three dimensions with GPU-accelerated automatic differentiation: Computational performance analysis using the example of adsorption in covalent-organic frameworks. Chem. Eng. Sci., 120380. DOI 10.1016/j.ces.2024.120380.
- URL opened: Crossref search record.
- What was read: metadata only.
- Relevance: LOW-MEDIUM. Automatic differentiation of a physical (not learned) Helmholtz functional for COF adsorption.

### L38. Sammueller, Hermann, de las Heras, Schmidt 2023 (neural functional theory)
- Citation: Florian Sammueller, Sophie Hermann, Daniel de las Heras, Matthias Schmidt (2023). Neural functional theory for inhomogeneous fluids: Fundamentals and applications. PNAS 120, e2312484120. DOI 10.1073/pnas.2312484120. arXiv:2307.04539.
- URLs opened: arXiv API record; Crossref record.
- What was read: abstract.
- Supports: a deep network represents the one-body direct correlation functional, trained on GCMC in random external potentials. The free energy comes from functional line integration and higher correlations from autodiff.
- Relevance: HIGH for how novelty is framed. Learned free-energy functionals are an established route to adsorption in model pores. Paper 3A works at a different level: it learns a macroscopic Omega(mu,T) per material directly from measured isotherms, not a density functional from simulated density profiles.

### L39. Sammueller, Schmidt, Evans 2025 (neural DFT, liquid-gas coexistence)
- Citation: Florian Sammueller, Matthias Schmidt, Robert Evans (2025). Neural Density Functional Theory of Liquid-Gas Phase Coexistence. Phys. Rev. X 15, 011013. DOI 10.1103/PhysRevX.15.011013. arXiv:2408.15835.
- URLs opened: arXiv API record; Crossref record.
- What was read: abstract.
- Supports: the neural functional describes capillary evaporation in a slit pore and drying at a wall for a Lennard-Jones fluid.
- Relevance: MEDIUM-HIGH for novelty context (capillary phenomena in pores from a learned functional).

### L40. Dijkman, Dijkstra, van Roij, Welling, van de Meent, Ensing 2025
- Citation: Jacobus Dijkman et al. (2025). Learning Neural Free-Energy Functionals with Pair-Correlation Matching. Phys. Rev. Lett. 134, 056103. DOI 10.1103/PhysRevLett.134.056103. arXiv:2403.15007.
- URLs opened: arXiv API record; Crossref record.
- What was read: abstract.
- Relevance: MEDIUM for novelty context (a learned Helmholtz functional trained only on bulk g(r)).

### L41. Cheng 2026 (equivariant 3D learned functional, gyroid pore adsorption)
- Citation: Bingqing Cheng (2026). Equivariant learning of a transferable three-dimensional classical density functional. arXiv:2608.13506 (13 Aug 2026).
- URLs opened: arXiv API record; https://arxiv.org/html/2608.13506v1 (adsorption section read via WebFetch).
- What was read: abstract and the adsorption application.
- Supports: a learned 3D excess functional, trained on equilibrium density fields without free-energy labels, predicts an adsorption isotherm of a Lennard-Jones fluid in a soft gyroid pore at T = 1.2 (supercritical), compared with GCMC. There is no temperature series and no real material or experiment.
- Relevance: a HIGH novelty risk, but only in wording. It is the most recent result where a learned free energy gives an adsorption isotherm. It does not address measured isotherms, isosteric heat, Clausius-Clapeyron, kinetics or water on MOFs and COFs.

### L42. Zhou, Bui, Cox 2026 (neural LMFT, confined azeotrope)
- Citation: Katie L. Y. Zhou, Anna T. Bui, Stephen J. Cox (2026). The roles of bulk and surface thermodynamics in the selective adsorption of a confined azeotropic mixture. J. Phys. Chem. B 130 (16), 4455-4466. DOI 10.1021/acs.jpcb.6c00640. arXiv:2601.21591.
- URLs opened: arXiv API record; Europe PMC record.
- What was read: abstract.
- Supports: a neural functional plus mean-field attraction. Bulk thermodynamics are correct "by construction" through a known EOS. Selectivity is scanned over pressure, temperature and composition in slit pores.
- Relevance: MEDIUM. Another learned-functional adsorption study in model pores across temperature.

### L43. Monti, Yatsyshin, Gkagkas, Duncan 2025 (neural corrections inside Helmholtz functional)
- Citation: Edoardo Monti, Peter Yatsyshin, Konstantinos Gkagkas, Andrew B. Duncan (2025). Learning Density Functionals to Bridge Particle and Continuum Scales. arXiv:2512.23840.
- URL opened: arXiv API record.
- What was read: abstract.
- Supports: compact networks embedded in the Helmholtz functional "preserve thermodynamic consistency" and reproduce coexistence and surface tension over a broad temperature range.
- Relevance: MEDIUM template (hybrid: a learned correction inside a thermodynamic potential).

### L44. Ball, Rana, Agrahari, Chatterjee 2023 (ANN configurational free energy, lattice isotherms)
- Citation: Akash Kumar Ball, Swati Rana, Gargi Agrahari, Abhijit Chatterjee (2023). Accelerated calculation of configurational free energy using a combination of reverse Monte Carlo and neural network models: Adsorption isotherm for 2D square and triangular lattices. Comput. Phys. Commun. 285, 108654. DOI 10.1016/j.cpc.2022.108654. arXiv:2212.00287.
- URLs opened: arXiv API record; arXiv PDF (text extracted and searched); Crossref record.
- What was read: abstract and methods (keyword level).
- Supports: ANNs predict local-environment probability distributions from RMC. The chemical potential, and hence the isotherm, follows from a quasi-chemical formula. It covers lattice-gas models and H on Ni(100), simulated only.
- Relevance: MEDIUM. A learned thermodynamic route to isotherms over temperature. The ANN learns distributions, not a differentiable potential, and there are no experiments, no Qst consistency and no MOFs.

### L45. Sanchez Medina, Linke, Stoll, Sundmacher 2023 (GH-GNN)
- Citation: Edgar Ivan Sanchez Medina, Steffen Linke, Martin Stoll, Kai Sundmacher (2023). Gibbs-Helmholtz graph neural network: capturing the temperature dependency of activity coefficients at infinite dilution. Digital Discovery 2. DOI 10.1039/D2DD00142J. arXiv:2212.01199.
- URLs opened: arXiv API record; Crossref record.
- What was read: abstract.
- Supports: GNNs supply the coefficients of a temperature form for ln gamma-infinity derived from Gibbs-Helmholtz (40,219 binaries).
- Relevance: MEDIUM-HIGH template: temperature dependence is hard-wired through a thermodynamic identity. The adsorption analogue, a van't Hoff form for the Henry constant, is a special case of what Paper 3A does at the low-pressure limit.

### L46. Pavsek, Mitsos, Sim, Rittig 2026 (Clapeyron-GNN)
- Citation: Jan Pavsek, Alexander Mitsos, Elvis J. Sim, Jan G. Rittig (2026). Clapeyron Neural Networks for Single-Species Vapor-Liquid Equilibria. arXiv:2602.18313 (20 Feb 2026).
- URL opened: arXiv API record.
- What was read: abstract.
- Supports: the Clapeyron equation is a loss regularizer linking vapor pressure, molar volumes and enthalpy of vaporization in a multitask GNN. Accuracy improves most where data are scarce.
- Relevance: HIGH. The closest neighbouring-field analogue of Clausius-Clapeyron consistency between an equilibrium curve and a heat. But it is soft (a loss term) and for bulk VLE. Both the adsorption analogue and a hard version remain open.

### L47. Leenhouts et al. 2025 (soft vs hard constraint, phase-transition enthalpies)
- Citation: Leenhouts et al. (2025). Thermodynamics-informed graph neural networks for phase transition enthalpies (ESCAPE 35). Systems and Control Transactions 4, 1662-1669. LAPSE:2025.0419.
- URL opened: https://psecommunity.org/wp-content/plugins/wpor/includes/file/2506/LAPSE-2025.0419-1v1.pdf (downloaded with curl because WebFetch was rate-limited; text extracted).
- What was read: full text (keyword level). The title is as given in the search listing. No DOI was found, so the exact title string is not confirmed by Crossref.
- Supports: on 32,023 experimental enthalpies, a soft constraint (sublimation = fusion + vaporization) kept accuracy, while the hard constraint raised sublimation RMSE and MAE by more than 10 kJ/mol.
- Relevance: HIGH as a RISK. This is published evidence that hard thermodynamic constraints can cost accuracy. Paper 3A must report accuracy honestly against penalty fits and explain why a potential-based construction, which constrains structure rather than outputs, need not lose accuracy.

### L48. Navabi and Takoudis 2026 (shape-constrained Bayesian I-splines)
- Citation: Pouyan Navabi, Christos G. Takoudis (2026). Shape-Constrained Bayesian Active Learning of Self-Limiting Saturation Curves. arXiv:2606.26577 (25 Jun 2026).
- URL opened: arXiv API record.
- What was read: abstract.
- Supports: monotone I-spline regression where every posterior curve starts at zero and never decreases, benchmarked on Langmuir, Sips and other saturation forms. The abstract notes that a stationary GP "produces unphysical dips".
- Relevance: MEDIUM. Hard monotonicity for single isotherm-like curves, but no temperature, no heat and no potential.

### L49. Fox, Tran, Nacion, Sharlin, Josephson 2023 (symbolic regression with adsorption constraints)
- Citation: Charles Fox, Neil Tran, Nikki Nacion, Samiha Sharlin, Tyler R. Josephson (2023). Incorporating Background Knowledge in Symbolic Regression using a Computer Algebra System. arXiv:2301.11919.
- URL opened: arXiv API record.
- What was read: abstract. A search summary adds the three constraints: zero loading at zero pressure, a finite initial slope and a non-decreasing isotherm.
- Supports: on historical adsorption data, "hard constraints prevent GA and MCMC SR from searching", while soft constraints help.
- Relevance: MEDIUM. Its list of single-component thermodynamic constraints matches Paper 3A's. It shows hard constraints are hard to impose in symbolic search, a problem a potential-based neural construction avoids.

### L50. Cornelio et al. (AI Descartes)
- Citation: Cristina Cornelio, Sanjeeb Dash, Vernon Austel, Tyler Josephson, Joao Goncalves, Kenneth Clarkson, Nimrod Megiddo, Bachir El Khadir, Lior Horesh. AI Descartes: Combining Data and Theory for Derivable Scientific Discovery. arXiv:2109.01634 (v4 Jan 2023). A PMC listing (PMC10097814, not opened) gives a Nat. Commun. 2023 version.
- URL opened: arXiv API record.
- What was read: abstract.
- Relevance: LOW-MEDIUM. Rederives Langmuir from data plus axioms; not a neural potential.

### L51. Nooraiepour, Masoudi, Song, Hellevang 2025 (adaptive PINN, H2)
- Citation: Mohammad Nooraiepour, Mohammad Masoudi, Zezhang Song, Helge Hellevang (2025). Adaptive Physics-Informed Neural Networks with Multi-Category Feature Engineering for Hydrogen Sorption Prediction in Clays, Shales, and Coals. arXiv:2509.00049 (24 Aug 2025).
- URL opened: arXiv API record.
- What was read: abstract.
- Supports: "integrates classical isotherm models with thermodynamic constraints" through adaptive loss functions, on 155 samples.
- Relevance: MEDIUM. Precursor of L02 and in the same soft-penalty family.

### L52. Kircher and Votsmeier 2026 (thermodynamically consistent NN kinetics)
- Citation: Tim Kircher, Martin Votsmeier (2026). Robust extraction of thermodynamically consistent neural-network-based kinetic models from reactor data: Methanation, methanol synthesis, and dimethyl ether synthesis. J. Catal. 461, 116958. DOI 10.1016/j.jcat.2026.116958.
- URLs: Crossref record opened (truncated abstract via OpenAlex before the quota ran out). The ScienceDirect page failed with a connection reset.
- What was read: metadata and the first sentences of the abstract.
- Relevance: MEDIUM for the kinetics part of Paper 3A (rates that vanish at equilibrium with the correct sign). Details unverified.

### L53. Qu, Yousef, Faney, de Hemptinne, Gallinari 2024 (NNEoS)
- Citation: Jingang Qu, Soleiman Yousef, Thibault Faney, Jean-Charles de Hemptinne, Patrick Gallinari (2024). NNEoS: Neural network-based thermodynamically consistent equation of state for fast and accurate flash calculations. Applied Energy 374, 124025. DOI 10.1016/j.apenergy.2024.124025.
- URL opened: Crossref record.
- What was read: metadata only.
- Relevance: LOW-MEDIUM template.

### L54. Petkovic, Vicent Luna, Dinne, Menkovski, Calero 2025 (SymGNN)
- Citation: Marko Petkovic et al. (2025). Symmetry-Informed Graph Neural Networks for Carbon Dioxide Isotherm and Adsorption Prediction in Aluminum-Substituted Zeolites. arXiv:2503.22737.
- URL opened: arXiv API record.
- What was read: abstract.
- Relevance: LOW. Its constraints come from symmetry, not thermodynamics.

## D. Search log, coverage and blocks

Searches were run on 2026-10-12 and 2026-10-13, with three kinds of tool:
- About 30 WebSearch queries (standard and extended).
- arXiv API fielded searches on abstracts:
  - isotherm AND "thermodynamically consistent" AND neural
  - adsorption AND "grand potential" AND "neural network"
  - isotherm AND "isosteric heat" AND ML/NN
  - adsorption AND isotherm AND "hard constraint"
  - isotherm AND monotonic AND neural
  - "spreading pressure" AND neural
  - adsorption AND isotherm AND "physics-informed"
  - adsorption AND isotherm AND "automatic differentiation"
  - sorption AND Clausius-Clapeyron AND learning/neural
  - MOF AND water AND isotherm AND learning
- Crossref bibliographic searches on the same phrases (journal articles from 2019 on).

These arXiv searches returned zero hits: "grand potential + neural network + adsorption", "isosteric heat + ML + isotherm", "hard constraint + isotherm", "spreading pressure + neural" and "automatic differentiation + isotherm".

Blocked or limited:
- The OpenAlex free daily budget ran out partway through; it supplied abstracts for L01-L28 only.
- The Semantic Scholar API returned "Too Many Requests".
- RSC (J. Mater. Chem. A) returned 403 and a Cloudflare challenge.
- The ScienceDirect connection was reset.
- nature.com pages redirect to a login on WebFetch, but the PDFs downloaded with curl.
- The Claude in Chrome extension was not connected.
- ChemRxiv was searched only through web search, not directly, and Google Scholar was not used.
- Paywalled ACS and Elsevier full texts were not read, except through accepted manuscripts on OSTI.

## E. Closest prior work (ranked)

1. L01 Lin, Wang, Deng 2025, IsothermODE (npj Comput. Mater.). A derivative-based neural isotherm that cites the grand potential and the Gibbs adsorption equation and predicts heat of adsorption. It is not a learned potential. It covers one temperature, learns heat separately, observes monotonicity without guaranteeing it, and uses simulated CO2.
2. L04 Daou et al. 2024 (J. Phys. Chem. C). ML loading at 300 K plus ML Qst(q), combined through integrated Clausius-Clapeyron to any temperature, then IAST. Temperature transfer is consistent with the supplied Qst by construction. However, the two learners are independent, Qst is temperature-independent, there is no monotonicity or Henry guarantee, and the data are simulated alkanes in zeolites.
3. L02/L03/L51 Nooraiepour et al. 2025-2026 (arXiv). PINNs for H2 and CH4 sorption on geological media with monotonicity, saturation and Van't Hoff as loss penalties. They report 98.6% monotonicity satisfaction. There is no learned potential and the network does not give Qst.
4. L13 Hoffmann et al. 2026 HANNA (Nat. Commun.), together with L11 GE-GNN (Rittig and Mitsos 2024) and L07 Rosenberger et al. 2022. This is the template: learn a potential and get properties by autodiff, including an enthalpy from the Gibbs-Helmholtz temperature derivative. None of these is about adsorption.
5. L38-L42 neural classical DFT (Sammueller et al. 2023, 2025; Dijkman et al. 2025; Cheng 2026; Zhou et al. 2026). Learned free-energy functionals that yield adsorption in model pores. They work at a different level (a molecular density functional for simulated Lennard-Jones fluids). Still, they are the closest instance of a learned free energy whose minimization gives adsorption.

Also close:
- L46 Clapeyron-GNN: soft Clapeyron consistency between an equilibrium curve and a heat, for bulk VLE.
- L36 Mayer et al. 2024: physics-based temperature extrapolation from one isotherm.
- L06 Bannoud et al. 2026: the accuracy versus consistency trade-off with penalty PINNs.

## F. Gap statement

Within the sources searched (listed in D), no published or preprinted work trains a neural network that does all of the following:
- represents a scalar adsorbed-phase thermodynamic potential (grand potential, spreading pressure or an equivalent) for a specific adsorbent-adsorbate pair, as a function of chemical potential (or pressure) and temperature;
- obtains both the equilibrium isotherm q*(p,T) and the isosteric heat Qst(q,T) as exact derivatives of that potential;
- therefore guarantees by construction monotonicity in pressure, Clausius-Clapeyron consistency between isotherm and heat, and the Henry limit.

Existing ML isotherm models fall into four groups:
- They regress uptake directly with no constraints (L24-L26, L28, L33, L34).
- They impose monotonicity, saturation and Van't Hoff behaviour as loss penalties, which are only approximately satisfied (L02, L03, L06, L51).
- They learn a derivative with no sign guarantee, at one temperature, with heat as a separate output (L01).
- They join two independent regressors through an integrated Clausius-Clapeyron step with a temperature-independent Qst (L04).

Potential-based hard construction is established in neighbouring fields: excess Gibbs energy (L11-L13), equations of state (L07-L09) and solid mechanics (L14, L20, L21). It also exists in molecular-level learned density functionals for model fluids in model pores (L38-L43). It has not been carried over to:
- macroscopic adsorption equilibrium of real materials;
- water on MOFs or COFs;
- joint training on isotherms and calorimetric or isosteric heats;
- coupling with sign-correct LDF kinetics.

We also found no work that tests such a construction against unconstrained and penalty-constrained fits on measured multi-temperature water isotherms.

Caveats that must travel with this statement:
1. The gap means "not found in the sources searched". It does not prove absence.
2. OpenAlex and Semantic Scholar were rate-limited, and Google Scholar and ChemRxiv were not searched directly. 2026 ChemRxiv preprints and conference papers are therefore the main blind spot.
3. Several potentially relevant papers were read only as metadata: L29 Kim et al. 2020, L30 Liu et al. 2023 (water isotherms for cooling), L32, L33 and L52. L30 in particular must be read in full before the claim appears in print.
4. The claim is about isotherm-level learned potentials. Molecular-level learned free-energy functionals that produce adsorption isotherms already exist (L38-L42) and must be acknowledged so the novelty is not overstated.
5. Classical thermodynamically consistent isotherm families (Langmuir, Toth, DA, generalized Langmuir) and physics models (L36) already give consistency by construction, with a fixed functional form. The contribution is flexibility together with consistency, not consistency itself.

## G. Risks to novelty

- IsothermODE (L01) already uses the grand potential and the Gibbs adsorption equation in a neural isotherm, so the wording can collide. Paper 3A must say precisely what is new: a learned potential, two exact derivatives, temperature dependence and guarantees.
- Daou et al. (L04) already produce temperature-consistent isotherms from ML plus Clausius-Clapeyron. A referee may call Paper 3A an incremental generalization. The answer has three parts: the shared potential means q and Qst cannot disagree; Qst depends on temperature; monotonicity and the Henry limit are hard guarantees demonstrated on experiments.
- Neural cDFT (L38-L42, especially Cheng 2026) already learns a free energy that yields adsorption, so a statistical-mechanics referee may see the idea as known. The distinction must be explicit: macroscopic, per material, trained on measured isotherms and heats, no density profiles.
- There is published evidence that hard constraints can reduce accuracy (L47, and the preference for soft constraints in L49). Paper 3A needs a fair head-to-head with penalty fits and must report any accuracy cost.
- The area is moving fast. Three groups are each one step from an adsorption version:
  - the Nooraiepour group (three preprints in 12 months);
  - the Rittig/Mitsos group (moved from soft Gibbs-Duhem to hard GE-GNN and now soft Clapeyron, L46);
  - the Jirasek/Hasse group (HANNA).
  A hard Clapeyron or adsorption variant from any of them would close the gap quickly.
- Unread items (L29, L30, L32, L52) could contain partial overlaps.

## H. SEEN-ONLY leads (seen in search results, not opened, not used as evidence)

- Wu, Cao, Lu, Cai 2023 CEJ, physics constraint in the loss (content only from a snippet; metadata verified, L32).
- Chaparro and Mueller 2024 Commun. Phys., Helmholtz free energy EOS for fluid and solid phases via ANNs.
- Zhu and Mueller 2020, arXiv:2007.14689, machine-learned EOS replicating SAFT-VR-Mie.
- Chaparro 2025 PhD thesis, Imperial College, "Thermodynamically-guided machine learning for thermophysical property modeling and prediction".
- PI-HySPAC, Int. J. Hydrogen Energy 2026 (ScienceDirect S0360319926032428): pressure and temperature monotonicity penalties for H2 storage in alumina-pillared clays.
- "Hybrid sampling approach to machine-learning potentials for gas adsorption: Hydrogen adsorption in MOF-303", ChemRxiv 10.26434/chemrxiv-2025-dkt8s v2 (Feb 2026).
- MLIP-MC, arXiv:2602.13725, ML interatomic potentials with Widom/GCMC for isosteric heats.
- Soroush et al. 2014 Energy & Fuels, LS-SVM for methane isotherms over temperature on 10 adsorbents.
- Gurnani et al. 2021 Chem. Mater., interpretable ML predictions of methane isotherms in MOFs.
- MOFNet (github.com/Matgen-project/MOFNet), pressure-adaptive isotherm extrapolation.
- GA-ANN for single and multicomponent H2 purification isotherms, Int. J. Hydrogen Energy 2023 (S0360319923040235).
- Deep neural network for H2 purification selectivity trained on IAST, Springer chapter 2023.
- Klein, Roth, Valizadeh, Weeger 2023, Data-Centric Engineering, parametrized polyconvex hyperelasticity.
- Masi and Stefanou 2022 CMAME multiscale TANN; Evolution TANN 2023 JMPS.
- ML-SAFT (Felton, Rasspe-Lange, Leonhard, Mitsos, Lapkin), PCP-SAFT parameter prediction.
- FeOs-torch package (pypi) for differentiable PC-SAFT.
- Thermodynamically consistent NN plasticity, JMPS 2023 (10.1016/j.jmps.2023.105416), and other TC-NN mechanics papers from Crossref listings.
- Communications Physics 2025 interpretable multimodal GNN for CO2 adsorption in MOFs (s42005-025-02399-1).
- AI Descartes Nat. Commun. version (PMC10097814); the arXiv version was used instead.


## I. Follow-up by the lead, 2026-10-13 (closing the agent's blind spots)

- **ChemRxiv-targeted searches** (WebSearch, extended mode, 2026-10-13): "chemrxiv thermodynamically consistent neural network adsorption isotherm isosteric heat" and "chemrxiv 2026 machine learning water adsorption isotherm temperature dependence MOF physics-constrained monotonic". No preprint matching a learned potential with hard monotonicity, Henry and Clausius-Clapeyron consistency was returned. Hits were already in this journal (L-keys for Nooraiepour, IsothermODE) or not relevant (ML interatomic potentials for water in Al-MOFs and NbOFFIVE-1-Ni; Gomez-Gualdron's 2019 multi-molecule isotherm MLP at one temperature). Search engines index ChemRxiv incompletely, so this narrows the blind spot but does not close it. A direct ChemRxiv search in a browser is still owed before submission.
- **L30 Liu et al. 2023**: OpenAlex record (https://api.openalex.org/works/doi:10.1039/D3TA03586G, read 2026-10-13) confirms title, authors, year and closed access. The abstract says the models predict water isotherms "based on uptake pressures and structure properties". A search snippet (SEEN-ONLY) says a random forest was best, on a dataset of 460 adsorbents. A random forest is piecewise constant in pressure, so it has no derivative-based heat and no monotonicity guarantee. The full text is still unread: pubs.rsc.org served a Cloudflare challenge to the built-in browser and returned 403 to WebFetch, and Claude in Chrome was not connected. Status unchanged: must be read in full before submission. Its 460-adsorbent dataset is a possible data source (to the data inventory).
- **L55 Abd Elwadood, Rouxel, Mao, Dumee 2026**, "AI-driven discovery of high-performance metal-organic frameworks for next-gen atmospheric water harvesting", J. Mater. Chem. A, DOI 10.1039/D6TA01583B. OpenAlex record only (closed access; publisher 403). The abstract is generic (MOF screening for water harvesting). From the title and abstract it is screening, not a thermodynamically constrained isotherm model. Metadata-level evidence only.
