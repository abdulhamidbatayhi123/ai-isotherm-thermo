# Paper 3A literature journal: calorimetric heats of water adsorption in MOFs and COFs

Started 2026-10-13. Purpose: find independently measured (calorimetric) heats of water adsorption to test Qst predicted from multi-temperature isotherm fits. Isotherm-derived Qst (Clausius-Clapeyron, virial, characteristic curve) does not count as independent.

Status codes: FULL = full text read; ABS = abstract read; META = metadata only; SEEN-ONLY = claim seen in a search snippet or abstract, not confirmed in text.

## Search log

### K01 (EXCLUDED, not calorimetric). Laurenz, Fueldner, Schnabel, Schmitz 2020
- Citation: E. Laurenz, G. Fueldner, L. Schnabel, G. Schmitz, "A Novel Approach for the Determination of Sorption Equilibria and Sorption Enthalpy Used for MOF Aluminium Fumarate with Water", Energies 13 (2020) 3003.
- DOI 10.3390/en13113003: Crossref title matches (checked 2026-10-13, https://api.crossref.org/works/10.3390/en13113003).
- Opened: MDPI html returned HTTP 403 (no bypass). Abstract read via https://api.openalex.org/works/doi:10.3390/en13113003 (2026-10-13). Status ABS.
- Finding: the enthalpy is computed through the Clausius-Clapeyron equation from slopes of small isothermal and isochoric state changes (volume-swing apparatus). Mean differential enthalpy 2.90 +/- 0.05 MJ/kg (52.2 +/- 1.0 kJ/mol). Isotherms at 30, 40, 60 C (inflection p/p0 about 0.25, 0.28, 0.33). Binder-based coating.
- Verdict: NOT independent (isotherm/isobar slope plus Clausius-Clapeyron). Useful only as a comparison of isosteric methods.

### K02 (EXCLUDED, not calorimetric; abstract wording resolved). Froehlich et al. 2016, CAU-10-H
- Citation: D. Froehlich, E. Pantatosaki, P. D. Kolokathis, K. Markey, H. Reinsch, M. Baumgaertner, M. A. van der Veen, D. E. De Vos, N. Stock, G. K. Papadopoulos, S. K. Henninger, C. Janiak, "Water adsorption behaviour of CAU-10-H: a thorough investigation of its structure-property relationships", J. Mater. Chem. A 4 (2016) 11859-11869.
- DOI 10.1039/c6ta01757f: title matches in OpenAlex record (https://api.openalex.org/works/doi:10.1039/c6ta01757f, 2026-10-13).
- Opened: RSC html returned 403. Full text read from KU Leuven Lirias PDF https://lirias.kuleuven.be/retrieve/4a6b0271-3678-4835-adf1-e7c9c81cffbf (2026-10-13), text extracted locally. Status FULL.
- Resolution: the abstract says "heat of adsorption [was] directly measured", but the Results section says the isosteric heat was calculated from the adsorption isotherms of Froehlich et al. (ref. 23) using the Clausius-Clapeyron equation. Only heat capacity, thermal conductivity and diffusivity were directly measured. dH_ads about 56 kJ/mol at low loading, plateau slightly over 50 kJ/mol at 0.06 to 0.28 g/g, falling below evaporation enthalpy at pore condensation (Fig. 10, figure only).
- Verdict: NOT independent. The abstract wording is misleading; do not cite as calorimetry.

### K03 (INDEPENDENT, DSC/TGA cycle). Kim et al. 2016, MOF-801 (plus 13X, MgY zeolites)
- Citation: H. Kim, H. J. Cho, S. Narayanan, S. Yang, H. Furukawa, S. Schiffres, X. Li, Y.-B. Zhang, J. Jiang, O. M. Yaghi, E. N. Wang, "Characterization of Adsorption Enthalpy of Novel Water-Stable Zeolites and Metal-Organic Frameworks", Sci. Rep. 6 (2016) 19097.
- DOI 10.1038/srep19097 (Crossref check below in the DOI table).
- Opened: https://pmc.ncbi.nlm.nih.gov/articles/PMC4726357/ (2026-10-13). Status FULL (main text and captions; SI .doc not opened).
- Method: conventional DSC (TA Discovery DSC) plus TGA (TA Discovery TGA) on samples pre-equilibrated at 60% RH in a TA Q5000SA; desorption ramp then sensible-heat ramp; thermodynamic-cycle analysis. This is calorimetric and independent of the isotherms, but it gives an integral (averaged) enthalpy over a loading window: MOF-801 2960 +/- 39 kJ/kg_water (about 53.3 kJ/mol) averaged over 19-20 wt% at 30 C. The loading-resolved curve in Fig. 4b (Eqn 17) is a model estimate assuming adsorbed-phase internal energy equals saturated liquid; figure only, described as nearly constant for MOF-801.
- Sample: MOF-801 made by Furukawa, Zhang, Jiang, Yaghi (Furukawa et al. JACS 2014 recipe); same paper also measures water isotherms of the same material on a DVS Vacuum and derives isosteric enthalpy by Clausius-Clapeyron (Fig. 1b), reported in "good agreement" with the DSC result. Isotherm temperatures are not listed in the text (Fig. 1a, "wide temperature range"); 5 C interval used for MOF-801.
- Heat vs loading: one numeric integral value plus figure-only curve. Multi-T isotherms: yes, same paper and same lab (temperatures need figure reading or SI).
- Rank: strong candidate (calorimetric number plus same-sample multi-T isotherms), but only one averaged number, not a differential curve.

### K04 (INDEPENDENT, Calvet gas-adsorption calorimetry). Wu, Guo, Sun, Navrotsky 2016, HKUST-1
- Citation: D. Wu, X. Guo, H. Sun, A. Navrotsky, "Interplay of Confinement and Surface Energetics in the Interaction of Water with a Metal-Organic Framework", J. Phys. Chem. C 120 (2016) 7562-7567.
- DOI 10.1021/acs.jpcc.5b12239: Crossref title matches (https://api.crossref.org/works?query.bibliographic=..., 2026-10-13).
- Opened: OSTI accepted manuscript https://www.osti.gov/servlets/purl/1247324 (2026-10-13), text extracted locally. Status FULL (accepted manuscript).
- Method: direct gas adsorption calorimetry at 25 C, Calvet-type Setaram SenSYS coupled to a volumetric adsorption analyzer, small water doses; differential enthalpy vs loading.
- Numbers (Table 1): about 0 mmol/g: -119.4 +/- 0.5 kJ/mol; 2.7 to 17.8 mmol/g: -50.2 +/- 1.8 kJ/mol; above 29.9 mmol/g: -15.2 +/- 2.3 kJ/mol. Full curve in Fig. 2B (figure). Isotherm at 25 C only from the same experiment.
- Sample: HKUST-1 characterized in an earlier Navrotsky paper (ref. 28); commercial Basolite C300 mentioned in intro, source not confirmed here.
- Multi-T isotherms of the same sample: NO (single 25 C). HKUST-1 multi-T water isotherms exist in other labs but on different samples; HKUST-1 also degrades in water, which complicates a Qst test.
- Rank: good differential calorimetry, weak for Paper 3A unless paired with another lab's multi-T isotherms.

### K05 (INDEPENDENT, microcalorimetry; ABS only). Bourrelly et al. 2010, MIL-53(Cr)
- Citation: S. Bourrelly, B. Moulin, A. Rivera, G. Maurin, S. Devautour-Vinot, C. Serre, T. Devic, P. Horcajada, A. Vimont, G. Clet, M. Daturi, J.-C. Lavalley, S. Loera-Serna, R. Denoyel, P. L. Llewellyn, G. Ferey, "Explanation of the Adsorption of Polar Vapors in the Highly Flexible Metal Organic Framework MIL-53(Cr)", J. Am. Chem. Soc. 132 (2010) 9488-9498.
- DOI 10.1021/ja1023282: Crossref title matches (https://api.crossref.org/works?query.bibliographic=..., 2026-10-13).
- Opened: HAL hal-01840524 returned an Anubis bot-protection page (not bypassed). Abstract read on https://esploro.umontpellier.fr/esploro/outputs/journalArticle/Explanation-of-the-Adsorption-of-Polar/9944055109311 (2026-10-13). Unpaywall API rejected the placeholder email (HTTP 422). Status ABS.
- Claim: water, methanol, ethanol adsorption studied by gravimetry, XRD, microcalorimetry, thermal analysis, IR, modeling; adsorption enthalpies from microcalorimetry show interaction strength falling from ethanol to water. Water induces framework contraction (breathing).
- Unknown (SEEN-ONLY): calorimeter temperature (Llewellyn lab typically 303 K Tian-Calvet with manometry), heat-vs-loading form, multi-T isotherms. Breathing MOF: a single-phase isotherm model would not apply cleanly.
- Rank: low to medium for Paper 3A (flexible framework, single T likely).

### K06 (INDEPENDENT, in-situ calorimetry with isotherms 298-338 K; SEEN-ONLY). Khan and Mitra 2025, MIL-101(Cr)
- Citation: M. A. Khan, S. Mitra, "Identifying consistent adsorption isotherm equation for water vapour/MIL-101(Cr) pair using calorimetric measurements", Int. Commun. Heat Mass Transf. 168 (2025) 109443.
- DOI 10.1016/j.icheatmasstransfer.2025.109443: Crossref title matches (2026-10-13).
- Opened: ScienceDirect abstract page and ResearchGate both returned HTTP 403; OpenAlex returned 429 (rate limit); Semantic Scholar 404. Status META plus search-snippet text (SEEN-ONLY).
- Seen in search snippet (not verified on the page): a modified constant-volume, variable-pressure apparatus with in-situ calorimetry, 298 to 338 K, 0.4 to 9.3 kPa; direct Qst for water on MIL-101(Cr); the authors say direct Qst measurements for this pair are rarely performed and reported values disagree; the CDS isotherm equation predicts both uptake and heat, while SC and Mahle equations fail at low uptake.
- If confirmed, this is a best-case design: calorimetric heat vs loading and isotherms at several temperatures on the same sample in the same rig. It is also directly on Paper 3A's question (which isotherm equation is thermodynamically consistent). Needs full-text access (user's institutional access or author request).
- Rank: potentially top; currently unverified.

### K07 (EXCLUDED, not calorimetric). QE-TPDA study of CAU-10 and MIL-96 (2024)
- PMC11643603 / PubMed 39683790, "Water Sorption Properties and Hydrothermal Stability of Al-Containing Metal-Organic Frameworks CAU-10 and MIL-96 Studied Using Quasi-Equilibrated Thermodesorption". Seen in search results only (2026-10-13). QE-TPDA heats (45-46 kJ/mol CAU-10; 43-56 kJ/mol MIL-96) are derived from thermodesorption equilibrium analysis, not calorimetry. Not independent; not pursued further.

### K08 (INDEPENDENT, Calvet gas-adsorption calorimetry; single T). Wang et al. 2019, mmen-Mg2(dobpdc)
- Citation: J. Wang, E. Yilmaz, X. Zhang, H. Li, R. Zhang, X. Guo, H. Sun, B. Wang, D. Wu, "Hydration Energetics of a Diamine-Appended Metal-Organic Framework Carbon Capture Sorbent", J. Phys. Chem. C 124 (2020) 398-403 (online 2019).
- DOI 10.1021/acs.jpcc.9b08008 (taken from PDF metadata; Crossref check in DOI table below).
- Opened: Di Wu lab PDF https://wpcdn.web.wsu.edu/wp-labs/uploads/sites/1547/2020/01/53.pdf (2026-10-13), text extracted. Status FULL.
- Method: Calvet microcalorimeter (Setaram Sensys Evo) integrated with Micromeritics 3Flex dosing, 25 C, triplicate isotherms; differential enthalpy vs loading (Fig. 3b, figure); plateaus quoted: near zero -110.9 +/- 3.1, plateau -65.8 +/- 4.7 (from 0.2 mmol/g), second plateau -44.2 +/- 1.8 kJ/mol (from about 4.0 mmol/g).
- Multi-T isotherms of the same sample: NO. Amine-appended CO2 sorbent, partly chemisorptive water binding; not a water-harvesting MOF.
- Rank: low for Paper 3A.

### K09 (EXCLUDED, not calorimetric). Cho et al. 2020, KMF-1 (Nat. Commun. 11, 5112)
- Opened https://pmc.ncbi.nlm.nih.gov/articles/PMC7547100/ (2026-10-13). Status FULL (asked about methods). Isosteric heat 52-57 kJ/mol from Clausius-Clapeyron plus virial on isotherms at 20, 30, 40 C; GCMC about -54 kJ/mol. No calorimetry. Useful only as a multi-T isotherm source.

### K10 (EXCLUDED, not calorimetric). Jeremias, Lozan, Henninger, Janiak 2013, UiO-66, UiO-67, H2N-UiO-66, H2N-MIL-125
- Citation: Dalton Trans. 42 (2013) 15967, DOI 10.1039/c3dt51471d (DOI printed on the PDF).
- Opened: Janiak group PDF https://www.ac1.hhu.de/.../Publikations-Dateien_274-583/289.pdf (2026-10-13). Status FULL.
- The "differential heat of adsorption" (89.5 kJ/mol H2N-UiO-66, 56.0 kJ/mol H2N-MIL-125) is from a modified Clausius-Clapeyron on isotherms at 25 and 40 C. NOT independent.

### K11 (EXCLUDED as a heat source). Wickenheisser et al. 2015, MIL-100(Fe,Cr), MIL-101(Cr) xerogel composites
- Micropor. Mesopor. Mater. 215 (2015) 143-153. Opened Janiak group PDF 341.pdf (2026-10-13). Water isotherms at 293 K only; no calorimetry found in text.

### K12 (SEEN-ONLY, TG-DSC heat storage). Makhanya, Oboirien, Musyoka, Ren, Ndungu 2022/2023, PET-derived MOFs
- Citation: "Evaluation of PET-derived metal organic frameworks (MOFs) for water adsorption and heat storage", J. Porous Mater. 30 (2023) 387-401. DOI 10.1007/s10934-022-01351-w: Crossref title matches (2026-10-13).
- Springer page redirected to a login (idp.springer.com); not followed. Status META plus search snippet.
- Snippet claims: water isotherms at 25 and 55 C; heat storage measured by TG-DSC; MIL-101(Cr), UiO-66(Zr), MIL-101(Fe), MIL-88B(Fe), Al-fumarate mentioned. Likely an integral desorption heat (J/g) from TG-DSC, not a differential heat vs loading. Needs full text.
- Rank: medium-low (possible integral calorimetric heat plus 2-T isotherms on same samples, but PET-derived samples and probably integral only).

### K13 (NOT calorimetric, noted). Mileo, Cho, Park, Devautour-Vinot, Chang, Maurin 2019, MIL-100(Fe)
- J. Phys. Chem. C 123 (2019) 23014-23025, DOI 10.1021/acs.jpcc.9b06228 (Crossref title match 2026-10-13). HAL copy behind Anubis bot check; figshare 403. META only. No Llewellyn coauthor; experimental enthalpy most likely isosteric. Not pursued.

### K14 (SEEN-ONLY, TG-DSC integral heat on composites). Permyakova et al. 2017, salt-MOF composites
- "Design of salt-metal organic framework composites for seasonal heat storage applications", J. Mater. Chem. A 5 (2017), DOI 10.1039/c7ta03069j (DOI resolves per search listing; Crossref check pending). RSC PDF returned 403; ESI URL returned 404. Status META plus snippets.
- Snippet: a TG-DSC111 (Setaram) with humidity generator; cycle 30 C adsorption / 80 C desorption at 12.5 mbar; energy storage capacities (integral) of CaCl2 composites of MIL-100(Fe), MIL-101(Cr), MIL-127(Fe) etc. Integral cycle heats, not differential heat vs loading; composites, not neat MOFs. Low value for Paper 3A.

### K15 (EXCLUDED). Celic et al. 2022, MIL-96(Al), MIL-100(Al), MIL-110(Al)
- Nanomaterials 12 (2022) 2092, DOI 10.3390/nano12122092. Read via Europe PMC full text XML https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9231181/fullTextXML (2026-10-13), FULL (first 100k chars). Heat from Dubinin-Radushkevich on a single 313 K isotherm; TG/DTA used only for mass loss. Not calorimetric.

### K16 (EXCLUDED). Ho et al. 2023, NU-1500-Cr (Commun. Chem. 6, 70)
- Read via Europe PMC XML (2026-10-13). Enthalpy from MD simulation; one experimental isotherm at 25 C. Not calorimetric.

### K17 (SEEN-ONLY, method unknown). Camur et al. 2023, monolithic UiO-66, UiO-66-NH2, Zr-fumarate (MOF-801)
- "Monolithic Zirconium-Based Metal-Organic Frameworks for Energy-Efficient Water Adsorption Applications", Adv. Mater. 35 (2023), DOI 10.1002/adma.202209104. Abstract read via Europe PMC core record (2026-10-13): not OA at publisher; Alicante repository handle 10045/133853 timed out. Coauthors include Silvestre-Albero (immersion calorimetry lab) and Fraunhofer ISE (Huegenell, Ernst).
- Snippet only: monoUiO-66 dH_ads about -60 kJ/mol at low coverage, about -35 at 10 wt%, about -40 from 15 wt% to saturation; UiO-66-NH2 about -108. Method of determination not seen; could be isosteric. Needs full text before use.

### K18 (EXCLUDED as calorimetry for water vapour). Other checks
- Zaworotko/Bezrukov square-lattice networks (ACS AMI 2024, PMC11232023, read 2026-10-13): no calorimetry, one 298 K water isotherm.
- Bushuev et al. 2026 J. Phys. Chem. C 130, 2057 (DOI 10.1021/acs.jpcc.5c08036): high-pressure intrusion calorimetry into pure-silica LTA zeolites; not MOF, not vapour adsorption.
- Solovyeva, Aristov et al. CAU-10-X (Langmuir 37 (2021) 693, DOI 10.1021/acs.langmuir.0c02729) and MIL-160 (Energies 2021): abstracts list TG isobars/isotherms 5-100 C and isosteric heats; no calorimetry. Good multi-T isotherm sources only.
- Froehlich PhD dissertation (Duesseldorf, docserv Derivate-45136), text searched 2026-10-13: SETARAM Sensys evo used only for heat capacity of Al-fumarate; no calorimetric heat of adsorption. Confirms K02.
- Weber, Bezverkhyy, Bellat et al. 2016 Ga-MIL-53 (TGA, DSC, XRD at 298 K; abstract via search snippet): breathing material, single T; not pursued.

### K19 (SUPPORT for K03: multi-T isotherms of MOF-801 from the lab that made the K03 sample). Furukawa et al. 2014
- Citation: H. Furukawa, F. Gandara, Y.-B. Zhang, J. Jiang, W. L. Queen, M. R. Hudson, O. M. Yaghi, "Water Adsorption in Porous Metal-Organic Frameworks and Related Materials", J. Am. Chem. Soc. 136 (2014) 4369-4381. DOI 10.1021/ja500330a (Crossref title match 2026-10-13).
- Opened: Yaghi group PDF https://yaghi.berkeley.edu/pdfPublications/14-watermofs.pdf (2026-10-13), text extracted. Status FULL (main text; SI figures S52 and S54 not opened).
- Water isotherms of MOF-801-P and MOF-841 at various temperatures between 15 and 55 C (BELSORP-aqua3). Isosteric Qst by Clausius-Clapeyron, about 60 kJ/mol for MOF-801-P. Not calorimetric. Its value is that it is the multi-T isotherm set from the lab that supplied the K03 calorimetry sample (Furukawa, Zhang and Jiang coauthor both). Same synthesis lab; same batch not established.
- Note: the K03 calorimetric integral value of 2960 kJ/kg_water is about 53.3 kJ/mol, against the isosteric value of about 60 kJ/mol here. That makes it a useful, honest test case.

### K20 (SEEN-ONLY, companions to K06). Khan and Mitra: more calorimetric papers (IIT Kharagpur)
- M. A. Khan, S. Mitra, "Modifying volumetric adsorption setup for combined measurement of adsorption heat and uptake", Measurement 258 (2026) 119138, DOI 10.1016/j.measurement.2025.119138 (Crossref metadata read 2026-10-13; no abstract in the record). This is the method paper for the K06 rig.
- M. A. Khan, S. Mitra, "Enhancing Atmospheric Water Harvesting: A Comparative Study of Water Vapor Adsorption on Material Institute Lavoisier-101(Cr), Metal-Organic Framework-801 and Regular Density-Silica Gel", Heat Transf. Eng. 47 (2025/2026) 1770-1779, DOI 10.1080/01457632.2025.2553979 (Crossref metadata). Snippet: MIL-101(Cr) characterized at 303-333 K and 0.63-15.5 kPa. Not known whether MOF-801 heats were measured calorimetrically.
- M. A. Khan, K. Thu, S. Mitra, "Experimental evaluation of Adsorption Heat for Water vapour/Silica gel pair for chiller application", Appl. Therm. Eng. (2024) 123289, DOI 10.1016/j.applthermaleng.2024.123289 (Crossref metadata). Not a MOF, but it is a calorimetric benchmark on a reference adsorbent from the same rig.
- M. A. Khan, S. Mitra, book chapter "Measurement of heat of adsorption as a framework for identifying consistent isotherm equation", in Gas-Solid Adsorption Thermodynamics (2026), DOI 10.1016/b978-0-443-29815-8.00006-9.
- Snippet from a ResearchGate listing seen in search, not opened: directly measured Qst for water/MIL-101(Cr) falls from about 2965 to 2600 kJ/kg (about 53.4 to 46.8 kJ/mol). The corrected Dubinin-Serpinsky equation is the most consistent for MIL-101(Cr), and Dubinin-Astakhov for RD silica gel. Sample about 0.75 g. SEEN-ONLY.

### K21 (EXCLUDED). Cui et al. 2019, MIL-160 heat properties
- Appl. Therm. Eng. 161 (2019) 114135, DOI 10.1016/j.applthermaleng.2019.114135 (Crossref title match). Snippets: specific heat by DSC (20-75 C) and thermal conductivity; no heat of adsorption seen. The HAL INRAE copy was not opened. Not a calorimetric heat of adsorption.

### K22 (EXCLUDED). Other screened items
- Kloss et al. 2024, CPO-27 analogues (Nanomaterials 14, 1791; Europe PMC XML read 2026-10-13): 298 K isotherms, no calorimetry.
- Iacomi PhD thesis (Aix-Marseille 2018, supervised by Llewellyn; theses.fr API read 2026-10-13): microcalorimetry on UiO-66, DUT-49 and others, but the abstract does not name water.
- TU Dresden "optical calorimetry" (InfraSORP IR thermography) for MOF water uptake: semi-quantitative screening, not a differential heat. Excluded.
- Wang et al. 2018, MIP-200 (Nat. Energy 3, 985; DOI 10.1038/s41560-018-0261-6): the HAL copy is behind Anubis and the enthalpy method was not seen. META only.
- COFs: no search (Europe PMC or web) found a calorimetric heat of water adsorption for any COF. The only COF hit (TB-COF-Li, Angew. 2025) reports an evaporation enthalpy of adsorbed water, not an adsorption heat, and its method was not seen.

## DOI verification table (Crossref, 2026-10-13)
| Key | DOI | Crossref title matches |
|---|---|---|
| K01 | 10.3390/en13113003 | yes |
| K02 | 10.1039/c6ta01757f | yes |
| K03 | 10.1038/srep19097 | yes |
| K04 | 10.1021/acs.jpcc.5b12239 | yes |
| K05 | 10.1021/ja1023282 | yes |
| K06 | 10.1016/j.icheatmasstransfer.2025.109443 | yes |
| K08 | 10.1021/acs.jpcc.9b08008 | yes |
| K09 | 10.1038/s41467-020-18968-7 | yes |
| K10 | 10.1039/c3dt51471d | yes |
| K12 | 10.1007/s10934-022-01351-w | yes |
| K13 | 10.1021/acs.jpcc.9b06228 | yes |
| K14 | 10.1039/c7ta03069j | yes |
| K15 | 10.3390/nano12122092 | yes |
| K17 | 10.1002/adma.202209104 | Crossref returned the record. A local encoding error stopped the title printing, so the title was confirmed through Europe PMC instead. |
| K19 | 10.1021/ja500330a | yes |
| K20 | 10.1016/j.measurement.2025.119138; 10.1080/01457632.2025.2553979 | yes |
| K21 | 10.1016/j.applthermaleng.2019.114135 | yes |

## Access notes
- Not bypassed: HAL (hal.science, hal.umontpellier.fr) and Fraunhofer Publica showed Anubis bot checks, and PMC showed a reCAPTCHA once. MDPI, RSC, ScienceDirect, ResearchGate and figshare returned 403, and Springer redirected to a login. OpenAlex returned HTTP 429 (Retry-After about 86 min), Semantic Scholar returned 429 or 404, and Unpaywall rejected the placeholder email (422).
- Full texts came from PMC, Europe PMC XML, OSTI, KU Leuven Lirias, the Di Wu lab site, the Janiak group site and the Yaghi group site. One file, the Froehlich dissertation (36 MB, Duesseldorf docserv), was fetched with curl into the session scratchpad for text search, because WebFetch has a 10 MB limit.

## Ranked table (usefulness for Paper 3A)
| Rank | Key | Material | Calorimetric method | T of calorimetry | Heat vs loading | Multi-T isotherms, same sample or lab | Verified |
|---|---|---|---|---|---|---|---|
| 1 | K06 (+K20) | MIL-101(Cr) | in-situ calorimetry in a modified volumetric rig | 298-338 K (stated range) | yes (direct Qst vs uptake, per snippet) | yes, same rig, 298-338 K | SEEN-ONLY; needs full text |
| 2 | K03 (+K19) | MOF-801 | DSC plus TGA desorption cycle (TA Discovery) | 30 C reference | one integral value (2960 kJ/kg over 19-20 wt%); model curve as figure only | yes: same paper (DVS, temperatures only in Fig. 1a) and same lab (15-55 C, K19) | FULL |
| 3 | K04 | HKUST-1 | Calvet gas-adsorption calorimetry (Setaram SenSYS) | 25 C | yes; Table 1 gives three ranges, Fig. 2B the curve | no (25 C only); other labs only; MOF is unstable in water | FULL |
| 4 | K05 | MIL-53(Cr) | microcalorimetry (Llewellyn lab) | probably 303 K (unconfirmed) | unknown | unknown; breathing framework | ABS |
| 5 | K08 | mmen-Mg2(dobpdc) | Calvet (Sensys Evo) plus 3Flex | 25 C | yes, figure plus plateau values | no | FULL |
| 6 | K12 | PET-derived MIL-101(Cr), UiO-66 and others | TG-DSC heat storage (probably integral) | unknown | probably no | isotherms at 25 and 55 C on the same samples | SEEN-ONLY |
| 7 | K14 | CaCl2-MOF composites | TG-DSC111 integral cycle heat | 30/80 C | no | no | SEEN-ONLY |
| 8 | K17 | monolithic UiO-66, UiO-66-NH2, Zr-fumarate | unknown (may be isosteric) | unknown | yes (values seen) | unknown | SEEN-ONLY |
| excluded | K01, K02, K07, K09, K10, K11, K13, K15, K16, K18, K21, K22 | various | isosteric, DR, QE-TPDA, MD, or none | | | | |

Non-MOF calorimetric controls with isotherms in the same paper: zeolites 13X and MgY in K03 (DSC/TGA, integral 3852 and 3985 kJ/kg), and RD silica gel in Khan, Thu and Mitra 2024 (same rig as K06).

## Verdict
On what is verified today, only one MOF allows a clean test: MOF-801. It has K03 calorimetry plus multi-T isotherms from the same paper and the same lab (K19). Even so, the calorimetry is one integral number averaged over 19-20 wt% (about 53.3 kJ/mol), not a differential curve. The test is therefore a point comparison, not a test of curve shape.
HKUST-1 (K04) has true differential calorimetry vs loading, but only at 25 C and with no multi-T isotherms on the same sample. A test would need another lab's isotherms on a different HKUST-1 sample, and HKUST-1 degrades in water. Treat it as a secondary case with caveats.
MIL-101(Cr) (K06 and K20, Khan and Mitra 2025-2026) could be the best case of all: direct calorimetric heat vs uptake and isotherms at 298-338 K in one rig. The paper itself asks which isotherm equation is thermodynamically consistent. Its content has only been SEEN in snippets because ScienceDirect blocked access.
Answer: yes, Paper 3A can test Qst against calorimetry for three MOFs (MOF-801, MIL-101(Cr), HKUST-1). Two conditions apply: the Khan and Mitra full text must be obtained (library access or a request to the authors), and HKUST-1 must be flagged as a single-temperature comparison across labs. Without Khan and Mitra the honest count is one clean MOF (MOF-801) and one weak one (HKUST-1). The 13X, MgY and silica gel controls from the same calorimetric papers can extend the benchmark to non-MOF adsorbents. No calorimetric heat of water adsorption was found for any COF.

