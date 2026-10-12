# Paper 3A literature journal: the classical side

Question: the classical thermodynamics that defines the physics of a potential-based neural isotherm for water in MOFs and COFs, the strongest classical competitors, and the known pitfalls.

Read date for every entry: 2026-10-12/13 (session started 2026-10-12, crossed midnight Istanbul time).
Verification method: every DOI was resolved live against the Crossref API (https://api.crossref.org/works/DOI) in this session; abstracts came from OpenAlex (https://api.openalex.org/works/doi:DOI), Semantic Scholar API, or the publisher page; full text from Europe PMC (fullTextXML), the publisher's open page, or an author's institutional copy. No archived copies were used. ACS (pubs.acs.org) served a Cloudflare bot challenge and ScienceDirect refused the built-in browser; those pages were not forced, so claims from them are abstract-level or marked SEEN-ONLY.

Reading levels used below:
- FULL: full text read (or the relevant sections searched in the full text).
- ABSTRACT: abstract read live (publisher, OpenAlex or Semantic Scholar).
- METADATA: only Crossref metadata confirmed; content claim marked SEEN-ONLY.

---

## Part 1. Source entries

### C01. Myers and Prausnitz 1965 (IAST, spreading pressure)
- Citation: A. L. Myers, J. M. Prausnitz, "Thermodynamics of mixed-gas adsorption", AIChE Journal 11(1), 121-127 (1965).
- DOI: 10.1002/aic.690110125 (Crossref confirmed: title, authors, volume 11, pages 121-127).
- URL opened: https://api.crossref.org/works/10.1002/aic.690110125
- Read: METADATA.
- Supports (SEEN-ONLY for content): the standard origin of the ideal adsorbed solution theory, in which the pure-component reduced spreading pressure psi = pi A / RT = integral_0^p q(p')/p' dp' is the quantity that is equalised across components. Paper 3A uses only the pure-component integral, which is a direct consequence of the Gibbs adsorption isotherm (see C02, C03).
- Relevance: canonical citation for the spreading-pressure integral, which is the natural "adsorbed-phase potential" a network can learn.

### C02. Talu and Myers 1988 (rules, limits and consistency of single-gas isotherms)
- Citation: O. Talu, A. L. Myers, "Rigorous thermodynamic treatment of gas adsorption", AIChE Journal 34(11), 1887-1893 (1988).
- DOI: 10.1002/aic.690341114 (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.1002/aic.690341114
- Read: ABSTRACT.
- Supports: the paper is "a summary of rules, limits, and consistency requirements" for single gases and mixtures, and notes that theories "should agree in special cases such as low surface coverage". This is the standard citation for the Henry-law limit and related consistency rules.
- Relevance: the reference a referee expects next to "thermodynamically consistent isotherm" (Henry limit, finite spreading pressure, behaviour at low coverage). The detailed list of rules is SEEN-ONLY (abstract level).

### C03. Myers and Monson 2002 (absolute vs excess; solution thermodynamics of adsorption)
- Citation: A. L. Myers, P. A. Monson, "Adsorption in porous materials at high pressure: theory and experiment", Langmuir 18(26), 10261-10273 (2002).
- DOI: 10.1021/la026399h (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.1021/la026399h
- Read: ABSTRACT.
- Supports: treats gas plus porous solid as a solution; relates absolute properties (natural in theory) to excess properties (measured) "by using an estimate of the helium void volume"; the distinction matters at high pressure (up to 1000 bar in their example).
- Relevance: the excess-vs-absolute correction scales with bulk gas density times pore volume. At water vapour pressures of a few kPa the bulk density is tiny (see C30 for p0 and the ideal-gas check), so the correction is negligible for water; this paper is the source for the general formalism, and the numerical smallness for water is computed in Part 2 rather than quoted.

### C04. Pan, Ritter and Balbuena 1998 (approximations in Clausius-Clapeyron)
- Citation: H. Pan, J. A. Ritter, P. B. Balbuena, "Examination of the approximations used in determining the isosteric heat of adsorption from the Clausius-Clapeyron equation", Langmuir 14(21), 6323-6327 (1998).
- DOI: 10.1021/la9803373 (Crossref confirmed, exact title).
- URL attempted: https://pubs.acs.org/doi/10.1021/la9803373 (Cloudflare challenge, not bypassed); OpenAlex and Semantic Scholar have no abstract (it is a Note).
- Read: METADATA. Content SEEN-ONLY.
- Indirect support: C06 (full text, below) cites this paper (its ref. 25) for the statement that the two Clausius-Clapeyron approximations, negligible adsorbed-phase molar volume and ideal gas, make Clausius-Clapeyron values "differ from the direct experimental data, especially at higher loadings". That sentence is C06's, not Pan et al.'s.
- Relevance: the standard reference for the two approximations behind Qst = -R d ln p / d(1/T) at constant loading. For water at kPa both approximations are excellent; cite C04 via C06.

### C05. Sircar, Mohr, Ristic and Rao 1999 (isosteric heat: theory and experiment)
- Citation: S. Sircar, R. Mohr, C. Ristic, M. B. Rao, "Isosteric heat of adsorption: theory and experiment", Journal of Physical Chemistry B 103(31), 6539-6546 (1999).
- DOI: 10.1021/jp9903817 (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.1021/jp9903817
- Read: ABSTRACT.
- Supports: isosteric heats "can be unambiguously defined by the Gibbsian Surface Excess (GSE) model" and measured by differential calorimetry, with no need for assumptions about the size of the adsorbed phase.
- Relevance: justifies defining Qst from measured (excess) isotherms and calorimetry as the gold standard for checking isotherm-derived Qst.

### C06. Nuhnen and Janiak 2020 (practical guide to isosteric enthalpy in MOFs)
- Citation: A. Nuhnen, C. Janiak, "A practical guide to calculate the isosteric heat/enthalpy of adsorption via adsorption isotherms in metal-organic frameworks, MOFs", Dalton Transactions 49, 10295-10307 (2020).
- DOI: 10.1039/d0dt01784a (Crossref confirmed).
- URLs opened: OpenAlex abstract; full text PDF from the authors' institute (HHU Duesseldorf, Janiak group publication list): https://www.ac1.hhu.de/fileadmin/redaktion/Fakultaeten/Mathematisch-Naturwissenschaftliche_Fakultaet/Chemie/AnorganischeChemie/AnorganischeChemie_I/Publikations-Dateien_274-583/565.pdf
- Read: FULL.
- Supports:
  - Two or three isotherms with dT <= 20 K (two) or about 10 K (three) are the basis for Clausius-Clapeyron or virial analysis.
  - Both isotherms "should be fitted with the same continuous function" before reading off isosteres.
  - Because the enthalpy is temperature dependent, spacing larger than 20 K "will artificially introduce errors"; three isotherms recommended so that a standard error of the ln p vs 1/T regression can be reported.
  - Clausius-Clapeyron rests on negligible adsorbed-phase molar volume and ideal gas (citing C04).
  - Virial route: ln p = ln n + (1/T) sum a_i n^i + sum b_i n^i, Hads(n) = R sum a_i n^i; zero-coverage value is R a0 and is strongly correlated with the lowest-coverage point included: the same data gave about -54 or -33 kJ/mol depending on which low-pressure points were excluded.
  - "No extrapolation beyond the experimental data range should be done."
  - Calorimetry comparison: for CO2 in MIL-100(Cr) isotherm-derived and microcalorimetric values agree at low coverage but deviate considerably with loading; isotherm values lie substantially below calorimetry.
  - Terminology: Qst = -Hads; Qst > 0.
- Relevance: the most-cited MOF tutorial on Qst. It documents exactly the failure modes Paper 3A claims to remove (per-temperature fits, extrapolation, sensitivity to low-coverage points). Its data are CO2/SO2/H2, not water: note this when citing.

### C07. Siperstein, Avendano, Ortiz and Gil-Villegas 2021 (analytic Qst from isotherm models)
- Citation: F. R. Siperstein, C. Avendano, J. J. Ortiz, A. Gil-Villegas, "Analytic expressions for the isosteric heat of adsorption from adsorption isotherm models and two-dimensional SAFT-VR equation of state", AIChE Journal 67(3), e17186 (2021). Open access.
- DOI: 10.1002/aic.17186 (Crossref confirmed).
- URL opened: https://aiche.onlinelibrary.wiley.com/doi/full/10.1002/aic.17186
- Read: FULL (HTML full text).
- Supports:
  - Clausius-Clapeyron Qst "is only valid for pure components and perfect gases"; Qst equals the differential enthalpy of adsorption for pure components at low pressure where the ideal gas holds.
  - Fitting N2O on biochar at six temperatures with Langmuir, virial, Freundlich, Sips, Toth, dual-site Langmuir and 2D-SAFT-VR: all models agree on Qst "only in the region where no extrapolation" is needed; zero-coverage Qst varies strongly with model choice although all isotherm fits were good.
  - Dual-site Langmuir gave an "unphysical maxima at low coverage" in Qst; Freundlich and Sips Qst "diverged at low coverages"; Freundlich and Sips have no finite Henry slope at zero pressure, whereas Toth does.
  - Temperature-dependent saturation capacity (thermal expansion coefficient of the adsorbed phase) changes the Qst expression.
- Relevance: direct evidence that standard classical isotherm families violate the Henry limit (Freundlich, Sips) and produce unphysical Qst shapes (dual-site Langmuir) when fitted per temperature; the strongest published motivation for a model whose Qst is analytic and whose Henry limit is built in. Not water: say so.

### C08. Rehner 2026 (thermodynamically consistent enthalpies of adsorption)
- Citation: P. Rehner, "Thermodynamically consistent enthalpies of adsorption of mixtures from classical density functional theory", Journal of Physical Chemistry B 130, 3582-3589 (2026).
- DOI: 10.1021/acs.jpcb.6c00492 (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.1021/acs.jpcb.6c00492 (abstract; listed as hybrid open access but pubs.acs.org served a bot challenge).
- Read: ABSTRACT.
- Supports: cDFT gives "noise-free derivatives" and a "thermodynamically fully consistent model" from which enthalpies follow; the paper revisits the definition of the enthalpy of adsorption "from an energy balance perspective and in the context of the Clausius-Clapeyron relation". Demonstrated for PC-SAFT fluids in a model slit pore.
- Relevance: the closest physics-side precedent for "derive the enthalpy as a derivative of one consistent free-energy model"; Paper 3A does the same with a learned potential instead of cDFT. Cite as conceptual precedent; it is not a water or MOF data paper.

### C09. Sircar and Hufton 2000 (why LDF works)
- Citation: S. Sircar, J. R. Hufton, "Why does the linear driving force model for adsorption kinetics work?", Adsorption 6, 137-147 (2000).
- DOI: 10.1023/A:1008965317983 (Crossref confirmed).
- URL opened: https://link.springer.com/article/10.1023/A:1008965317983
- Read: ABSTRACT.
- Supports: LDF is used "because it is simple, analytic, and physically consistent"; particle-level kinetic detail is averaged out in heterogeneous solids, breakthrough curves and process efficiency.
- Relevance: justification for coupling the learned equilibrium q*(p,T) to LDF dq/dt = k (q* - q). Sign correctness of LDF follows from monotonic q*: if q < q*(p,T) uptake increases. The thermodynamic (chemical potential) driving-force version is SEEN-ONLY here.

### C10. Glueckauf 1955 (origin of LDF coefficient)
- Citation: E. Glueckauf, "Theory of chromatography. Part 10. Formulae for diffusion into spheres and their application to chromatography", Transactions of the Faraday Society 51, 1540-1551 (1955).
- DOI: 10.1039/tf9555101540 (Crossref confirmed).
- URL opened: https://api.crossref.org/works/10.1039/tf9555101540
- Read: METADATA. Content (the k = 15 D/R^2 approximation) SEEN-ONLY.
- Relevance: standard citation for the LDF approximation to Fickian diffusion in spheres.

### C11. Liu, Wang and Kapteijn 2020 (Chem. Rev., water and MOFs)
- Citation: X. Liu, X. Wang, F. Kapteijn, "Water and metal-organic frameworks: from interaction toward utilization", Chemical Reviews 120(16), 8303-8377 (2020).
- DOI: 10.1021/acs.chemrev.9b00746 (Crossref confirmed). PMC7453405.
- URL opened: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7453405/fullTextXML
- Read: FULL (searched sections).
- Supports:
  - Following Polanyi and Dubinin, the adsorption potential A(p/p0,T) captures the temperature and pressure dependence of water uptake with one variable; "often, the Dubinin-Astakhov relation is used, whereby all isotherms collapse onto a single characteristic curve" with a step at a MOF-specific characteristic energy E.
  - Characteristic curves are "conveniently used for modeling of cycle performance" (refs 7, 334, 335 there).
  - Table footnote: heat-of-adsorption values below the heat of condensation (about 40.7 kJ/mol) "seem physically unrealistic".
  - Capillary condensation in pores wider than a critical diameter Dc that depends on sigma (water van der Waals diameter 0.28 nm), Tc (647 K) and T; Dc is "around 2.0 nm" at room temperature, and wider pores show condensation with hysteresis; "a hysteresis loop is always found" there because the adsorption branch "does not reach thermodynamic equilibrium". The equation itself (their eq. 2) is an image in the XML and was not read; the form Dc = 4 sigma Tc/(Tc - T) gives 2.08 nm at 298 K and is consistent with their number, but treat the exact form as SEEN-ONLY.
  - Examples with hysteresis: MIL-101(Cr) mesoporous cages (heat 44.5 kJ/mol near the evaporation enthalpy), MIL-53(Al)-OH breathing, Y-shp-MOF-5 superclusters, UiO-66 (defects, pore sizes). CAU-10(Al)-H: no hysteresis, average isosteric heat about 54 kJ/mol.
- Relevance: anchor review for water MOFs; establishes that the characteristic-curve approach is the field's default temperature model (therefore the main competitor), supplies a physical sanity bound on Qst, and the hysteresis taxonomy.

### C12. de Lange, Verouden, Vlugt, Gascon and Kapteijn 2015 (adsorption-driven heat pumps with MOFs)
- Citation: M. F. de Lange, K. J. F. M. Verouden, T. J. H. Vlugt, J. Gascon, F. Kapteijn, "Adsorption-driven heat pumps: the potential of metal-organic frameworks", Chemical Reviews 115(22), 12205-12250 (2015).
- DOI: 10.1021/acs.chemrev.5b00059 (Crossref confirmed).
- URL opened: OpenAlex record (abstract field contains only the landing-page boilerplate); pubs.acs.org blocked.
- Read: METADATA. Content SEEN-ONLY.
- Indirect support: C11 (full text) uses "as calculated according to ref (7)" (this paper) for average enthalpy of adsorption, and cites it for characteristic-curve cycle modelling.
- Relevance: the standard Delft treatment of water-MOF thermodynamics for heat pumps; must be read in full before submission.

### C13. Aristov 2023 (potential theory of adsorption for heat transformation)
- Citation: Yu. I. Aristov, "Applying the potential theory of adsorption for adsorptive heat transformation", Adsorption 29, 225-235 (2023).
- DOI: 10.1007/s10450-023-00385-z (Crossref confirmed).
- URL opened: https://link.springer.com/article/10.1007/s10450-023-00385-z
- Read: ABSTRACT plus visible nomenclature and reference list.
- Supports: the article "examines how the fundamental potential theory of adsorption is used" in adsorbent design and cycle harmonisation. Nomenclature lists the Dubinin adsorption potential A, characteristic energy E, heterogeneity parameter n (DA), and volume expansion coefficient alpha (the temperature correction to the limiting volume), and affinity coefficient beta.
- Relevance: the Aristov group's own statement of the method; the presence of an expansion coefficient term shows that the "invariant" curve is in practice corrected for liquid-density changes. Quantitative accuracy claims are SEEN-ONLY.

### C14. Solovyeva, Krivosheeva, Gordeeva and Aristov 2021 (MIL-160 water, characteristic curve and Qst)
- Citation: M. V. Solovyeva, I. V. Krivosheeva, L. G. Gordeeva, Yu. I. Aristov, "MIL-160 as an adsorbent for atmospheric water harvesting", Energies 14(12), 3586 (2021). Open access.
- DOI: 10.3390/en14123586 (Crossref confirmed).
- URL opened: https://www.mdpi.com/1996-1073/14/12/3586/htm (via the built-in browser; curl was refused).
- Read: FULL (searched).
- Supports:
  - Water isotherms measured at 20, 35 and 50 C; isosteric heat from ln P vs 1/T isosteres: 49 to 52 +/- 1 kJ/mol at w = 0.05-0.25 g/g, slightly above the condensation heat 43.9 kJ/mol at 303 K.
  - Isobars plotted vs Delta F = -RT ln(P/P0(T)) "merged into one characteristic curve", so MIL-160 "obeyed the Polanyi principle of temperature invariance"; the curve was fitted by an empirical sum of two logistic steps plus a linear term (7 parameters).
  - The invariance claim is visual (a figure), with no reported deviation metric.
- Relevance: a clean, typical example of the classical workflow Paper 3A competes with (characteristic curve fitted with a flexible empirical function; Qst from isosteres). Also a candidate dataset (three temperatures). Pitfall: invariance asserted without a number.

### C15. Henninger, Jeremias, Kummer and Janiak 2012 (MOFs for adsorption heat pumps)
- Citation: S. K. Henninger, F. Jeremias, H. Kummer, C. Janiak, "MOFs for use in adsorption heat pump processes", European Journal of Inorganic Chemistry 2012(16), 2625-2634 (2012).
- DOI: 10.1002/ejic.201101056 (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.1002/ejic.201101056
- Read: ABSTRACT.
- Supports: water is the preferred working fluid; suitability is "governed by the microporosity, hydrophilicity, and hydrothermal stability" of the sorbent; MOFs compared with silica gel, aluminophosphates, zeolites.
- Relevance: frames the heat-transformation community that uses characteristic curves for water MOFs.

### C16. Jeremias, Froehlich, Janiak and Henninger 2014 (water and methanol on MOFs for heat transformation)
- Citation: F. Jeremias, D. Froehlich, C. Janiak, S. K. Henninger, "Water and methanol adsorption on MOFs for cycling heat transformation processes", New Journal of Chemistry 38, 1846-1852 (2014).
- DOI: 10.1039/c3nj01556d (Crossref confirmed).
- URL opened: OpenAlex (one-sentence abstract); RSC HTML refused curl.
- Read: ABSTRACT (one sentence). Content beyond that SEEN-ONLY.
- Relevance: a multi-MOF water dataset from the Fraunhofer ISE/Janiak line; check SI for multi-temperature isotherms.

### C17. Furukawa et al. 2014 (water adsorption in 23 porous materials)
- Citation: H. Furukawa, F. Gandara, Y.-B. Zhang, J. Jiang, W. L. Queen, M. R. Hudson, O. M. Yaghi, "Water adsorption in porous metal-organic frameworks and related materials", Journal of the American Chemical Society 136(11), 4369-4381 (2014).
- DOI: 10.1021/ja500330a (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.1021/ja500330a (green OA copy at EPFL Infoscience listed).
- Read: ABSTRACT.
- Supports: three criteria for water sorbents: condensation pressure in pores, uptake capacity, recyclability/water stability; 23 materials, 20 MOFs; MOF-801-P and MOF-841 best.
- Relevance: canonical water-MOF dataset and the "step position" criterion that the characteristic curve encodes.

### C18. Bering, Dubinin and Serpinskii 1972 (error of assuming characteristic-curve invariance)
- Citation: B. P. Bering, M. M. Dubinin, V. V. Serpinskii, "Error of calculating the temperature dependence of adsorption on the assumption of an invariance of the characteristic curve", Bulletin of the Academy of Sciences of the USSR, Division of Chemical Science 21, 384-386 (1972).
- DOI: 10.1007/BF00857806 (Crossref confirmed).
- Read: METADATA. Content SEEN-ONLY.
- Relevance: the title alone shows that the founders of the theory quantified the error of temperature invariance. Highest-priority SEEN-ONLY lead for item 3.

### C19. Lehmann, Beckert, Nonnen, Glaeser, Kolditz and Nagel 2017 (Dubinin-Polanyi prediction vs experiment)
- Citation: C. Lehmann, S. Beckert, T. Nonnen, R. Glaeser, O. Kolditz, T. Nagel, "Water loading lift and heat storage density prediction of adsorption heat storage systems using Dubinin-Polanyi theory: comparison with experimental results", Applied Energy 207, 274-282 (2017).
- DOI: 10.1016/j.apenergy.2017.07.008 (Crossref confirmed).
- URL attempted: ScienceDirect (refused); OpenAlex and Semantic Scholar have no abstract.
- Read: METADATA. Content SEEN-ONLY.
- Relevance: one of very few papers whose title promises a quantitative test of DP predictions against experiment for water (zeolite-based heat storage). High-priority SEEN-ONLY lead.

### C20. Teicht 2023 (modified potential theory when invariance fails)
- Citation: C. Teicht, "An easy-to-use modification of the potential theory of adsorption and creation of an adsorbent data base", Energy 263, 125968 (2023).
- DOI: 10.1016/j.energy.2022.125968 (Crossref confirmed).
- Read: METADATA. A web-search snippet (not the paper) stated the method applies "when the temperature invariance ... is not satisfied"; SEEN-ONLY.
- Relevance: evidence that the heat-transformation community already needs corrections to invariance.

### C21. Preissler-Kurzhoefer et al. 2022 (Dubinin-based universal adsorption theory, flexible MOFs)
- Citation: H. Preissler-Kurzhoefer, M. Lange, A. Kolesnikov, J. Moellmer, O. Erhart, M. Kobalz et al., "Hydrocarbon sorption in flexible MOFs, Part I: thermodynamic analysis with the Dubinin-based universal adsorption theory (D-UAT)", Nanomaterials 12(14), 2415 (2022).
- DOI: 10.3390/nano12142415 (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.3390/nano12142415
- Read: ABSTRACT.
- Supports: D-UAT condenses data to pore volume, reduced enthalpy and (for flexible frameworks) reduced free-energy differences; as a prediction tool it "depends on rough assumptions, and thus is not recommended".
- Relevance: hydrocarbons, not water, but the authors of a Dubinin-based method themselves advise against using it predictively for flexible MOFs.

Update to C18 (later in the session): the Springer page https://link.springer.com/article/10.1007/BF00857806 shows the paper's Conclusions (read: CONCLUSIONS paragraph, which serves as abstract). They state (1) that for a given permissible maximum error, the range of fillings where temperature invariance of the Gibbs free energy at constant filling is usable "can be much broader" than where it strictly holds, and (2) that numerous systems violate invariance at every filling, yet calculations postulating it "still leads to completely satisfactory results". This is the founders' own verdict: invariance is an approximation that works in practice, not an exact law.

### C22. Myers 2002 (thermodynamics of adsorption in porous materials: immersion free energy instead of spreading pressure)
- Citation: A. L. Myers, "Thermodynamics of adsorption in porous materials", AIChE Journal 48(1), 145-160 (2002).
- DOI: 10.1002/aic.690480115 (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.1002/aic.690480115
- Read: ABSTRACT.
- Supports: for micropores the 2-D variables (spreading pressure, surface area) "must be abandoned"; adsorption is split into isothermal compression of the gas and isothermal immersion of clean adsorbent; Gibbs free energy, enthalpy and entropy follow from solution thermodynamics.
- Relevance: this is the formal basis for Paper 3A's potential. The immersion (grand) free energy per mass of adsorbent, Omega(p,T) = -RT integral_0^p n(p',T) d ln p', is the same integral as the IAST reduced spreading pressure (C01) but does not require a surface area. Paper 3A should call its learned quantity the grand potential (or immersion free energy), citing C22, and avoid calling it a spreading pressure for MOFs.

### C23. Myers 2004 book chapter (Thermodynamics of adsorption)
- Citation: A. L. Myers, "Thermodynamics of adsorption", in T. M. Letcher (ed.), Chemical Thermodynamics for Industry, Royal Society of Chemistry, pp. 243-253 (2004).
- DOI: 10.1039/9781847550415-00243 (Crossref confirmed).
- Read: METADATA. Content SEEN-ONLY.
- Relevance: the chapter the brief named; cite alongside C22 only after reading it.

### C24. Sircar 1999 (Gibbsian surface excess revisited)
- Citation: S. Sircar, "Gibbsian surface excess for gas adsorption revisited", Industrial and Engineering Chemistry Research 38(10), 3670-3682 (1999).
- DOI: 10.1021/ie9900871 (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.1021/ie9900871
- Read: ABSTRACT.
- Supports: the Gibbsian surface excess is "the true experimental variable" of all conventional methods; surface potentials, isosteric heats and heat capacities can be estimated from it, and thermodynamic consistency tests can be formulated, "no need to estimate actual amounts adsorbed".
- Relevance: lets Paper 3A train on measured (excess) water uptakes directly and define the potential and Qst on that basis, without an absolute-adsorption conversion.

### C25. Talu and Myers 2001 (Gibbs dividing surface; when absolute and excess differ)
- Citation: O. Talu, A. L. Myers, "Molecular simulation of adsorption: Gibbs dividing surface and comparison with experiment", AIChE Journal 47(5), 1160-1168 (2001).
- DOI: 10.1002/aic.690470521 (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.1002/aic.690470521
- Read: ABSTRACT.
- Supports: "at low temperature near the normal boiling point" simulations compare directly with experiment; conversion from absolute to excess (via helium pore volume) is needed for gases "near or above its critical temperature".
- Relevance: the citable statement that the excess/absolute distinction is a near- or super-critical issue. Water vapour at 288-353 K and below 50 kPa is deeply subcritical (Tc = 647.096 K, C30), so excess equals absolute to within the tiny bulk-vapour term computed in Part 2.

### C26. Shimizu and Matubayasi 2021a (temperature dependence of sorption; when a characteristic curve exists)
- Citation: S. Shimizu, N. Matubayasi, "Temperature dependence of sorption", Langmuir 37(37), 11008-11017 (2021). CC BY.
- DOI: 10.1021/acs.langmuir.1c01576 (Crossref confirmed).
- URL opened: https://pure.york.ac.uk/portal/en/publications/temperature-dependence-of-sorption/ (York repository record with abstract; the PDF link and pubs.acs.org served bot challenges).
- Read: ABSTRACT.
- Supports: the collapse of isotherms onto a "characteristic curve" against adsorption potential "has not been given a clear explanation"; a characteristic curve exists "when sorbate number increment contributes purely energetically", whereas the correlation between sorbate number and entropy "drives the temperature dependence" of an isotherm; explains opposite temperature dependence of water on carbons with uniform vs broad pore size distributions; criticises routine use of BET and GAB beyond their premises.
- Relevance: the sharpest theoretical statement of when the main classical competitor (temperature-invariant characteristic curve) must fail: whenever the adsorbed water has a loading-dependent entropy beyond the liquid reference. A learned potential F(q,T) with free temperature dependence can represent that entropic term; the characteristic curve cannot. This is the physics argument for Paper 3A's temperature-extrapolation test.

### C27. Shimizu and Matubayasi 2021b (sorption: statistical thermodynamic fluctuation theory)
- Citation: S. Shimizu, N. Matubayasi, "Sorption: a statistical thermodynamic fluctuation theory", Langmuir 37(24), 7380-7391 (2021).
- DOI: 10.1021/acs.langmuir.1c00742 (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.1021/acs.langmuir.1c00742
- Read: ABSTRACT.
- Supports: multiple isotherm models with different mechanisms "often fit an experimental isotherm equally well"; BET and GAB fit isotherms that do not satisfy their assumptions; an isotherm containing Langmuir, BET and GAB as special cases follows without assuming sites or layers.
- Relevance: the fluctuation route ties the isotherm slope to number fluctuations (d<N>/d ln a = <dN^2> >= 0), which is the statistical-mechanical statement of monotonicity/stability (exact relation stated in Part 2, derived from standard grand-canonical identities; the abstract does not quote it). Also supports the referee-proof claim that a good fit says little about mechanism.

### C28. Shimizu and Matubayasi 2021c (cooperative sorption on porous materials)
- Citation: S. Shimizu, N. Matubayasi, "Cooperative sorption on porous materials", Langmuir 37(34), 10279-10290 (2021).
- DOI: 10.1021/acs.langmuir.1c01236 (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.1021/acs.langmuir.1c01236
- Read: ABSTRACT.
- Supports: a cooperative isotherm generalising the Hill isotherm, "without the need for assumptions on adsorption sites, layers, and pore geometry"; parameters are the cooperative number of sorbates and the free energy of transfer from saturated vapour to the interface.
- Relevance: a modern, thermodynamically grounded S-shaped (type V) model for water steps; a candidate classical baseline. Its free energy of transfer from saturated vapour is a characteristic-curve-like variable.

### C29. Shimizu and Matubayasi 2024 (sorption hysteresis: fluctuation theory)
- Citation: S. Shimizu, N. Matubayasi, "Sorption hysteresis: a statistical thermodynamic fluctuation theory", Langmuir 40, 11504-11515 (2024).
- DOI: 10.1021/acs.langmuir.4c00606 (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.1021/acs.langmuir.4c00606
- Read: ABSTRACT.
- Supports: no unified approach has modelled hysteresis and its energetics; standard capillary-condensation and interfacial-EOS approaches "have not proved to be up to the task"; separate analytic branches are parameterised by free energy per molecule in pore clusters and cluster size; covers IUPAC H1, H2(a), H2(b) and types IV and V.
- Relevance: if Paper 3A treats hysteretic COF/MOF data, the honest classical comparator is a two-branch model; a single equilibrium potential represents at most one branch (see Part 2).

### C30. IAPWS SR1-86(1992) (saturation properties; the p0(T) correlation)
- Citation: IAPWS, "Revised supplementary release on saturation properties of ordinary water substance", SR1-86(1992), St. Petersburg, September 1992. Underlying paper: W. Wagner, A. Pruss, J. Phys. Chem. Ref. Data 22, 783-787 (1993), DOI 10.1063/1.555926 (Crossref confirmed).
- URLs opened: https://iapws.org/technical-guidance/release/Supp-sat (release page) and https://iapws.org/technical-guidance/release/Supp-sat.download (the PDF, 7 pages, read in full).
- Read: FULL.
- Content recorded exactly:
  - Constants: Tc = 647.096 K, pc = 22.064 MPa, rho_c = 322 kg/m3.
  - Vapour pressure, eq. (1): ln(p/pc) = (Tc/T) [a1 tau + a2 tau^1.5 + a3 tau^3 + a4 tau^3.5 + a5 tau^4 + a6 tau^7.5], tau = 1 - T/Tc, with a1 = -7.85951783, a2 = 1.84408259, a3 = -11.7866497, a4 = 22.6807411, a5 = -15.9618719, a6 = 1.80122502.
  - Saturated vapour density, eq. (3): ln(rho''/rho_c) = c1 tau^(2/6) + c2 tau^(4/6) + c3 tau^(8/6) + c4 tau^(18/6) + c5 tau^(37/6) + c6 tau^(71/6), with c1 = -2.03150240, c2 = -2.68302940, c3 = -5.38626492, c4 = -17.2991605, c5 = -44.7586581, c6 = -63.9201063.
  - Validity: 273.16 K <= T <= 647.096 K (triple point to critical point), ITS-90.
  - Verification Table 1: T = 273.16 K: p = 611.657 Pa, dp/dT = 44.436693 Pa/K, rho' = 999.789, rho'' = 0.00485426 kg/m3. T = 373.1243 K: p = 0.101325 MPa, dp/dT = 3.616e3 Pa/K, rho'' = 0.597586 kg/m3.
- Verification done in this session: a direct implementation of eqs. (1) and (3) reproduced 611.657 Pa, dp/dT = 44.4367 Pa/K and rho'' = 0.004854 kg/m3 at 273.16 K, and 101325.0 Pa and 0.597586 kg/m3 at 373.1243 K.
- Values computed from eq. (1) for Paper 3A (not table values in the release; reproduce with the code): 10 C 1228.11 Pa; 15 C 1705.68 Pa; 20 C 2339.19 Pa; 25 C 3169.82 Pa; 30 C 4246.92 Pa; 35 C 5629.06 Pa; 40 C 7385.11 Pa; 50 C 12352.48 Pa; 60 C 19947.38 Pa; 70 C 31202.20 Pa; 80 C 47415.78 Pa.
- Relevance: the p0(T) every characteristic-curve competitor and every relative-humidity conversion needs. Using the same p0(T) for all models removes a hidden source of disagreement. Note that some ML/MOF papers use Antoine fits instead: C35 quotes ps(T0 = 298 K) = 3157 Pa, 866.2 Pa at 278 K and 4231.6 Pa at 303 K, while eq. (1) gives 3141.6, 863.4 and 4210.5 Pa at those temperatures (0.3 to 0.5% high). A 0.5% error in p0 shifts A = RT ln(p0/p) by RT x 0.005, about 12 J/mol at 298 K: small against characteristic energies of several kJ/mol, but it is a systematic, temperature-dependent bias that can masquerade as non-invariance.

### C31. IAPWS R6-95(2018) (IAPWS-95 formulation, release text)
- Citation: IAPWS, "Revised release on the IAPWS Formulation 1995 for the thermodynamic properties of ordinary water substance for general and scientific use", R6-95(2018), Prague, September 2018.
- URLs opened: https://iapws.org/technical-guidance/release/IAPWS-95 and https://iapws.org/technical-guidance/release/IAPWS-95.download (PDF read for sections 4-7 and Table 8).
- Read: FULL (relevant sections).
- Supports: saturation properties from the Helmholtz equation via the phase-equilibrium (Maxwell) condition are "thermodynamically consistent" with the single-phase region; the simple SR1-86 equations are "not identical" with IAPWS-95 values "but agree with them within the uncertainties" of the simple equations. Table 8 at T = 275 K: p_sigma = 0.698451167e-3 MPa, rho'' = 0.550664919e-2 kg/m3.
- Cross-check done in this session: SR1-86 eq. (1) gives 698.436 Pa at 275 K vs IAPWS-95 698.451 Pa (difference 0.002%). IAPWS-95 Table 8 values give Z = p/(rho'' R T) = 0.99937 for saturated vapour at 275 K with R = 0.46151805 kJ/(kg K) from the release.
- Relevance: justifies using SR1-86 for p0(T) and records that the difference from full IAPWS-95 is far below isotherm measurement error.

### C32. Wagner and Pruss 2002 (IAPWS-95 paper)
- Citation: W. Wagner, A. Pruss, "The IAPWS formulation 1995 for the thermodynamic properties of ordinary water substance for general and scientific use", Journal of Physical and Chemical Reference Data 31(2), 387-535 (2002).
- DOI: 10.1063/1.1461829 (Crossref confirmed: volume 31, pages 387-535).
- Read: METADATA (the formulation itself was read through the IAPWS release C31).
- Relevance: the archival citation for IAPWS-95.

### C33. Oppenheim, Yang, Dinakar and Dinca 2025 (Mg-SU-102: characteristic curves from 15 to 55 C)
- Citation: J. J. Oppenheim, Z. Yang, B. Dinakar, M. Dinca, "High-capacity water sorbent cycles without hysteresis under dry conditions", Nature Communications 16, 4297 (2025) (article number confirmed on Crossref).
- DOI: 10.1038/s41467-025-59551-2 (Crossref confirmed). PMC12062333.
- URL opened: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12062333/fullTextXML
- Read: FULL (searched).
- Supports:
  - Isotherms 15 to 55 C; characteristic curves A = RT ln(P0/P) "overlap well, with a slight shift towards lower energies at higher temperatures", attributed to "entropic contributions from capillary condensation".
  - No significant hysteresis-loop growth at low temperature in 15-55 C.
  - Isosteric enthalpy from 25, 30, 35, 40 C isotherms only, "as only the isotherms within this temperature range have sufficient data points for reliable fits"; -49 to -56 kJ/mol in the step.
- Relevance: (i) the cleanest recent, open, multi-temperature MOF water dataset with an explicit statement that invariance is approximate and drifts systematically with T: exactly the residual a learned potential could capture; (ii) evidence of the practical data limit for Clausius-Clapeyron (only a subset of temperatures usable).

### C34. Solovyeva et al. 2018 (MOF-801 water for adsorption cooling)
- Citation: M. V. Solovyeva, L. G. Gordeeva, T. A. Krieger, Yu. I. Aristov, "MOF-801 as a promising material for adsorption cooling: equilibrium and dynamics of water adsorption", Energy Conversion and Management 174, 356-363 (2018).
- DOI: 10.1016/j.enconman.2018.08.032 (Crossref confirmed).
- URL opened: Semantic Scholar API record (abstract).
- Read: ABSTRACT.
- Supports: equilibrium and dynamics of water on MOF-801; cooling at evaporator 5 C with adsorption at 30 C; regeneration 80-85 C; uptake swing 0.21 g/g. The abstract does not state invariance; whether a characteristic curve was used is SEEN-ONLY.
- Relevance: Aristov-group cycle analysis for a canonical Zr MOF; candidate dataset.

### C35. Trezza, Bergamasco, Fasano and Chiavazzo 2021 (Polanyi rescaling of water isotherms in ML screening)
- Citation: G. Trezza, L. Bergamasco, M. Fasano, E. Chiavazzo, "Minimal set of crystallographic descriptors for sorption properties in hypothetical metal organic frameworks: role in sequential learning optimization", arXiv:2111.09602 (2021).
- URL opened: https://arxiv.org/pdf/2111.09602 (v1 PDF, read).
- Read: FULL (main text and SI sections S5-S6).
- Supports: water isotherm at T0 rescaled to other temperatures by p = ps(T) exp(A/RT) (Polanyi); validated on Al-fumarate at 298, 313, 333 K with only "general agreement" (visual, no metric); Frumkin-Fowler-Guggenheim (FFG) isotherm used as a "thermodynamically consistent" S-shaped model with a lateral-interaction parameter; Qst then from a two-isotherm Clausius-Clapeyron average.
- Relevance: shows that the ML-for-MOF-water literature already uses the characteristic curve as its temperature model, again without an extrapolation error metric. Paper 3A can quantify what this paper only eyeballed. (Preprint; check for a published version before citing.)

### C36. Kim et al. 2016 (MOF-801 water adsorption enthalpy by DSC/TGA vs isosteric)
- Citation: H. Kim, H. J. Cho, S. Narayanan, S. Yang, H. Furukawa, S. Schiffres, X. Li, Y.-B. Zhang, J. Jiang, O. M. Yaghi, E. N. Wang, "Characterization of adsorption enthalpy of novel water-stable zeolites and metal-organic frameworks", Scientific Reports 6, 19097 (2016).
- DOI: 10.1038/srep19097 (confirmed via OSTI record 1624815 and Europe PMC PMC4726357).
- URL opened: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4726357/fullTextXML
- Read: FULL (searched).
- Supports:
  - Clausius-Clapeyron requires ideal gas, negligible adsorbed volume, reversible physisorption, inert adsorbent and equilibrium.
  - For hydrophilic adsorbents the separation between isotherms at low relative pressure is minimal, so "the isosteric method is highly sensitive to the resolution of adsorption isotherms".
  - MOF-801: DSC/TGA enthalpy nearly constant over a wide uptake range and in "good agreement" with the isosteric value; zeolites 13X and MgY rise to more than twice the latent heat at low uptake.
- Relevance: the one water-MOF calorimetry-type check found with full text; supports using isosteric Qst as a reference for MOF-801-like step materials, and documents the low-pressure resolution problem.

### C37. Najaf Tomaraei et al. 2025 (water: calorimetry vs Clausius-Clapeyron on GAB fits)
- Citation: G. Najaf Tomaraei, S. Binney, R. Stratton, H. Zhuang, J. L. Wade, "H2O and CO2 sorption in ion-exchange sorbents: distinct interactions in amine versus quaternary ammonium materials", ACS Applied Materials and Interfaces 17, 53547-53562 (2025).
- DOI: 10.1021/acsami.5c12939 (Crossref confirmed). Read through the copy posted at https://arxiv.org/pdf/2508.03909 (publisher PDF).
- Read: FULL (searched).
- Supports: Clausius-Clapeyron enthalpies from multi-temperature GAB fits agree "in both trend and magnitude" with simultaneous TGA/DSC enthalpies; both decrease with loading to a plateau near the condensation enthalpy (44 kJ/mol); Clausius-Clapeyron is "sensitive to experimental variability in relative humidity and temperature control"; open-flow calorimetry can underestimate heat through convective losses.
- Relevance: polymer sorbents, not MOFs, but a recent explicit water comparison of the two Qst routes; supports the 44 kJ/mol plateau as a physical sanity check.

### C38. Giraldo, Rodriguez-Estupinan and Moreno-Pirajan 2019 (Clausius-Clapeyron vs CSK vs calorimetry)
- Citation: L. Giraldo, P. Rodriguez-Estupinan, J. C. Moreno-Pirajan, "Isosteric heat: comparative study between Clausius-Clapeyron, CSK and adsorption calorimetry methods", Processes 7(4), 203 (2019).
- DOI: 10.3390/pr7040203 (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.3390/pr7040203
- Read: ABSTRACT.
- Supports: for N2 on MOF-199 (HKUST-1), MCM-41, SBA-15, activated carbon and graphite, ordered solids give coincident isosteric heats by the three methods, while heterogeneous solids give high dispersion of Clausius-Clapeyron and CSK values relative to calorimetry.
- Relevance: not water; supports the general point that isotherm-derived Qst is reliable for ordered frameworks and unreliable for heterogeneous solids.

### C39. Siperstein et al. (see C07) and Nuhnen and Janiak (see C06) are the two primary Qst-method references; C36-C38 are the calorimetry checks.

### C40. Liu-Kapteijn group review update 2023 (Water adsorption in MOFs: structures and applications)
- Citation: B. Zhang, Z. Zhu, X. Wang, X. Liu, F. Kapteijn, "Water adsorption in MOFs: structures and applications", Advanced Functional Materials 34, 2304788 (2024; online 2023).
- DOI: 10.1002/adfm.202304788 (Crossref confirmed).
- Read: METADATA (search snippet only). Content SEEN-ONLY.
- Relevance: the most recent comprehensive water-MOF review from the Delft group; read before submission.

### C41. Shih and Lin 2025 (JACS: water adsorption in >200 MOFs by simulation)
- Citation: S.-M. Shih, L.-C. Lin, "Water adsorption in metal-organic frameworks: characteristics, mechanisms, and structure-property relationships", Journal of the American Chemical Society 147(38), 34791-34803 (2025). CC BY 4.0.
- DOI: 10.1021/jacs.5c10686 (Crossref confirmed). PMC12464999.
- URL opened: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12464999/fullTextXML
- Read: FULL (searched).
- Supports: average isosteric heats are "originally determined from averaging the isosteric heats calculated via applying the Clausius-Clapeyron equation to experimental isotherms at multiple temperatures"; for 225 MOFs this was too costly, so the infinite-dilution isosteric heat was used as a proxy; a hydrophilicity index built on it correlated well on 19 structures (r_s = -0.94) but weakly on >200 MOFs (r_s = -0.39).
- Relevance: shows Qst is a key descriptor for water-step position and that experimental multi-temperature Qst is scarce. Simulation paper, not an isotherm-model review.

### C42. Oppenheim and Dinca 2024 (isoreticular curves: capillary condensation theory for MOF water)
- Citation: J. J. Oppenheim, M. Dinca, "Isoreticular curves: a theory of capillary condensation to model water sorption within microporous sorbents", Journal of the American Chemical Society 146, 20615-20626 (2024).
- DOI: 10.1021/jacs.4c02743 (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.1021/jacs.4c02743
- Read: ABSTRACT.
- Supports: applies capillary condensation theory and macroscopic thermodynamic models to a large set of MOF water isotherms; relates critical relative pressure alpha, capacity and binding free energy dG via Qmax = a1 (dG/ln alpha)^2 + a2 (dG/ln alpha); discusses pore size or temperature for the onset of hysteresis.
- Relevance: the physical basis for why hysteresis appears above a critical pore size or below a critical temperature; links to C11's Dc formula.

### C43. Nguyen et al. 2020 (COF-432: S-shaped water isotherm without hysteresis)
- Citation: H. L. Nguyen, N. Hanikel, S. J. Lyle, C. Zhu, D. M. Proserpio, O. M. Yaghi, "A porous covalent organic framework with voided square grid topology for atmospheric water harvesting", Journal of the American Chemical Society 142(5), 2218-2221 (2020).
- DOI: 10.1021/jacs.9b13094 (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.1021/jacs.9b13094 (green OA copy at air.unimi.it served a bot challenge).
- Read: ABSTRACT.
- Supports: "Unlike other reported COFs", COF-432 shows an S-shaped isotherm with a steep step at low RH "without hysteretic behavior".
- Relevance: establishes that most COFs show hysteretic water sorption (the abstract's contrast) and gives one hysteresis-free COF suitable for an equilibrium potential. The search engine summary (not opened) reported isotherms at 10, 25, 40 C and Qst about 48 kJ/mol; SEEN-ONLY until the SI is read.

### C44. Brahma, Dwarkanath and Balasubramanian 2024 (COF water isotherm steps by simulation)
- Citation: D. Brahma, N. Dwarkanath, S. Balasubramanian, "Insights into isotherm step and pore-filling mechanisms for water adsorption in covalent organic frameworks", Chemistry of Materials 36, 5651-5660 (2024).
- DOI: 10.1021/acs.chemmater.4c00673 (Crossref confirmed).
- Read: ABSTRACT (OpenAlex).
- Supports: step positions for six COFs computed by flat-histogram MC agree with experiment; two pore-filling mechanisms before the inflection point depending on binding strength and number of hydrophilic sites.
- Relevance: COF water steps are mechanistically like MOF steps; supports including COFs in a common potential-based treatment.

### C45. Kloss et al. 2024 (CPO-27 isoreticular series: from site binding to pore condensation)
- Citation: M. Kloss, L. Schaefers, Z. Zhao, C. Weinberger, H. Egold, M. Tiemann, "Water sorption on isoreticular CPO-27-type MOFs: from discrete sorption sites to water-bridge-mediated pore condensation", Nanomaterials 14(22), 1791 (2024).
- DOI: 10.3390/nano14221791 (Crossref confirmed).
- Read: ABSTRACT (OpenAlex).
- Supports: in larger-pore analogues, after primary open-metal-site binding, sorption proceeds by "classical pore condensation" through H-bond anchor sites; defects alter preferential sites.
- Relevance: a MOF series spanning the change from Langmuir-like site filling to condensation; a natural stress test for a single learned potential.

### C46. Thommes et al. 2015 (IUPAC physisorption report)
- Citation: M. Thommes, K. Kaneko, A. V. Neimark, J. P. Olivier, F. Rodriguez-Reinoso, J. Rouquerol, K. S. W. Sing, "Physisorption of gases, with special reference to the evaluation of surface area and pore size distribution (IUPAC Technical Report)", Pure and Applied Chemistry 87(9-10), 1051-1069 (2015).
- DOI: 10.1515/pac-2014-1117 (Crossref confirmed).
- URL opened: OpenAlex abstract; the De Gruyter page hung in the built-in browser.
- Read: ABSTRACT. The isotherm types (I to VI, IVa/IVb) and hysteresis types (H1 to H5) are cited from C29's abstract (which names H1, H2(a), H2(b) and types IV, V); the definitions themselves are SEEN-ONLY here.
- Relevance: the reference for "type V" and hysteresis-loop terminology.

### C47. Do and Do 2000 (water in activated carbon model)
- Citation: D. D. Do, H. D. Do, "A model for water adsorption in activated carbon", Carbon 38(5), 767-773 (2000).
- DOI: 10.1016/S0008-6223(99)00159-1 (Crossref confirmed). Follow-ups confirmed: Neitsch, Heschel, Suckow 2001, Carbon 39, 1437-1438, DOI 10.1016/S0008-6223(01)00077-X; Do, Junpirom, Do 2009, Carbon 47, 1466-1473, DOI 10.1016/j.carbon.2009.01.039.
- Read: METADATA. Content (functional-group cluster adsorption plus micropore filling by clusters) SEEN-ONLY.
- Relevance: the standard cluster-type model for type V water; a classical baseline candidate.

### C48. Dubinin and Astakhov 1971 (DA equation; zeolites over wide T and p)
- Citation: M. M. Dubinin, V. A. Astakhov, "Description of adsorption equilibria of vapors on zeolites over wide ranges of temperature and pressure", in Molecular Sieve Zeolites-II, Advances in Chemistry 102, 69-85 (1971). Companion: "Development of the concepts of volume filling of micropores in the adsorption of gases and vapors by microporous adsorbents", Bull. Acad. Sci. USSR Div. Chem. Sci. 20. Crossref holds two records with this title in the same issue: DOI 10.1007/BF00849307 (pages 3-7, the one C11 cites) and DOI 10.1007/BF00849308 (pages 8-12), most likely parts 1 and 2. Cite 10.1007/BF00849307 to match C11 and the usual citation, and check the second record's subtitle before citing it.
- DOI: 10.1021/ba-1971-0102.ch044 (Crossref confirmed).
- URL opened: https://api.openalex.org/works/doi:10.1021/ba-1971-0102.ch044
- Read: ABSTRACT.
- Supports: theory of volume filling of micropores extended to zeolites "over wide temperature ranges", including adsorption on cation centres and filling of the remaining volume.
- Relevance: the original DA reference for the characteristic-curve competitor.

### C49. Bakaev and Steele 1993 (the characteristic curve in physical adsorption)
- Citation: V. A. Bakaev, W. A. Steele, "The characteristic curve in physical adsorption", Adsorption Science and Technology 10, 123-136 (1993).
- DOI: 10.1177/0263617499010001-411 (Crossref confirmed).
- Read: ABSTRACT (OpenAlex).
- Supports: traces "the rule of its temperature invariance" from Polanyi through Frenkel-Halsey-Hill and Dubinin to heterogeneous-surface theory; simulated argon isotherms at two temperatures "can be described by one absolute isotherm".
- Relevance: the review-level citation for the history and theoretical status of invariance.

### C50. Kadlec 2001 (history and present state of Dubinin's theory)
- Citation: O. Kadlec, "The history and present state of Dubinin's theory of adsorption of vapours and gases on microporous solids", Adsorption Science and Technology 19(1), 1-24 (2001).
- DOI: 10.1260/0263617011493944 (Crossref confirmed).
- URL opened: https://journals.sagepub.com/doi/10.1260/0263617011493944 (abstract and reference list).
- Read: ABSTRACT.
- Relevance: historical overview; useful only as a secondary citation.

### C51. Riffel et al. 2011 (modified DR for water on silica gel 127B)
- Citation: D. B. Riffel, F. P. Schmidt, F. A. Belo, A. P. F. Leite, F. B. Cortes, F. Chejne, F. Ziegler, "Adsorption of water on Grace Silica Gel 127B at low and high pressure", Adsorption 17, 977-984 (2011).
- DOI: 10.1007/s10450-011-9379-6 (Crossref confirmed).
- URL opened: https://link.springer.com/article/10.1007/s10450-011-9379-6
- Read: ABSTRACT.
- Supports: a modified Dubinin-Radushkevich equation accounting for self-associating molecules; R^2 = 0.9924 vs thermogravimetric data, "8.13% better than the best Dubinin-Astakhov fit".
- Relevance: plain DA is not sufficient for water even on silica gel; modified potential-theory variants are the competitive classical form.

### C52. Chua et al. 2002 and Chakraborty et al. 2009 (silica gel + water: Toth fit and property surfaces)
- Citations: H. T. Chua, K. C. Ng, A. Chakraborty, N. M. Oo, M. A. Othman, "Adsorption characteristics of silica gel + water systems", J. Chem. Eng. Data 47, 1177-1181 (2002), DOI 10.1021/je0255067; A. Chakraborty, B. B. Saha, S. Koyama, K. C. Ng, K. Srinivasan, "Adsorption thermodynamics of silica gel-water systems", J. Chem. Eng. Data 54, 448-452 (2009), DOI 10.1021/je800458k (both Crossref confirmed).
- Read: ABSTRACT (OpenAlex) for both.
- Supports: Chua: water on two silica gels at 298-338 K and 500-7000 Pa; the Toth isotherm "is found to fit all of the experimental data within the experimental errors". Chakraborty: property surfaces (entropy, enthalpy, heat capacity, isosteric heat) derived from "chemical equilibria between adsorbed and gaseous phases, Maxwell relations" and measured isotherms at 273-373 K and 0.5-10 kPa.
- Relevance: Chakraborty et al. is the closest classical precedent to "derive all thermal properties consistently from one fitted equilibrium surface" for water; Paper 3A must cite it and explain the difference (a learned, constraint-preserving surface for step-shaped MOF/COF isotherms rather than a fixed Toth form).

### C53. Ng et al. 2017 (universal isotherm model via site-energy distribution)
- Citation: K. C. Ng, M. Burhan, M. W. Shahzad, A. B. Ismail, "A universal isotherm model to capture adsorption uptake and energy distribution of porous heterogeneous surface", Scientific Reports 7, 10634 (2017).
- DOI: 10.1038/s41598-017-11156-6 (Crossref confirmed, article number 10634).
- Read: ABSTRACT (OpenAlex).
- Supports: all IUPAC isotherm types unified by a revised Langmuir model with a homotattic patch approximation and multiple site-energy sets with probability factors.
- Relevance: a flexible classical competitor with physical parameters; candidate baseline for type V water.

### C54. Mahle 2002 (type 5 isotherm model) and Cardenas 2024 (temperature-dependent type V models for Al-fumarate and CAU-10)
- Citations: J. J. Mahle, "An adsorption equilibrium model for Type 5 isotherms", Carbon 40(15), 2753-2759 (2002), DOI 10.1016/S0008-6223(02)00201-4 (Crossref confirmed; METADATA only). C. Cardenas (presenter), "Temperature-dependent V-type isotherm models: applied to water vapor adsorption on metal-organic frameworks", poster 57e, 2024 AIChE Spring Meeting (ISBN 978-0-8169-1121-9), abstract opened at https://proceedings.aiche.org/conferences/aiche-spring-meeting-and-global-congress-on-process-safety/2024/proceeding/paper/57e-temperature-dependent-v-type-isotherm-models-applied-water-vapor-adsorption-on-metal-organic
- Read: Mahle METADATA; Cardenas ABSTRACT (conference, not peer reviewed).
- Supports (Cardenas): the Mahle and weighted dual-site Langmuir models showed limitations "particularly at low and high pressures" for water on Al-fumarate and CAU-10; a modified Mahle equation improved accuracy and fed a fixed-bed simulation.
- Relevance: identifies the engineering-side temperature-dependent type V competitors (Mahle, weighted dual-site Langmuir). Use as a lead; do not rely on the poster for numbers.

### C55. Thu, Mitra and Saha 2017 (isosteric heat with non-ideal gas and adsorbed-phase volume; DA form)
- Citation: K. Thu, S. Mitra, B. B. Saha, "Theoretical development on the isosteric heat of adsorption and experimental confirmation", arXiv:1709.01723 (2017).
- URL opened: https://arxiv.org/pdf/1709.01723 (PDF, text extracted).
- Read: FULL (derivation section; equations partly garbled in extraction).
- Supports: the isostere slope for the Dubinin-Astakhov equation, eq. (6): (d ln p/dT)_x = (d ln ps/dT)_x + (E/RT^2)(-ln theta)^(1/n) + a term proportional to (d va/dT)_x from the adsorbed-phase volume (thermal expansion); validated against calorimetry for CO2, SF6, N2 on NaX and silicalite (not water); warns that excellent Qst fits can coexist with poor isotherm fits, so isotherm accuracy must be reported first.
- Relevance: the derivation behind relation (R6) in Part 2: under an invariant DA curve, Qst = Delta_vap H(T) + A + expansion term. Preprint; check for a journal version before citing.

### C56. Glaznev, Ovoshchnikov and Aristov 2009 and Sircar 1983 (LDF in water heat-transformer kinetics; non-isothermal LDF)
- Citations: I. S. Glaznev, D. S. Ovoshchnikov, Yu. I. Aristov, "Kinetics of water adsorption/desorption under isobaric stages of adsorption heat transformers: the effect of isobar shape", Int. J. Heat Mass Transfer 52, 1774-1777 (2009), DOI 10.1016/j.ijheatmasstransfer.2008.09.031 (METADATA). S. Sircar, "Linear-driving-force model for non-isothermal gas adsorption kinetics", J. Chem. Soc. Faraday Trans. 1 79, 785 (1983), DOI 10.1039/F19837900785 (ABSTRACT via OpenAlex).
- Supports (Sircar 1983): the solid-film LDF model "provides a mathematically simple but adequate description of non-isothermal gas sorption kinetics" and its equilibrium/transport interactions are equivalent to more complex non-isothermal models.
- Relevance: non-isothermal LDF couples uptake to the heat of adsorption, so a model whose Qst is consistent with its isotherm gives a consistent energy balance. Glaznev et al. (title) show isobar shape matters for water kinetics in heat transformers; content SEEN-ONLY.

### C57. Krishna and Wesselingh 1997 (Maxwell-Stefan: chemical-potential gradients as driving forces)
- Citation: R. Krishna, J. A. Wesselingh, "The Maxwell-Stefan approach to mass transfer", Chemical Engineering Science 52(6), 861-911 (1997).
- DOI: 10.1016/S0009-2509(96)00458-7 (Crossref confirmed).
- Read: METADATA. Content SEEN-ONLY.
- Relevance: the flux-force reference: the thermodynamic driving force is the chemical-potential gradient, and the Fickian/LDF form follows via the thermodynamic correction factor Gamma = d ln p / d ln q, which a learned potential supplies analytically.

### C58. Coudert, Jeffroy, Fuchs, Boutin and Mellot-Draznieks 2008 (osmotic potential; grand potential from the isotherm)
- Citation: F.-X. Coudert, M. Jeffroy, A. H. Fuchs, A. Boutin, C. Mellot-Draznieks, "Thermodynamics of guest-induced structural transitions in hybrid organic-inorganic frameworks", Journal of the American Chemical Society 130(43), 14294-14302 (2008).
- DOI: 10.1021/ja805129c (Crossref confirmed). Green OA copy: https://arxiv.org/pdf/1904.09588 (opened, text extracted).
- Read: FULL (derivation section and model).
- Supports:
  - Grand potential of the adsorbed fluid from the isotherm, eq. (6)-(7): Omega(P) = - integral_0^P N_ads(p) (d mu/dp) dp = - integral_0^P N_ads(p) V_m(p) dp, with Omega(P = 0) = 0; with ideal gas, V_m = RT/p.
  - Osmotic potential of a host phase, eq. (8): Omega_os(T,P) = F_host(T) + PV - integral_0^P N_ads(T,p) V_m(T,p) dp; comparing Omega_os across host phases predicts guest-induced transitions; with a Langmuir isotherm, eq. (11): Omega_os = F_host + PV - N_max RT ln(1 + K P / N_max).
  - Stepped isotherms in flexible frameworks are "frequently assorted with hysteresis loops".
- Relevance: the cleanest published statement of the potential Paper 3A learns (C22 gives the solution-thermodynamics view; C58 gives the explicit integral). It also shows what a single smooth potential cannot do: a breathing MOF needs one potential per host phase plus the empty-host free-energy difference F_host, so a guest-induced transition appears as a crossing of two potentials, not as a feature of one.

### C59. Hastings et al. 2024 (water isotherms 25-125 C on MOF-303, MOF-LA2-1, MIL-100(Fe); Darken relation)
- Citation: J. Hastings, T. Lassitter, Z. Zheng, S. Chheda, J. I. Siepmann, L. Gagliardi et al., "High-temperature water adsorption isotherms and ambient temperature water diffusion rates on water harvesting metal-organic frameworks", Journal of Physical Chemistry C 128, 11328-11339 (2024).
- DOI: 10.1021/acs.jpcc.4c01733 (Crossref confirmed). Accepted manuscript at OSTI: https://www.osti.gov/pages/servlets/purl/3009890 (opened, text extracted); OSTI record 3009890 (abstract).
- Read: FULL (accepted manuscript, searched).
- Supports:
  - Isotherms 25 to 125 C; Qst by Clausius-Clapeyron from 45 to 115 C in 10-degree steps (citing C04); initial-site heats near 54 kJ/mol (MOF-LA2-1) and 60 kJ/mol (MIL-100(Fe)), averages 47 and 48 kJ/mol.
  - MOF-303: "significant decrease in the adsorption capacity from 25 C to 45 C" with the step shifting toward 15% RH; samples from three sources (Yaghi lab, novoMOF, Framergy) give different capacities and different temperature sensitivity; a change in MOF structure "may also contribute".
  - Darken relation used with the isotherm slope (thermodynamic correction factor) to explain loading-dependent diffusion; diffusion slows at the step.
- Relevance: (i) the widest-temperature open water-MOF dataset found; the 25 to 45 C capacity drop is far larger than the 0.7% fall in liquid-water density over that range (computed from C30 eq. 2: 997.0 to 990.2 kg/m3), so it is a direct counterexample to strict characteristic-curve invariance; (ii) sample-to-sample variation is a pitfall for any benchmark; (iii) uses the Darken/flux-force link that Paper 3A's sign-correct LDF relies on.

### C60. Lenzen et al. 2019 (CAU-23: characteristic curve and Qst = Delta_vap h + A in a MOF cycle model)
- Citation: D. Lenzen, J. Zhao, S.-J. Ernst, M. Wahiduzzaman, A. K. Inge, D. Froehlich et al., "A metal-organic framework for efficient water-based ultra-low-temperature-driven cooling", Nature Communications 10, 3025 (2019).
- DOI: 10.1038/s41467-019-10960-0 (Crossref confirmed). PMC6616384.
- URL opened: https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6616384/fullTextXML
- Read: FULL (methods searched).
- Supports: A(p,T) = -RT ln(p/ps(T)); uptake converted to liquid volume W = X(p,T)/rho_L(T); "the plot W(A) is referred to as characteristic curve", fitted by DA W = W0 exp(-(A/E)^n) or sectionwise (citing de Lange et al., C12); "within the Dubinin-Astakhov approach", q_st = Delta h_vap(T) + A(T) (their eq. 17); uptake taken from either a weighted dual-site Langmuir (wDSL) or DA, "depending on which fits best"; evaporation enthalpy 44.19 kJ/mol used in the COP.
- Relevance: the explicit, citable form of the characteristic-curve Qst used by the MOF heat-transformation community (Fraunhofer ISE / Janiak / Stock line), and evidence that wDSL is the other standard temperature-dependent competitor. Article number 3025 confirmed on Crossref.

---

## Part 2. Synthesis for Paper 3A

### (a) Exact thermodynamic relations Paper 3A must use

Notation: n(p,T) uptake per unit mass (mol/kg; measured as Gibbs excess, C24); p water vapour pressure; p0(T) saturation pressure; R = 8.314462618 J/(mol K); ideal-gas vapour unless stated.

R1. Grand (immersion) potential and the Gibbs adsorption isotherm [C22, C58, C01].
  Omega(p,T) = - integral_0^p n(p',T) V_m dp' = - RT integral_0^p n(p',T) d ln p'   (ideal gas, Omega(0,T) = 0)
  so n(p,T) = -(1/RT) (d Omega / d ln p)_T.
  Paper 3A's learned scalar can be Phi(ln p, T) = -Omega/RT = integral_0^p n d ln p (the IAST "reduced spreading pressure" psi of C01; for micropores call it the grand or immersion potential per unit mass, C22).
  LaTeX: \Omega(p,T) = -RT\int_0^{p} n(p',T)\,\mathrm{d}\ln p', \qquad n = -\frac{1}{RT}\left(\frac{\partial \Omega}{\partial \ln p}\right)_T.

R2. Monotonicity / mechanical stability [C27 for the fluctuation framing; identity is standard grand-canonical statistics, not quoted from a source here].
  (d n / d ln p)_T >= 0, equivalently Phi convex in ln p: d^2 Phi / d(ln p)^2 >= 0. In the grand canonical ensemble (d<N>/d(beta mu))_T = <N^2> - <N>^2 >= 0, so a negative slope is unphysical at equilibrium. A van der Waals-type loop belongs only to metastable branches (see R8 and C11, C29).

R3. Henry limit [C02, C06, C07].
  lim_{p->0} n/p = K_H(T), finite and > 0; equivalently Phi -> K_H(T) p as p -> 0.
  With K_H(T) = K0 exp(Q0/RT), the zero-coverage isosteric heat is Qst(n->0) = Q0 (from R4).
  Freundlich and Sips violate this limit (no finite slope at p = 0) and their Qst diverges at low coverage; Toth does not (C07). In the virial form ln p = ln n + (1/T) sum a_i n^i + sum b_i n^i the zero-coverage heat is -R a0 (C06; C06 writes Hads = R a0 with a0 < 0).

R4. Isosteric heat from Clausius-Clapeyron at constant loading [C04 via C06, C07, C36].
  Qst(n,T) = -R [d ln p / d(1/T)]_n = R T^2 (d ln p / dT)_n.
  For a model that returns n(p,T), evaluate it by implicit differentiation (C07 does this for dual-site Langmuir):
  (d ln p/dT)_n = -(dn/dT)_p / (dn/d ln p)_T, hence Qst = -R T^2 (dn/dT)_p / (dn/d ln p)_T.
  With R1: (dn/d ln p)_T = d^2 Phi/d(ln p)^2 and (dn/dT)_p = d^2 Phi/(d ln p dT), so Qst comes from second derivatives of one scalar, and its sign is fixed if Phi is convex in ln p and n decreases with T.
  LaTeX: Q_{st}(n,T) = R T^2\left(\frac{\partial \ln p}{\partial T}\right)_n = -RT^2\,\frac{(\partial n/\partial T)_p}{(\partial n/\partial \ln p)_T}.
  Approximations: ideal gas and negligible adsorbed molar volume (C04, C06, C36). Exact Clapeyron form: Qst = T (v_g - v_a) (dp/dT)_n. For water at 25 C and p0, v_a/v_g = 2.3e-5 (computed) and Z = 0.9984 (R7), so both corrections are below 0.2%.
  Terminology: report Qst > 0 and Delta H_ads = -Qst (C06).

R5. Characteristic curve and its Qst [C11, C60, C55, C18, C26].
  A(p,T) = RT ln(p0(T)/p); W = n M / rho_L(T) (liquid-volume uptake, C60).
  Invariance hypothesis: W = W(A), independent of T.
  If the curve is invariant in n (not W): ln p = ln p0(T) - A(n)/RT gives (d ln p/dT)_n = d ln p0/dT + A/(RT^2), hence
  Qst(n,T) = R T^2 d ln p0/dT + A = Delta_vap H(T) + A   (C60 eq. 17, q_st = Delta h_vap(T) + A).
  If invariance is in W with rho_L(T), an extra term from liquid thermal expansion appears (C55 eq. 6; C13 lists the volume expansion coefficient alpha). For water alpha_L = 3.4e-4 1/K at 25-45 C (computed from C30 eq. 2), small but not zero.
  Consequence: the characteristic-curve competitor has Qst - Delta_vap H = A, i.e. Qst is fixed by the isotherm at one temperature; any loading-dependent adsorbed-phase entropy beyond the liquid reference breaks it (C26).
  LaTeX: A = RT\ln\frac{p_0(T)}{p}, \qquad Q_{st} = \Delta_{vap}H(T) + A(n) \;\;(\text{invariant } A(n)).

R6. Vaporisation enthalpy consistent with p0(T) [C30 eqs. (6), (7)].
  Delta_vap h = h'' - h' = T (1/rho'' - 1/rho') dp0/dT (exact Clapeyron, built into SR1-86).
  Computed from SR1-86: 43.99 kJ/mol at 25 C, 43.35 at 40 C, 42.48 at 60 C, 41.58 at 80 C. The ideal-gas form R T^2 d ln p0/dT overestimates by 0.17% (25 C) to 0.97% (80 C). Use the same choice in R5 as in R4, or the error appears as spurious non-invariance.
  Note: the 40.7 kJ/mol often quoted as "the" heat of condensation (C11 table note) is the value at the normal boiling point; at 25 C the bound is 44.0 kJ/mol.

R7. Saturation pressure and ideal-gas check [C30, C31].
  ln(p0/pc) = (Tc/T) [a1 tau + a2 tau^1.5 + a3 tau^3 + a4 tau^3.5 + a5 tau^4 + a6 tau^7.5], tau = 1 - T/Tc, coefficients in C30.
  Verification values: 611.657 Pa at 273.16 K (release Table 1); 3169.82 Pa (25 C), 4246.92 Pa (30 C), 7385.11 Pa (40 C) computed from eq. (1).
  Compressibility of saturated vapour Z = p0/(rho'' R_w T) from eqs. (1) and (3): 0.99948 (0.01 C), 0.99837 (25 C), 0.99802 (30 C), 0.99717 (40 C), 0.99467 (60 C), 0.99068 (80 C). Below saturation Z is closer to 1 (deviation roughly proportional to p). IAPWS-95 Table 8 gives Z = 0.99937 at 275 K (C31). Ideal gas is adequate for water at the kPa pressures of MOF isotherms.

R8. Excess vs absolute uptake [C03, C24, C25].
  n_abs - n_ex = V_pore rho_gas. With rho_gas = p M/(Z R T): 2.3e-5 g/cm3 at 25 C and p0; for V_pore = 0.5 cm3/g the difference is 1.2e-5 g/g (1.5e-4 g/g at 80 C and p0), against uptakes of 0.1-0.5 g/g, i.e. below 0.01-0.1%. Water vapour in MOF isotherms is deeply subcritical (T/Tc < 0.55), the regime where C25 says simulation and experiment compare directly. Treat measured uptake as the Gibbs excess (C24) and state that the distinction is negligible.

R9. LDF kinetics and sign correctness [C09, C10, C57, C59].
  dq/dt = k_LDF [q*(p,T) - q], with k_LDF = 15 D/r_p^2 for spheres (Glueckauf, C10; content SEEN-ONLY).
  Flux-force reading: with mu_gas = mu0 + RT ln p and the adsorbed-phase chemical potential mu_ads(q,T) = mu0 + RT ln p_eq(q,T), the sign of (q* - q) equals the sign of (mu_gas - mu_ads) if and only if p_eq(q,T) is increasing in q, i.e. R2 holds. So LDF is thermodynamically sign-correct exactly when the isotherm is monotone. A Maxwell-Stefan/Darken refinement uses D = D0 (d ln p/d ln q)_T (C57, used in C59), which R1 supplies as D0 n / (d^2 Phi/d(ln p)^2).

### (b) Strongest classical competitors, ranked

1. Temperature-invariant characteristic curve W(A), fitted with a flexible function (DA, sum of logistic steps as in C14, or sectionwise as in de Lange/C60), with Qst = Delta_vap H(T) + A (R5). Evidence: it is the default temperature model of the water-MOF heat-transformation field (C11, C12, C13, C60); merged curves reported for MIL-160 20-50 C (C14), Mg-SU-102 15-55 C with a slight systematic shift (C33), Al-fumarate 298-333 K "general agreement" (C35); the founders found it practically accurate even where not strictly valid (C18); one isotherm plus p0(T) predicts all temperatures, so it is the bar for temperature extrapolation. Weaknesses: invariance asserted visually in every water-MOF case found (no published error metric), fails by construction when adsorbed-phase entropy differs from liquid (C26), and is contradicted by temperature-dependent capacity (MOF-303, C59) and framework flexibility (C58).
2. Jointly fitted temperature-dependent site or cooperative models with analytic Qst: weighted dual-site Langmuir (C60), Mahle-type type V models (C54), Toth/Sips/Langmuir with explicit T-dependence (C07), cooperative isotherm (C28), Fowler-Guggenheim/FFG (C35), Toth with property surfaces as in silica gel-water (C52). Evidence: these give closed-form Qst consistent with the isotherm when fitted to all temperatures at once (C07); wDSL was chosen over DA for some MOFs (C60). Weaknesses: dual-site Langmuir Qst can show an unphysical maximum; Sips/Freundlich break the Henry limit and their Qst diverges; all disagree outside the measured loading window (C07); the AIChE poster reports Mahle and wDSL failing at low and high pressure for Al-fumarate and CAU-10 (C54).
3. Virial isotherm fitted to all temperatures simultaneously (C06, C07). Thermodynamically consistent by construction (Qst from coefficients, Henry limit built in) but cannot fit steep water steps without excluding data (C06), so it is a low-loading competitor only.
4. Cluster and multilayer models: Do-Do and successors (C47), GAB, modified DR for water (C51). Common for carbons and silica; GAB and BET are often used beyond their premises (C26, C27). Weak for MOF steps unless augmented.
5. Per-temperature fits plus two- or three-temperature Clausius-Clapeyron (the common practice described in C06, used in C14, C33, C59). This is the baseline that Paper 3A's "unconstrained" comparison resembles; it is the weakest for Qst (C06, C07, C36).

Direct calorimetric references for water are scarce: MOF-801 DSC/TGA agrees with isosteric values (C36); polymer sorbents agree in trend and magnitude (C37); for gases, isotherm Qst agrees with calorimetry on ordered solids and disperses on heterogeneous ones (C38), and falls below calorimetry at higher loading for CO2 in MIL-100(Cr) (C06).

### (c) Pitfalls a referee will raise

1. Qst from separate per-temperature fits, two or three temperatures, wide spacing: introduces artificial error; C06 recommends <= 20 K for two isotherms and three isotherms at about 10 K with reported standard errors.
2. Extrapolating Qst outside the measured loading window, especially to zero coverage: different good-fitting models disagree strongly (C07); the virial a0 changed from -54 to -33 kJ/mol with the choice of low-pressure points (C06). Paper 3A must report Qst only where every temperature has data, or show the constrained model's extrapolation separately.
3. Unphysical Qst shapes from classical models: maxima at low coverage (dual-site Langmuir), divergence (Sips, Freundlich) (C07). Counting such violations is a fair metric for Paper 3A, but apply it to the classical models too.
4. Low-pressure resolution for hydrophilic sorbents: isotherms at different temperatures nearly coincide at low relative pressure, so isosteric Qst is resolution-limited there (C36). The Henry regime of water is often not measured at all; claims about the Henry limit must be framed as a structural property of the model, not as a validated number.
5. Physical bounds on Qst: values below the vaporisation enthalpy "seem physically unrealistic" for water in MOFs (C11), but use the bound at the right temperature (44.0 kJ/mol at 25 C, not 40.7, R6).
6. Characteristic-curve invariance is approximate: shift with T (C33), entropic cause (C26), founders' error analysis (C18), temperature-dependent capacity (C59). A fair comparison must fit the characteristic curve as flexibly as the network (C14's 7-parameter logistic form, not a 3-parameter DA) so that Paper 3A's advantage cannot be blamed on a weak baseline.
7. p0(T) and Delta_vap H(T) consistency: different p0 correlations (Antoine vs IAPWS) differ by up to 0.5% (C30 vs C35) and the ideal-gas Delta_vap H differs from the exact one by 0.2-1% (R6); both bias A and Qst systematically with temperature. Use SR1-86 for everything and say so.
8. Hysteresis: the adsorption branch of capillary-condensation systems "does not reach thermodynamic equilibrium" (C11); most COFs show hysteretic water sorption (C43); hysteresis needs two-branch models (C29). An equilibrium potential represents one branch only: Paper 3A must state which branch it fits, restrict Qst and Clausius-Clapeyron to reversible regions or to one branch consistently, and exclude or flag H-type loops. Which branch is closer to equilibrium for a given loop type is a point to take from the IUPAC report (C46), currently SEEN-ONLY.
9. Flexible frameworks: guest-induced transitions require separate potentials for each host phase plus the host free-energy difference (C58); a single smooth potential will either smear a breathing step or violate convexity. Exclude breathing MOFs (MIL-53 type) or model them explicitly.
10. Sample and instrument variability: MOF-303 from three sources gives different capacities and temperature sensitivity (C59). Train/test splits by temperature must stay within one sample and one instrument, and the paper should report the inter-sample spread as a floor on achievable accuracy.
11. Excess vs absolute and ideal gas: a referee may ask; R7 and R8 give the numbers (both negligible for water at kPa).
12. Mechanism claims from fit quality: several models fit equally well (C27); Paper 3A should not claim mechanistic insight from the learned potential alone.
13. Equilibration time and kinetics in water isotherm measurements are not covered by the sources read here; treat as an open item (see d).

### (d) SEEN-ONLY leads (metadata or abstract only; read before citing for content)

- C04 Pan, Ritter, Balbuena 1998, Langmuir 14, 6323 (DOI 10.1021/la9803373): the two Clausius-Clapeyron approximations and their error; ACS bot challenge blocked it.
- C12 de Lange et al. 2015, Chem. Rev. 115, 12205 (DOI 10.1021/acs.chemrev.5b00059): characteristic-curve cycle modelling and average enthalpy method for water MOFs.
- C18 Bering, Dubinin, Serpinskii 1972 (DOI 10.1007/BF00857806): full error analysis of the invariance assumption (only conclusions read).
- C19 Lehmann et al. 2017, Appl. Energy 207, 274 (DOI 10.1016/j.apenergy.2017.07.008): DP-theory predictions vs experiment for water heat storage; the most likely source of a quantitative invariance test.
- C20 Teicht 2023, Energy 263, 125968 (DOI 10.1016/j.energy.2022.125968): modification of potential theory when invariance fails.
- Kohler, Hinze, Mueller, Schwieger 2017, "Temperature independent description of water adsorption on zeotypes showing a type V adsorption isotherm", Energy 135, 227-236 (DOI 10.1016/j.energy.2017.06.115, Crossref confirmed; ADS page served a human-verification check, OpenAlex had no abstract).
- C23 Myers 2004 chapter (DOI 10.1039/9781847550415-00243).
- C10 Glueckauf 1955 (DOI 10.1039/tf9555101540) for the 15 D/r^2 coefficient.
- C40 Zhang et al. 2023/2024 Adv. Funct. Mater. review (DOI 10.1002/adfm.202304788).
- C46 IUPAC 2015 report (DOI 10.1515/pac-2014-1117): isotherm and hysteresis types, which branch is equilibrium.
- C47 Do and Do 2000 (DOI 10.1016/S0008-6223(99)00159-1) and C54 Mahle 2002 (DOI 10.1016/S0008-6223(02)00201-4): model equations.
- C43 Nguyen et al. 2020 COF-432 SI: multi-temperature isotherms and Qst (reported by a search summary as about 48 kJ/mol from 10, 25, 40 C; not verified).
- C57 Krishna and Wesselingh 1997 (DOI 10.1016/S0009-2509(96)00458-7).
- Rehner 2026 (C08) full text, and Thiele et al. 2026, J. Phys. Chem. B 130, 2299-2313 (DOI 10.1021/acs.jpcb.5c08035, Crossref confirmed, not opened): cDFT multicomponent isotherms and enthalpies in MOFs.
- Aristov 2026 book chapter "Thermodynamic issues related to adsorptive conversion of ultra-low temperature heat", in Gas-Solid Adsorption Thermodynamics, pp. 149-191 (DOI 10.1016/B978-0-443-29815-8.00010-0, Crossref confirmed, not opened).
- Gordeeva, Solovyeva, Aristov 2016 NH2-MIL-125 (DOI 10.1016/j.energy.2016.01.034) and Solovyeva, Gordeeva, Aristov 2019 MIL-101(Cr)-methanol (DOI 10.1016/j.enconman.2018.12.065): Aristov-group characteristic-curve applications.
- Dalby, Abbott, Matubayasi, Shimizu 2022, "Cooperative sorption on heterogeneous surfaces", Langmuir 38, 13084-13092 (DOI 10.1021/acs.langmuir.2c01750, Crossref confirmed, not opened).
- Hamid, Vyawahare, Chen (Texas Tech), "Estimation of isosteric heat of adsorption from generalized Langmuir isotherm", OSTI record 2222462 (abstract read; journal DOI not resolved): gL isotherm with Clausius-Clapeyron validated against measured Qst.

### Counts
- Entries C01-C60 (a few combine two papers). Opened live at full-text level: C06, C07, C11, C14, C30, C31, C33, C35, C36, C37, C41, C55, C58, C59, C60 (15). Abstract or conclusions level: about 30. Metadata only (SEEN-ONLY for content): C04, C10, C12, C16 (one-sentence abstract), C19, C20, C23, C32, C40, C47, C54 (Mahle), C57.
- Every DOI listed was resolved on the Crossref API in this session, except where noted (OSTI 2222462).

