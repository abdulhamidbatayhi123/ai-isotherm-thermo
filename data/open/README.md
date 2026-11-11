# Open isotherm data and how to obtain the rest

`isotherms_open.csv` holds the water adsorption isotherms of the materials whose sources are published under the
Creative Commons Attribution 4.0 licence (CC BY 4.0; licences read from Crossref on 2026-11-12). The lines are copied
verbatim from the frozen data set used for every fit (`data/raw/dataset/isotherms.csv`, SHA-256 in
`FREEZE_MANIFEST.json`), so they parse to exactly the values the confirmatory runs used; `SHA256SUMS` gives the hash of
this file and `scripts/export_open_data.py` writes it. Columns: material, class, set (confirmatory or development),
source key, temperature `T_K` (K), pressure `p_Pa` (Pa), uptake `q_molkg` (mol of water per kg of framework), how
the points were obtained (`provenance`) and relative pressure `rh` (IAPWS saturation pressure).

**Attribution (CC BY 4.0).** The points were digitised by A. Batayhi from the figures listed in `SOURCES.csv` and
converted to the units above (changes made: digitisation, unit conversion, adsorption branch up to p/p_sat = 0.90).
Cite the original articles when using them:
- COF-SO3H: Schweng, P. et al., ChemRxiv 2023, doi:10.26434/chemrxiv-2023-mlmlv (SI Fig. S2); published in
  ChemSusChem 2024, doi:10.1002/cssc.202301906.
- PI-3-COF and NO-PI-3-COF: Grunenberg, L. et al., J. Am. Chem. Soc. 2023, doi:10.1021/jacs.3c02572 (SI Fig. S34).
- HFPTP-DMePDA-COF, HFPTP-PDA-COF, TFBCz-PDA-COF and the development material TFPPy-PDA-COF: Tan, K. T. et al.,
  Nat. Commun. 2021, 12, 6747, doi:10.1038/s41467-021-27128-4 (main Figs. 3a-c and 4i-k).

## The other materials

| Material (set) | Source | Licence of the source | How to obtain the points |
|---|---|---|---|
| CALF-25 (conf.) | NIST/ARPA-E adsorption database (ISODB) records of Taylor et al. 2012 | NIST SRD 205, records marked "All rights reserved" | free public database; record IDs in `scripts/build_dataset.py`; fetched by `data/scripts/isodb_water_inventory.py` |
| Zn2(bptc) (conf.) | ISODB records of Lin et al. 2006 | as above | as above |
| Mg-SU-102 (conf.) | Oppenheim et al. 2025, Nat. Commun., source data of Fig. 4 | CC BY-NC-ND 4.0 | free download of the article's source-data file; read by `scripts/build_dataset.py` |
| Al-fumarate (conf.) | Hanikel et al. 2019, ACS Cent. Sci., SI | ACS AuthorChoice (free to read) | free PDF; `scripts/digitise_sources.py` |
| Co2Cl2(BTDD) (conf.) | Rieth et al. 2017, ACS Cent. Sci., SI | ACS AuthorChoice (free to read) | free PDF; `scripts/digitise_sources.py` |
| COF-482-hydrazide (conf.) | Nguyen et al. 2022, ACS Cent. Sci., SI | CC BY-NC-ND 4.0 | free PDF; `scripts/digitise_sources.py` |
| COF-432 (conf.) | Nguyen et al. 2020, J. Am. Chem. Soc., SI | ACS standard licence | subscription PDF; `scripts/digitise_sources.py` |
| CuBTC, MIL-100 (dev.) | ISODB records of Rezk et al. 2012, Int. J. Heat Mass Transfer | NIST SRD 205 | free public database; record IDs in `scripts/build_dataset.py` |
| MIL-160 (dev.) | ISODB records of Cadiau et al. 2015, Adv. Mater. | NIST SRD 205 | as above |

The source PDFs are downloaded into `data/raw/primary/<key>/` (the download logs record the URLs used); then
`scripts/regenerate_digitisation.sh` regenerates every point list, and the SHA-256 of the full data set in
`FREEZE_MANIFEST.json` shows whether a regenerated set is identical to the one used. Point lists that are not
redistributed here are available to the editor and reviewers in confidence.
