import pandas as pd


def get_clinvar_label(row):
    if row.clinsig == 1 or row.clinsig == '1':
        return 'Pathogenic'
    elif row.clinsig == 0 or row.clinsig == '0':
        return 'Benign'
    else:
        return row.clinsig


def get_combined_score(row):
    return row.marcnv_score + (row.ISV_probability - 0.5)


def get_combined_label(row, col_name):
    score = row[col_name]
    if score >= 0.99:
        return 'Pathogenic'
    elif score >= 0.9:
        return 'Likely pathogenic'
    elif score >= -0.89:
        return 'Uncertain significance'
    elif score > -0.99:
        return 'Likely benign'
    else:
        return 'Benign'


gain = pd.read_csv('./cnv_interpretation/data/evaluation_data/clinvar_summary_gain.tsv', sep='\t', low_memory=False)
loss = pd.read_csv('./cnv_interpretation/data/evaluation_data/clinvar_summary_loss.tsv', sep='\t', low_memory=False)

cnvs = loss.append(gain)
cnvs = cnvs[cnvs.data == 'train']
# cnvs = cnvs[['cnv_type', 'clinsig', 'marcnv_severity', 'marcnv_score', 'ISV_probability', 'data']]

# z clinsig (clinvar na pathp/benign)
cnvs['clinvar_label'] = cnvs.apply(lambda row: get_clinvar_label(row), axis=1)

# vytvor combined score
cnvs['combined_score'] = cnvs.apply(lambda row: get_combined_score(row), axis=1)

# z combined na labe
cnvs['combined_label'] = cnvs.apply(lambda row: get_combined_label(row, col_name='combined_score'), axis=1)


columns_ci = ['Pathogenic', 'Likely pathogenic', 'Uncertain significance', 'Likely benign', 'Benign']

clinvar_vs_combined = pd.DataFrame(0, columns=columns_ci, index=columns_ci)
for i, row in cnvs.iterrows():
    combined_label = row['combined_label']
    clinvar_label = row['clinvar_label']

    # pri kazdom riadku pripocitat do tabulky mdx_other, na poziciu [mdx][other]
    clinvar_vs_combined[combined_label][clinvar_label] = clinvar_vs_combined[combined_label][clinvar_label] + 1

print(clinvar_vs_combined)
path_to_save = './cnv_interpretation/data/evaluation_data/clinvar_combined_compare_counts_train.tsv'
clinvar_vs_combined.to_csv(path_to_save, sep='\t')

with open("./cnv_interpretation/data/evaluation_data/counts_mdx_other_compare/mdx_vs_other_sankey.txt",
          "a") as sankey_file:
    # zapis do suboru o ake porovnanie sa jedna
    sankey_file.write('\nClinVar vs Combined TRAIN \n')
    # prechadzaj tabulku poctov a vypis v sankey formate iba tie ktore sa maju zobrazit (> 0)
    for clinvar_label in columns_ci:
        for combined_label in columns_ci:
            if clinvar_vs_combined[clinvar_label][combined_label] > 0:
                sankey_str = combined_label + ' ClinVar  [' + str(clinvar_vs_combined[clinvar_label][combined_label]) + ']  ' \
                             + clinvar_label + ' Combined'
                print(sankey_str)
                sankey_file.write(sankey_str + '\n')


cnvs.groupby(['clinvar_label', 'combined_label'])['cnv_type'].count()


counts_clinvar_combined = pd.read_csv('./cnv_interpretation/data/evaluation_data/clinvar_combined_test_counts.csv', sep='\t')

with open("./cnv_interpretation/data/evaluation_data/counts_mdx_other_compare/mdx_vs_other_sankey.txt",
          "a") as sankey_file:
    # zapis do suboru o ake porovnanie sa jedna
    sankey_file.write('\nClinVar vs Combined TEST \n')
    for i, row in counts_clinvar_combined.iterrows():
        sankey_str = row.ClinVar + ' ClinVar  [' + str(row.Count) + ']  ' + row.Combined + ' Combined'
        print(sankey_str)
        sankey_file.write(sankey_str + '\n')
