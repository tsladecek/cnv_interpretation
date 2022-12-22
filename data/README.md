# Data

Data used for evaluation of results and construction of figures and tables present in the manuscript

- **beds/**: contains lists of cnvs downloaded from ClinVar separated to `train`, `validation`, `test`, `test-long` (CNV length > 5MBp), `test-multiple` (CNV duplicated more than once or deleted on both chromosomes), `likely` (CNVs with ClinVar labels *likely benign* or *likely pathogenic*), `uncertain` (CNVs with ClinVar label *uncertain significance*)
- **evaluation_data/** - data for evaluation of clinical CNVs
- **benign_cnv_database_comparison.tsv.gz** - marcnv predictions with different databases of Benign CNVs at different population frequency thresholds
- **marcnv.tsv.gz** - marcnv predictions of CNVs with variable database of benign CNVs and HI genes option and fixed population frequency (0.5) and variable selection of loss only or loss + gain benign CNVs for CNV loss (section 2F)
- **metadata.tsv.gz** - metadata (ClinVar label, multiplicity, ClinVar label review, gold stars) to all CNVs in the `beds/` folder 