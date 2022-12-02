import numpy as np
from isv import isv
import pandas as pd
from collections import Counter
from scripts.helpers import acmg_severity


def get_label_acmg(row, col_name):
    acmg_labels = ['Benign', 'Likely benign', 'Uncertain significance', 'Likely pathogenic', 'Pathogenic']
    marcnv_score = row[col_name]
    if marcnv_score <= -0.99:
        return acmg_labels[0]
    elif marcnv_score < -0.89:
        return acmg_labels[1]
    elif marcnv_score < 0.89:
        return acmg_labels[2]
    elif marcnv_score < 0.99:
        return acmg_labels[3]
    elif marcnv_score >= 0.99:
        return acmg_labels[4]
    else:
        return 'None'


def get_coordintates(row):
    return str(row.chrom) + ':' + str(row.start) + '-' + str(row.end)


def get_marcnv_isv_score(row, isv_ratio):
    return row.marcnv_score + isv_ratio * (row.isv_score - 0.5)


def get_cnv_type(row):
    if row.cnv_type == 'DEL':
        return 'loss'
    else:
        return 'gain'


def get_mdx_eval(row, col_name):
    label = row[col_name]
    acmg_labels = ['Benign', 'Likely benign', 'Uncertain significance', 'Likely pathogenic', 'Pathogenic']
    if label == 'VUS / likely pathogenic':
        return acmg_labels[3]
    elif label == 'VUS / likely benign':
        return acmg_labels[1]
    elif label == 'VUS / pathogenic':
        return acmg_labels[3]
    elif label == 'B-VUS':
        return acmg_labels[1]
    elif label == 'VUS-patogénny conflicting':
        return 'VUS-pathogenic conflicting'
    else:
        return label


cnvs_all = pd.read_csv("./data/evaluation_data/marcnv_svk.tsv.gz", sep='\t')
loss = cnvs_all[cnvs_all.cnv_type == 'loss']
loss['cnv_type'] = 'DEL'
gain = cnvs_all[cnvs_all.cnv_type == 'gain']
gain['cnv_type'] = 'DUP'
cnvs_marcnv = loss.append(gain)
cnvs = cnvs_marcnv[['chrom', 'start', 'end', 'cnv_type']]

results = isv(cnvs, proba=True, shap=False)
results_category = isv(cnvs, proba=False, shap=False)
results_isv = results.merge(results_category, on=['chrom', 'start', 'end', 'cnv_type'])
results_isv_marcnv = results_isv.merge(cnvs_marcnv, on=['chrom', 'start', 'end', 'cnv_type'])
results_isv_marcnv['marcnv_score'] = results_isv_marcnv[['section1_score', 'section2_score', 'section3_score',
                                                         'section4_score', 'section5_score']].sum(axis=1)
results_isv_marcnv.rename(columns={'ISV_x':'isv_score', 'ISV_y':'isv_label'}, inplace=True)
results_isv_marcnv['marcnv_label'] = results_isv_marcnv.apply(lambda row: get_label_acmg(row, 'marcnv_score'), axis=1)
results_isv_marcnv['GRCh38'] = results_isv_marcnv.apply(lambda row: get_coordintates(row), axis=1)
results_isv_marcnv['Typ aberácie'] = results_isv_marcnv.apply(lambda row: get_cnv_type(row), axis=1)
results_isv_marcnv.to_csv("./data/evaluation_data/marcnv_isv_svk.tsv", sep="\t", index=False)


# zlepit s vyhodnotemim podla klinikov
arr2020_coordinates = pd.read_csv("./data/evaluation_data/arr2020.tsv", sep='\t')
arr2020_mdx_eval = pd.read_csv("./data/evaluation_data/arr2020_mdx_evaluation.csv", sep='\t')
arr2020 = arr2020_coordinates.merge(arr2020_mdx_eval, on=['IDN', 'P.č.'])
arr2020_mdx_isv_marcnv = arr2020.merge(results_isv_marcnv, on=['GRCh38', 'Typ aberácie'])
arr2020_mdx_isv_marcnv.to_csv('./data/evaluation_data/arr2020_mdx_isv_marcnv.tsv', sep='\t', index=False)

gs_coordinates = pd.read_csv("./data/evaluation_data/gs2020.tsv", sep='\t')
gs_mdx_eval = pd.read_csv("./data/evaluation_data/gs2020_mdx_evaluation.csv", sep='\t')
gs = gs_coordinates.merge(gs_mdx_eval, on=['IDN', 'P.č.'])
gs_mdx_isv_marcnv = gs.merge(results_isv_marcnv, on=['GRCh38', 'Typ aberácie'])
gs_mdx_isv_marcnv.rename(columns={'MDX predtým': 'predtym MDX', 'MDX teraz': 'teraz MDX'}, inplace=True)
gs_mdx_isv_marcnv.to_csv('./data/evaluation_data/gs2020_mdx_isv_marcnv.tsv', sep='\t', index=False)

