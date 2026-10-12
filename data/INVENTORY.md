# Data inventory for Paper 3A (water isotherms q*(p,T) and isosteric heats of MOFs and COFs)

Compiled 2026-10-12/13 from live sources. Every count below is either produced by a script in `data/scripts/` (the output file is named next to the number) or is marked **[manual]** with the page, figure or file it was read from. Manual readings of papers were made from the downloaded PDFs in `data/raw/primary/<shortkey>/` (each directory has a `download_log.tsv` with source URL and UTC time) or from live PMC / publisher pages. Items that could not be checked are marked UNVERIFIED.

## 0. Files

| Script | Output | What it does |
|---|---|---|
| `scripts/isodb_water_inventory.py` | `isodb_water_records.csv`, `isodb_water_multiT.csv`, `isodb_water_multiT_by_material.csv`, `isodb_water_summary.json`, raw JSON in `raw/isodb/records/` (1221 files), `raw/isodb/index_pure_water.json` | ISODB index, water key, pure-water records, per-record metadata, multi-temperature aggregation, counts |
| `scripts/isodb_priority_materials.py` | `isodb_priority_materials.csv`, `isodb_priority_materials.log` | regex lookup of the priority materials in the ISODB water records |
| `scripts/coremof2024_water_check.py` | `coremof2024_water_summary.json` | reads `raw/coremof2024/water.zip` (Zenodo 15055758) and summarises the water data |
| `scripts/primary_doi_check.py` | `primary_doi_check.csv`, `primary_doi_check.log` | Crossref metadata, Unpaywall OA status/licence and ISODB presence for the curated list `primary_candidates.csv` (38 DOIs) |
| `scripts/primary_numeric_check.py` | `primary_numeric_files_summary.json`, `primary_numeric_check.log` | sheet structure and point counts of the numeric source-data spreadsheets found |

Logs: `isodb_water_inventory.log` (the fetching run), `isodb_water_inventory_rerun.log` (offline rerun with the final class heuristic; the CSV/JSON outputs are from this rerun). Python: the ai-mof-cof-dynamics venv, run with `-I`.

## 1. NIST/ARPA-E ISODB (NIST SRD-205)

### 1.1 Counts (all from `isodb_water_summary.json`, retrieved 2026-10-13T01:09 +0300)