# kombinacia ISV + marcnv
# marcnv + isv_ratio * (isv_prob - 0.5)
cnvs_mdx_isv_marcnv = arr2020_mdx_isv_marcnv.append(gs_mdx_isv_marcnv)

isv_ratio = 1.99
cnvs_mdx_isv_marcnv['marcnv_isv_1_99'] = cnvs_mdx_isv_marcnv.apply(lambda row: get_marcnv_isv_score(row, isv_ratio), axis=1)

isv_ratio = 0.19
cnvs_mdx_isv_marcnv['marcnv_isv_0_19'] = cnvs_mdx_isv_marcnv.apply(lambda row: get_marcnv_isv_score(row, isv_ratio), axis=1)

cnvs_mdx_isv_marcnv['marcnv_isv_1_99_label'] = cnvs_mdx_isv_marcnv.apply(lambda row: get_label_acmg(row, 'marcnv_isv_1_99'), axis=1)
cnvs_mdx_isv_marcnv['marcnv_isv_0_19_label'] = cnvs_mdx_isv_marcnv.apply(lambda row: get_label_acmg(row, 'marcnv_isv_0_19'), axis=1)
cnvs_mdx_isv_marcnv.to_csv('./data/evaluation_data/cnvs_svk_mdx_isv_marcnv_evaluation_2.tsv', index=False, sep='\t')


isv_ratios = np.arange(0, 2, 0.1)
for isv_ratio in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1. , 1.1, 1.2,
                  1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9]: #isv_ratios:
    col_name_ratio = 'marcnv_isv_' + str(isv_ratio)
    cnvs_mdx_isv_marcnv[col_name_ratio] = cnvs_mdx_isv_marcnv.apply(lambda row: get_marcnv_isv_score(row, isv_ratio), axis=1)
    col_name_ratio_label = col_name_ratio + '_label'
    cnvs_mdx_isv_marcnv[col_name_ratio_label] = cnvs_mdx_isv_marcnv.apply(lambda row: get_label_acmg(row, col_name_ratio), axis=1)
cols_to_save = ['IDN']
cnvs_mdx_isv_marcnv[cols_to_save].to_csv('./data/evaluation_data/cnvs_svk_mdx_isv_marcnv_evaluation_isv_ratio.tsv', index=False, sep='\t')


for isv_ratio in [0.19, 1, 1.99, 2]:
    col_name_ratio = 'marcnv_isv_' + str(isv_ratio)
    cnvs_mdx_isv_marcnv[col_name_ratio] = cnvs_mdx_isv_marcnv.apply(lambda row: get_marcnv_isv_score(row, isv_ratio),
                                                                    axis=1)
    col_name_ratio_label = col_name_ratio + '_label'
    cnvs_mdx_isv_marcnv[col_name_ratio_label] = cnvs_mdx_isv_marcnv.apply(
        lambda row: get_label_acmg(row, col_name_ratio), axis=1)

cnvs_mdx_isv_marcnv.to_csv('./data/evaluation_data/cnvs_svk_mdx_isv_marcnv_evaluation_isv_ratio_019_1_199_2.tsv', index=False, sep='\t')


cnvs_mdx_isv_marcnv = pd.read_csv("./data/evaluation_data/cnvs_svk_mdx_isv_marcnv.csv", sep='\t')
cnvs_mdx_isv_marcnv['MDX_evaluation_old'] = cnvs_mdx_isv_marcnv.apply(lambda row: get_mdx_eval(row, 'predtym MDX'), axis=1)
cnvs_mdx_isv_marcnv['MDX_evaluation_recent'] = cnvs_mdx_isv_marcnv.apply(lambda row: get_mdx_eval(row, 'teraz MDX'), axis=1)
cnvs_mdx_isv_marcnv.to_csv("./data/evaluation_data/cnvs_svk_mdx_isv_marcnv.csv", sep='\t', index=False)


## nove zjednotene vyhodnotenia (tie co boli konfliktne MDX)
# zlepit s predchadzajucim suborom
cnvs = pd.read_csv("./data/evaluation_data/cnvs_svk_mdx_isv_marcnv_old.tsv", sep='\t')
zjednotene_interpretacie = pd.read_csv("./data/evaluation_data/mdx_zjednotena_interpretacia.csv", sep='\t')
cnvs_zjednotene_interpretacie = cnvs.merge(zjednotene_interpretacie, how='left', on=['IDN'])
cnvs_zjednotene_interpretacie.to_csv("./data/evaluation_data/cnvs_zjednotene_mdx_isv_marcnv.tsv", index=False, sep='\t')