- Water is `XLYOFNOQVPJJNP-UHFFFAOYSA-N` (found by name in `gases.json`).
- Index: 39988 isotherms; 2455 contain water; **1221 are pure water** (water is the only adsorbate). All 1221 records fetched (0 failures).
- 557 distinct material ids (matdb hashkeys), 275 DOIs, 667 material x DOI pairs.
- Pressure units: bar for all 1221. Adsorption units are heterogeneous: mmol/g 521, cm3(STP)/g 194, molecules/unitcell 113, g/g 97, mg/g 54, ml/g 42, wt% 32, 28 records with empty units, and 20 other unit strings (`isotherms_by_adsorption_units`).
- `category` field (index and record): blank 700, `exp` 413, `sim` 98, `mod` 10. The ISODB user guide (p. 4 of `raw/isodb/site_terms/isodb_userguide.pdf`) defines the measurement classes as experiment, simulation, quantum/DFT and modeling. Blank means not categorised, not "measured".
- Measured versus digitised: **there is no field that says "measured" versus "digitised".** The record fields are exactly: DOI, adsorbates, adsorbent, adsorptionUnits, articleSource, category, compositionType, concentrationUnits, date, digitizer, filename, isotherm_data, isotherm_type, pressureUnits, tabular_data, temperature (`record_field_union`). The relevant ones:
  - `tabular_data`: 0 for 1160 records, 1 for 61. The field is not defined on the live site. The NIST programme page (https://www.nist.gov/node/1823066) says isotherms come from "tabular source data (preferred) or digitization of graphical isotherms", so we read `tabular_data = 1` as "taken from a table in the source" and 0 as "digitised from a figure". This is an inference.
  - `digitizer`: a person's name for 529 records, `UNKNOWN` for 692 (`isotherms_by_digitizer`).
  - `articleSource`: the figure or table the points came from (e.g. "Figure 2", "Table 3", "Figure 3 / AIF Supplementary Data"); `UNKNOWN` for 692.
  - The ISODB user guide states the database "contains adsorption isotherms digitized from the cataloged articles" (p. 1). In practice almost all water isotherms in ISODB are digitised experimental (or simulated) curves, not raw instrument data.
- Branch: no adsorption/desorption field exists. From the order of pressure points (`pressure_trend_heuristic`, a heuristic): increasing 1090, up_then_down 57 (loop stored in one record), mixed 61, decreasing 13.
- **No isosteric heat or calorimetric field exists in ISODB records.** Qst must come from the papers.

### 1.2 Multi-temperature coverage (from `isodb_water_summary.json`)

Material class is a regex heuristic on the adsorbent name (matdb `materials.json` has only hashkey, name and synonyms, no class). Order: COF, zeolite, MOF (names, linker abbreviations, metal-bracket formulas, Hill formulas with C plus a framework metal), carbon/polymer, silica/oxide/salt, other. Read `material_name` before trusting a label: e.g. `C214H180O24N2` is "other", and the cross-DOI CuBTC entry mixes 77 K and 550 K records with room-temperature ones.

Same paper (material x DOI pairs), distinct temperatures:

| Threshold | All categories | of which MOF | COF | zeolite | carbon/polymer | silica/oxide/salt | other | exp or blank only |
|---|---|---|---|---|---|---|---|---|
| >= 2 T | 61 | 22 | 2 | 11 | 11 | 4 | 11 | 57 |
| >= 3 T | 44 | 12 | 1 | 8 | 9 | 4 | 10 | 40 |
| >= 4 T | 26 | 8 | 0 | 8 | 4 | 3 | 3 | 24 |

Same material id across papers: >= 2 T: 64 (MOF 23, COF 3); >= 3 T: 46 (MOF 14, COF 1); >= 4 T: 27 (MOF 9, COF 0) (`multiT_materials_across_DOIs_all_categories`). Cross-paper sets mix samples and labs and are weaker evidence than a single-paper set.

The MOF and COF single-paper sets with >= 3 temperatures (`isodb_water_multiT.csv`):

| Material | DOI | T (K) | Category | Units | Note |
|---|---|---|---|---|---|
| CuBTC (HKUST-1) | 10.1016/j.ijheatmasstransfer.2012.07.068 (Rezk 2012) | 293, 301, 309, 317, 325, 333, 341, 349, 358 | blank | mmol/g | two curves per T in several cases (duplicates or two series, check); digitizer UNKNOWN |
| MIL-100 | same | same 9 T | blank | mmol/g | same caveat |
| ZIF-7, ZIF-8 | 10.1016/j.molliq.2017.01.110 | 323 to 358, 8 T | sim | | simulated, not usable as measured data |
| Cu(C10H6O6)(H2O)1.66H2O | 10.1038/Nchem.1003 | 298 to 323, 6 T | blank | mmol/g | flexible hydrophilic/hydrophobic MOF |
| MIL-53(Ga) | 10.1021/Jp412433a | 273, 298, 323, 348, 373 | blank | mol/mol | |
| CALF-25 | 10.1021/Ja306812r | 298, 303, 307, 313 | blank | mmol/g | |
| Zn2C14N2O8H4 | 10.1021/Ja060946u | 288, 298, 308, 318 | blank | wt% | |
| CAU-10-H | 10.1039/C4dt02264e (Fröhlich 2014) | 298, 313, 333 | blank | g/g | 10, 16, 17 points |
| MIL-160 | 10.1002/adma.201502418 (Cadiau 2015) | 293, 303, 313 | exp (+ sim curves) | g/g | SI Fig. S4 per `articleSource` |
| MIL-160(Al) | 10.1007/s10450-020-00286-5 (Silva 2021) | 303, 323, 343 | exp | mmol/g | loops stored per record ("mixed") |
| S-MIL-53(Al) | 10.1016/j.jcat.2011.04.015 | 298, 323, 358 | blank | mmol/g | |
| AB-COF | 10.1021/acs.chemmater.5b02151 (Stegbauer 2015) | 288, 298, 313 | exp | cm3(STP)/g | the only COF with >= 3 T in ISODB |

Priority-material lookup (`isodb_priority_materials.log`): **COF-432: 0 records. MOF-303: 0. CAU-23: 0. KMF-1: 0. M2Cl2(BTDD): 0. MOF-LA2-1: 0.** MOF-801: 3 records, 298 K only (Furukawa 2014). MOF-841: 1 record, 298 K. CAU-10: 17 records, 288 to 333 K over 4 DOIs. Al-fumarate: 8 records, 288 to 313 K over 3 DOIs (multi-T only in Coelho 2016, 288 and 313 K). UiO-66: 31 records, but 273, 298, 303, 353 K come from different papers. Any COF: 33 records, 28 names, 10 DOIs, temperatures 288 to 313 K.

### 1.3 Licence and terms (quoted from the live site, 2026-10-12/13)

- Footer of https://adsorption.nist.gov/isodb/index.php (saved as `raw/isodb/site_terms/isodb_index_retrieved_2026-10-13.html`): "©2016 copyright by the U. S. Department of Commerce on behalf of the United States of America. All rights reserved." Disclaimer: "NIST makes no warranties to that effect, and NIST shall not be liable for any damage that may result from errors or omissions in the Database." Also: "Portions of the dataset contained in this database were collected with financial support from SpringerMaterials."
- Citation guide (live page): cite as Siderius, D.W., Shen, V.K., Johnson III, R.D. and van Zee, R.D., Eds., NIST/ARPA-E Database of Novel and Emerging Adsorbent Materials, NIST, Gaithersburg MD, https://dx.doi.org/10.18434/T43882 (retrieved date).
- User guide (`raw/isodb/site_terms/isodb_userguide.pdf`, p. 1): SRD-205 "is subject to copyright under the Standard Reference Data Act of 1968 ... though this copyright has not been exercised as of 30 September 2015. For inquiries regarding licensing or reproduction of the data contents of SRD-205, please consult the list of database contacts".
- NIST licence statement (https://www.nist.gov/open/license): SRD compilations carry copyright under 15 U.S.C. 290e; other works of NIST employees are not subject to US copyright (17 U.S.C. 105). ISODB is an SRD, so the 17 U.S.C. 105 public-domain rule does **not** automatically apply.
- The official GitHub mirror (github.com/NIST-ISODB/isodb-library) has no licence file (GitHub API `license: null`, checked 2026-10-13).

## 2. CoRE MOF 2024 (Zenodo 10.5281/zenodo.15055758)

- Record v1.1, published 2025-03-20, licence **CC BY 4.0**, concept DOI 10.5281/zenodo.14216941; the API `versions/latest` link resolves to 15055758 itself, so this is the newest version (checked 2026-10-12).
- Files and sizes (bytes, Zenodo API): NCR_FSR_SI.xlsx 187258; NCR_ION_SI.xlsx 22961; NCR_ASR_SI.xlsx 172053; ION_data_SI_20250204.csv 55530; ASR_data_SI_20250204.csv 1081836; unmodified_check_for_NCR_SI.xlsx 154909; **water.zip 12521561**; mofid-v2.zip 4473834; TSA.zip 271657136; FSR_data_SI_20250204.csv 649288; CoREMOF2024DB_SI_20250204.zip 44022768; ASR_FSR_check.csv 217362; 12089-recommended-screening-list.csv 330691. Downloaded: water.zip and the three *_data_SI CSVs (about 13.8 MB) into `raw/coremof2024/`.
- Water data (`coremof2024_water_summary.json`): 15747 AIF files (ASR 8448, FSR 6641, Ion 658). Every file: `_exptl_temperature 298`, `_simltn_forcefield_adsorbent UFF4MOF`, `_simltn_forcefield_adsorptive TIP4P`, loading in molecules/supercell, header "Gibbs Ensemble Monte Carlo Simulation Software: MCCCS-MN ... cutoff=9 Å, simulation cycles: 5E3 + 1.5E4 + 2.5E4". Pressure grid at most 5 points, 0.1, 1, 10, 100, 1000 Pa (7746 files have all 5; 1786 files hold a single point at 4540 Pa); `_adsorp_p0` = 4540 Pa. `water_data.xlsx` adds GEMC loading strings, a free energy of transfer, a Henry-regime point and a `KH_Classes` label (e.g. "weak"); `widom.xlsx` gives `H2O_henry(mmol/g/Pa)` with error per structure (8857 ASR, 7638 FSR, 710 Ion data rows). **No heat of adsorption and no second temperature anywhere.**
- Companion paper: Zhao et al., "CoRE MOF DB: a curated experimental metal-organic framework database with machine-learned properties for integrated material-process screening", Matter 2025, 10.1016/j.matt.2025.102140 (preprint 10.26434/chemrxiv-2024-nvmnr-v2, CC BY-NC-ND per Crossref). **Blocker:** full text could not be read: cell.com shows abstract plus "Get Access", chemRxiv shows a Cloudflare check, HAL and MIT DSpace copies are behind bot protection. The method statement above therefore comes from the AIF metadata in the data itself, which is the authoritative description of what was computed.
- Verdict: **not usable as an arm for temperature extrapolation or Qst.** One temperature, five low pressures (up to 1000 Pa, i.e. below about 0.22 of the TIP4P p0 used), generic force field. At most a 298 K Henry-regime pretraining or sanity signal for hydrophobic versus hydrophilic behaviour. Not recommended for Paper 3A.

## 3. Primary literature (measured water isotherms at >= 2 temperatures)

DOIs were verified at Crossref and OA status/licence taken from Unpaywall by `primary_doi_check.py` (`primary_doi_check.csv`). The brief's COF-432 DOI 10.1021/jacs.0c07062 returns "Resource not found" at Crossref; the correct DOI is **10.1021/jacs.9b13094**. Temperatures, Qst method and data format are **[manual]** readings (source location given). No paper below reports an independent calorimetric heat for water; every Qst is derived from the same isotherms (Clausius-Clapeyron, Dubinin characteristic curve, or virial/fit). ISODB column: number of pure-water ISODB isotherms with that DOI (`primary_doi_check.csv`).

### 3.1 MOFs

| Key | DOI | Material | Ads. T measured [manual] | Qst [manual] | Numeric data | OA / licence (Unpaywall) | ISODB |
|---|---|---|---|---|---|---|---|
| mgsu102_2025_natcommun | 10.1038/s41467-025-59551-2 | Mg-SU-102 | 15, 20, 25, 30, 35, 40, 45, 50, 55 °C (main Fig. 4) | from 25 to 40 °C isotherms, -49 to -56 kJ/mol | **yes**: source data `41467_2025_59551_MOESM3_ESM.xlsx`, sheet Figure4, 22 adsorption points per T (`primary_numeric_files_summary.json`); max RH falls from 0.82 at 15 °C to 0.089 at 55 °C, i.e. a common absolute-pressure range | gold, CC BY-NC-ND | 0 |
| kim2018_natcommun | 10.1038/s41467-018-03162-7 | MOF-801 | 15, 25, 45, 65, 85 °C (SI Note 3, Supp. Fig. 6a; text verified in PDF) | none | figures; main Fig. 1b is vector (0 to 40 % RH, exact extraction possible), SI Fig. 6a raster | gold, CC BY | 0 |
| fathieh2018_sciadv | 10.1126/sciadv.aat3198 | MOF-801, MOF-303 | 10 to 50 °C in 5 K steps, 9 T (SI figs. S6, S23 legends) | characteristic curve + Clausius-Clapeyron (figs. S8, S26) | raster, overlapping curves | gold, CC BY-NC | 0 |
| hanikel2019_mof303 | 10.1021/acscentsci.9b00745 | MOF-303, Al-fumarate (also SAPO-34, 13X) | 10, 25, 35, 50 °C (SI Figs. S17 to S24; legends read visually) | Clausius-Clapeyron, MOF-303 about 52 kJ/mol | raster | gold, ACS AuthorChoice | 0 |
| hanikel2023_la2 | 10.1021/acscentsci.3c00018 | MOF-LA2-1 | 25, 35 °C (SI Fig. S17) | Clausius-Clapeyron, 51 kJ/mol | raster | gold, CC BY | 0 |
| zheng2022_natprotoc | 10.1038/s41596-022-00756-w | MOF-303 (4 routes) | 25 °C only | none | **yes** (figshare 10.6084/m9.figshare.19859002.v3, CC BY 4.0, `SourceData_Isotherm.xlsx`), single T | closed article | 0 |
| cho2020_kmf1 | 10.1038/s41467-020-18968-7 | KMF-1 | 20, 30, 40 °C (main Fig. 2a; verified in PDF) | Clausius-Clapeyron and virial, 52 to 57 kJ/mol | figures; SI Figs. 16 and 18 are vector (characteristic curve, about 30 points per T) | gold, CC BY | 0 |
| lenzen2019_cau23 | 10.1038/s41467-019-10960-0 | CAU-23 | 25, 40, 60 °C (Methods; verified in PDF) | van 't Hoff from isotherms and wDSL fit, -48.2 kJ/mol | raster; SI Fig. 20 legend says "45 °C - fit" beside 40 °C data | gold, CC BY | 0 |
| rieth2017_co2cl2btdd | 10.1021/acscentsci.7b00186 | Co2Cl2(BTDD) | 283, 293, 298 K (SI Fig. S8; verified in PDF) | Clausius-Clapeyron, about 55 kJ/mol at low coverage | raster | gold, ACS AuthorChoice | 0 |
| rieth2019_anion | 10.1021/jacs.9b06246 | Ni2X2(BTDD), X = Cl, Br | conflict: main Fig. 6A says 288, 298, 308 K; SI p. S4 says 283, 293, 298 K | from characteristic curve, about -57 kJ/mol | raster | hybrid, CC BY-NC-ND | 0 |
| frohlich2014_cau10 | 10.1039/c4dt02264e | CAU-10-H | 298, 313, 333 K (from ISODB records) | used by Fröhlich 2016 for Clausius-Clapeyron | digitised in ISODB | hybrid, CC BY-NC | 3 |
| frohlich2016_cau10 | 10.1039/c6ta01757f | CAU-10-H | no new multi-T isotherms; Qst computed from the 2014 data (main text) | abstract says heat "directly measured", text says Clausius-Clapeyron: conflict | | hybrid, CC BY-NC | 0 |
| cadiau2015_mil160 | 10.1002/adma.201502418 | MIL-160, CAU-10, CAU-10-pydc | MIL-160 at 293, 303, 313 K (ISODB, SI Fig. S4) | UNVERIFIED (Wiley blocked) | digitised in ISODB | closed | 8 |
| silva2021_mil160 | 10.1007/s10450-020-00286-5 | MIL-160(Al) | 303, 323, 343 K (ISODB, Fig. 4a/4b) | UNVERIFIED | digitised in ISODB | closed | 6 |
| rezk2012_cubtc_mil100 | 10.1016/j.ijheatmasstransfer.2012.07.068 | CuBTC, MIL-100, silica gel | 293 to 358 K, 9 T (ISODB) | UNVERIFIED | digitised in ISODB | hybrid, CC BY | 43 |
| coelho2016_alfum | 10.1021/acs.iecr.5b03509 | Al-fumarate | 288, 313 K (ISODB) | UNVERIFIED | digitised in ISODB | closed | 3 |
| teo2017_alfum | 10.1016/j.ijheatmasstransfer.2017.06.086 | Al-fumarate | "25 °C to 60 °C" (abstract); exact list UNVERIFIED (ScienceDirect captcha) | isosteres | UNVERIFIED | hybrid, CC BY-NC-ND | 0 |
| bnn1_2026_natcommun | 10.1038/s41467-026-76301-0 | bnn-1-Co, bnn-1-Ni | 25, 35, 45 °C in raster SI Figs. 26 to 27; numeric only 27 and 60 °C | Clausius-Clapeyron from 25/35/45 °C | **partly**: source data MOESM3 sheets Fig 3a/3b, 27 and 60 °C, adsorption and desorption (`primary_numeric_files_summary.json`, 31 rows per sheet incl. headers) | gold, CC BY-NC-ND | 0 |
| furukawa2014_water | 10.1021/ja500330a | MOF-801, MOF-841, UiO-66 and others | 298 K only (ISODB: 12 records, all 298 K) | | digitised in ISODB | green | 12 |
| Not checked in full (publisher blocked) | kim2017_science 10.1126/science.aam8743; hanikel2021_science 10.1126/science.abj0890; lenzen2018_cau10 10.1002/adma.201705869; jeremias2014_alfum 10.1039/c4ra03794d; elsayed2016_alfum 10.1016/j.applthermaleng.2016.01.129; permyakova2017_mil160 10.1002/cssc.201700164; jeremias2012_mil100 10.1039/c2jm15615f | | UNVERIFIED | | | see `primary_doi_check.csv` | 0 each |

### 3.2 COFs

| Key | DOI | COF(s) | Ads. T measured [manual] | Qst [manual] | Numeric data | OA / licence | ISODB |
|---|---|---|---|---|---|---|---|
| nguyen2020_cof432 | 10.1021/jacs.9b13094 | COF-432 | 10, 25, 40 °C (main Fig. 4a caption and p. C text; verified in PDF) | Clausius-Clapeyron, about 48 kJ/mol (SI Section S11) | figure only; SI unread (ACS 403) | green (repository copy behind Cloudflare); article ACS standard licence | 0 |
| ma2026_cof432steam | 10.1021/acs.inorgchem.6c04117 | COF-432 (steam synthesis) | UNVERIFIED (ACS blocked; Crossref abstract only) | UNVERIFIED | UNVERIFIED | closed | 0 |
| nguyen2022_hcof | 10.1021/acscentsci.2c00398 | AB-COF, COF-480-hydrazide, Py-COF-2D, COF-482-hydrazide | 15, 25, 35 °C (SI Figs. S43 to S46) | Clausius-Clapeyron: 49, 50.5, 45, 47 kJ/mol (SI Figs. S47 to S50) | figures only | gold, CC BY-NC-ND | 0 |
| nguyen2025_onset | 10.1021/acscentsci.4c01878 | COF-309, HCOF-2 | 25, 35, 45 °C (SI Figs. S23, S8) | Clausius-Clapeyron, 48.1 and 47 kJ/mol | figures; `oc4c01878_si_005.xlsx` is a literature Qst compilation (12 MOF and 8 COF rows, read in the file), not isotherms | gold, CC BY | 0 |
| grunenberg2023_nitrone | 10.1021/jacs.3c02572 | PI-3-COF, NO-PI-3-COF, TTI-COF series | 15, 25, 35 °C (SI Figs. S34, S35) | Clausius-Clapeyron, about 47 and 50 kJ/mol (SI Fig. S36) | figures; some TTI samples lose capacity between runs | hybrid, CC BY | 0 |
| schweng2024_sulfoCOF | 10.1002/cssc.202301906 | COF-SO3H | 25, 35, 45 °C (SI Fig. S2, preprint) | 42 kJ/mol from 25 and 35 °C only | figures | hybrid, CC BY | 0 |
| tan2021_watercluster | 10.1038/s41467-021-27128-4 | seven COFs (HFPTP-PDA etc.) | 283.15, 288.15, 298.15 K (Methods) | Clausius-Clapeyron, 41.4 to 46.7 kJ/mol | figures; SI Table 3 gives step position, uptake and Qst per T, not full isotherms | gold, CC BY | 0 |
| abdulhalim2025_ketoenamine | 10.1002/smll.202508046 | COF-TP-43 | 25, 35, 45 °C (SI Fig. S24) | none | figures | hybrid, CC BY-NC-ND | 0 |
| xu2024_gtub5cof | 10.1038/s41467-024-51950-1 | GTUB5-COF (low porosity, type II) | 283, 293, 303 K (main Fig. 10b) | about -21 kJ/mol | figures; paper has internal inconsistencies | gold, CC BY | 0 |
| stegbauer2015_azineCOF | 10.1021/acs.chemmater.5b02151 | AB-COF, ATFG-COF | 288, 298, 313 K for AB-COF (ISODB); paper UNVERIFIED (ACS blocked) | UNVERIFIED | digitised in ISODB | closed | 9 |

## 4. Per-material summary (candidates with >= 3 measured temperatures)

"n pts" is per isotherm. "Digitise" means figures only. Sources: section 3 tables; ISODB numbers from `isodb_water_multiT.csv` / `isodb_priority_materials.csv`.

| Material | Class | Temperatures | Source and form | n pts | Qst available | Licence of source |
|---|---|---|---|---|---|---|
| Mg-SU-102 | MOF | 9 T, 15 to 55 °C | numeric source data | 22 (script) | yes, from isotherms | CC BY-NC-ND |
| MOF-303 | MOF | 10, 25, 35, 50 °C (and 9 T in Fathieh 2018) | digitise | about 60 to 80 [manual, Hanikel 2019 SI] | yes, from isotherms | ACS AuthorChoice; CC BY-NC |
| MOF-801 | MOF | 15, 25, 45, 65, 85 °C (Kim 2018); 9 T (Fathieh 2018) | digitise (part vector) | about 13 [manual, Kim 2018 SI Fig. 6a] | Fathieh only | CC BY; CC BY-NC |
| CuBTC, MIL-100 | MOF | 9 T, 293 to 358 K | ISODB digitised | 16 to 71 (script) | not in ISODB | CC BY (article); ISODB terms |
| KMF-1 | MOF | 20, 30, 40 °C | digitise (vector characteristic curve) | about 30 [manual, SI Fig. 18] | yes | CC BY |
| CAU-23 | MOF | 25, 40, 60 °C | digitise | about 20 to 30 [manual, Fig. 2a] | yes | CC BY |
| CAU-10-H | MOF | 298, 313, 333 K | ISODB digitised | 10, 16, 17 (script) | Fröhlich 2016 (derived) | CC BY-NC; ISODB terms |
| MIL-160(Al) | MOF | 293, 303, 313 K and 303, 323, 343 K | ISODB digitised | 8 to 55 (script; the 14-point 303 K curve is `sim`) | UNVERIFIED | closed; ISODB terms |
| Co2Cl2(BTDD) | MOF | 283, 293, 298 K | digitise | UNVERIFIED | yes | ACS AuthorChoice |
| Ni2X2(BTDD) | MOF | 3 T (temperature conflict) | digitise | UNVERIFIED | yes (characteristic curve) | CC BY-NC-ND |
| COF-432 | COF | 10, 25, 40 °C | digitise main Fig. 4a | UNVERIFIED | yes, about 48 kJ/mol | closed (ACS) |
| COF-309, HCOF-2 | COF | 25, 35, 45 °C | digitise | UNVERIFIED | yes | CC BY |
| AB-COF, COF-480-hydrazide, Py-COF-2D, COF-482-hydrazide | COF | 15, 25, 35 °C | digitise | UNVERIFIED | yes | CC BY-NC-ND |
| PI-3-COF, NO-PI-3-COF | COF | 15, 25, 35 °C | digitise | UNVERIFIED | yes | CC BY |
| seven Jiang-group COFs | COF | 10, 15, 25 °C | digitise | UNVERIFIED | yes | CC BY |
| COF-SO3H | COF | 25, 35, 45 °C | digitise | 5 % RH steps to 90 % [manual, preprint SI] | yes (2 T only) | CC BY |
| AB-COF (Lotsch) | COF | 288, 298, 313 K | ISODB digitised | 83, 28, 38 (script) | UNVERIFIED | closed; ISODB terms |

## 5. Licence position (conservative; not legal advice)

- **Redistributable with attribution:** CoRE MOF 2024 Zenodo files (CC BY 4.0); MOF-303 source data on figshare (CC BY 4.0); digitised values from CC BY articles (Kim 2018, Cho 2020, Lenzen 2019, Hanikel 2023, Nguyen 2025, Grunenberg 2023, Schweng 2024, Tan 2021, Xu 2024, Rezk 2012 per Unpaywall).
- **Non-commercial only:** CC BY-NC sources (Fathieh 2018, Fröhlich 2014/2016, Jeremias 2014). A public academic repository is compatible with NC if attribution is kept.
- **No derivatives:** CC BY-NC-ND sources (Mg-SU-102 source data, bnn-1 source data, Nguyen 2022, Rieth 2019, Abdulhalim 2025). Use the values for analysis; do not republish the spreadsheets or a reformatted copy. Provide a fetch script instead.
- **Closed / ACS standard licence:** COF-432, Cadiau 2015, Silva 2021, Coelho 2016, Stegbauer 2015 and the blocked Science/Wiley/RSC papers. Publish only our own fitted parameters and predictions plus a digitisation recipe (axis calibration and point list stay local), or ask the authors for numeric data.
- **ISODB:** copyright notice "All rights reserved" with the SRD copyright stated as not exercised (2015 user guide) and no licence file on the mirror. Recommend fetch-on-demand through `isodb_water_inventory.py`, cite DOI 10.18434/T43882 and each original paper, and do not commit the raw JSON. If redistribution matters, email the ISODB contacts listed in the user guide.
- Implemented: `data/.gitignore` keeps all of `raw/` out of git except the download logs and the saved ISODB terms page. The COF-432 PDF in `raw/primary/nguyen2020_cof432/` was downloaded from the Yaghi group website and is ACS copyrighted; keep it private.

## 6. Recommended candidate set for Paper 3A

Principle: numeric or high-density data with >= 3 temperatures for training; extreme temperatures and a different framework class for testing. Qst "ground truth" in every paper is derived from the same isotherms, so Qst tests are consistency tests unless independent calorimetry is added (section 7).

**Training (MOFs, >= 3 T, same sample and lab):**
1. Mg-SU-102: 9 T numeric; train on interior T, also the cleanest within-material extrapolation test (hold out 15 and 55 °C).
2. MOF-303: Hanikel 2019 (10, 25, 35, 50 °C), cross-checked against Fathieh 2018 (9 T). Digitise.
3. MOF-801: Kim 2018 (15 to 85 °C, 5 T; widest temperature span found). Digitise; use the vector Fig. 1b where it covers the range.
4. CuBTC and MIL-100: Rezk 2012 via ISODB, 9 T. Resolve the duplicate curves per T first.
5. CAU-10-H (ISODB, 298 to 333 K), MIL-160 (ISODB, two papers spanning 293 to 343 K), KMF-1 (20, 30, 40 °C), CAU-23 (25, 40, 60 °C), Co2Cl2(BTDD) (283, 293, 298 K).

**Held-out set:**
- Temperature hold-out within materials: highest and lowest T of Mg-SU-102, MOF-801 (85 °C), CuBTC/MIL-100 (358 K), CAU-23 (60 °C).
- Class hold-out (COFs, none used in training): COF-432 (10, 25, 40 °C), COF-309 and HCOF-2 (25, 35, 45 °C), the four hydrazide COFs (15, 25, 35 °C), PI-3-COF pair (15, 25, 35 °C), AB-COF (ISODB 288, 298, 313 K; also 15/25/35 °C in Nguyen 2022, a second-lab replicate).
- Qst hold-out: compare predicted Qst with the paper values above, and with the 20 literature values in `raw/primary/nguyen2025_onset/oc4c01878_si_005.xlsx`.

**COF-432 status:** correct DOI 10.1021/jacs.9b13094 (JACS 2020, 142, 2218). Adsorption and desorption isotherms at 10, 25 and 40 °C in main Fig. 4a, Clausius-Clapeyron Qst about 48 kJ/mol, no calorimetry, no numeric data found, absent from ISODB (0 records), article closed. Usable only after digitising Fig. 4a (three curves) from the locally held PDF; numeric data should be requested from the authors (O. M. Yaghi / H. L. Nguyen), which fits the planned Yaghi contact. The 2026 Inorg. Chem. COF-432 paper could add a second sample but its temperatures are unverified.

## 7. Gaps, digitisation needs and blockers

Gaps:
- No independent calorimetric water heats were found for any candidate (all Qst are isotherm-derived). Calorimetry papers (TG-DSC or microcalorimetry on Al-fumarate, CAU-10-H, MIL-160, MOF-801, UiO-66) still need a dedicated search.
- Only one data set gives numeric multi-T isotherms (Mg-SU-102). bnn-1 gives numeric 27 and 60 °C only.
- Few COF data above 45 °C and none below 10 °C.
- Pressure axes differ (P/P0, RH %, kPa, bar). Conversion to absolute pressure needs a stated p_sat(T) per paper (IAPWS); record which one each paper used.

To digitise (WebPlotDigitizer 4.x, automatic or manual point mode, one calibration per panel; record axis points and the image DPI):
- COF-432 Fig. 4a; HCOF SI Figs. S43 to S46; COF-309/HCOF-2 SI Figs. S23, S8; nitrone COF SI Figs. S34 to S35; Tan 2021 Figs. 3a to 3c; COF-SO3H SI Fig. S2; MOF-303 Hanikel 2019 SI Figs. S17 and S19; MOF-801 Kim 2018 Supp. Fig. 6a (and vector Fig. 1b); KMF-1 Fig. 2a (and vector SI Fig. 18); CAU-23 Fig. 2a; Co2Cl2(BTDD) SI Fig. S8; Ni2X2(BTDD) Fig. 6A.
- For vector figures (Kim 2018 Fig. 1b, KMF-1 SI Figs. 16 and 18) extract the path coordinates from the PDF instead; the error is then the plotting precision, not the reader.
- Error estimate: do not assume one. Measure it: digitise Mg-SU-102 main Fig. 4 and the MOF-303 Nature Protocols figure, for which the numeric source data exist, and report the RMS and maximum deviation in uptake (g/g) and in RH. Apply that error (scaled to each figure's axis span and resolution) as the measurement noise for all digitised sets, and propagate it to the Clausius-Clapeyron Qst.

Blockers met (recorded, not worked around): pubs.acs.org, science.org, Wiley, RSC, cell.com (Cloudflare 403 or challenge); sciencedirect.com and EPFL infoscience (captcha); chemRxiv pages and API, HAL and MIT DSpace (bot protection); PMC file links (proof-of-work page; Europe PMC supplementary-files service used instead); Claude in Chrome extension not connected. Consequences: the COF-432 SI, Stegbauer 2015, Ma 2026, Cadiau 2015, Permyakova 2017, Jeremias 2012/2014, Kim 2017, Hanikel 2021 and the CoRE MOF method section were not read.

Lead not downloaded: Bezrukov et al. 2023 (10.1016/j.xcrp.2023.101252, CC BY) with a 607 MB Zenodo dataset (10.5281/zenodo.6631711); a 2026 Zenodo code/data record 10.5281/zenodo.23222539 (MIT licence) fits ISODB water isotherms and is a secondary source only.
