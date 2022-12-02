import pandas as pd


# vypocitat pocty p, lp, vus, lb, b
# dat do formatu pre sankey diagram

columns_ci = ['Pathogenic', 'Likely pathogenic', 'VUS', 'Likely benign', 'Benign']
cnvs_zjednotene_interpretacie = pd.read_csv("./cnv_interpretation/data/evaluation_data/cnvs_isv_marcnv_zjednotene_mdx_final.tsv", sep='\t')


columns_other_ci = ['marcnv_label', 'isv_label', 'marcnv_isv_1_label', 'marcnv_isv_1.99_label', 'marcnv_isv_0.19_label']

# ukladaj vystup (pocty) do suboru pre sankey format
with open("./cnv_interpretation/data/evaluation_data/counts_mdx_other_compare/mdx_vs_other_sankey.txt", "a") as sankey_file:

    # prechadzat a porovnavat mdx s marcnv, isv, marcnv+isv, ...
    for column_other_ci in columns_other_ci:
        # vytvorit tabulku, riadky a stlpce budu ako columns_ci, na zaciatku vyplnene nulami
        mdx_other = pd.DataFrame(0, columns=columns_ci, index=columns_ci)

        # prechadzat suborom klinickych interpretacii
        for i, row in cnvs_zjednotene_interpretacie.iterrows():
            mdx_ci = row['Clinical Interpretation']
            other_ci = row[column_other_ci]

            # pri kazdom riadku pripocitat do tabulky mdx_other, na poziciu [mdx][other]
            mdx_other[other_ci][mdx_ci] = mdx_other[other_ci][mdx_ci] + 1

        print('\n' + column_other_ci)
        print(mdx_other)
        path_to_save = './cnv_interpretation/data/evaluation_data/counts_mdx_other_compare/mdx_vs_' + column_other_ci + '.tsv'
        mdx_other.to_csv(path_to_save, sep='\t')

        # zapis do suboru o ake porovnanie sa jedna
        sankey_file.write('\n' + 'mdx vs ' + column_other_ci + '\n')
        # prechadzaj tabulku poctov a vypis v sankey formate iba tie ktore sa maju zobrazit (> 0)
        for mdx_ci in columns_ci:
            for col_other_ci in columns_ci:
                if mdx_other[mdx_ci][col_other_ci] > 0:
                    sankey_str = col_other_ci + ' CI  [' + str(mdx_other[mdx_ci][col_other_ci]) + ']  ' + mdx_ci
                    print(sankey_str)
                    sankey_file.write(sankey_str + '\n')



# marcnv vs combined
marcnv_combined = pd.DataFrame(0, columns=columns_ci, index=columns_ci)

# prechadzat suborom klinickych interpretacii
for i, row in cnvs_zjednotene_interpretacie.iterrows():
    marcnv_label = row['marcnv_label']
    combined_label = row['marcnv_isv_1_label']

    # pri kazdom riadku pripocitat do tabulky mdx_other, na poziciu [mdx][other]
    marcnv_combined[combined_label][marcnv_label] = marcnv_combined[combined_label][marcnv_label] + 1

print(marcnv_combined)
path_to_save = './cnv_interpretation/data/evaluation_data/counts_mdx_other_compare/marcnv_vs_combined.tsv'
marcnv_combined.to_csv(path_to_save, sep='\t')

with open("./cnv_interpretation/data/evaluation_data/counts_mdx_other_compare/mdx_vs_other_sankey.txt",
          "a") as sankey_file:
    # zapis do suboru o ake porovnanie sa jedna
    sankey_file.write('\n marcnv vs combined \n')
    # prechadzaj tabulku poctov a vypis v sankey formate iba tie ktore sa maju zobrazit (> 0)
    for marcnv_label in columns_ci:
        for combined_label in columns_ci:
            if marcnv_combined[marcnv_label][combined_label] > 0:
                sankey_str = combined_label + ' MarCNV  [' + str(marcnv_combined[marcnv_label][combined_label]) + ']  ' \
                             + marcnv_label + ' combined'
                print(sankey_str)
                sankey_file.write(sankey_str + '\n')


# isv vs combined
isv_combined = pd.DataFrame(0, columns=columns_ci, index=columns_ci)
# prechadzat suborom klinickych interpretacii
for i, row in cnvs_zjednotene_interpretacie.iterrows():
    isv_label = row['isv_label']
    combined_label = row['marcnv_isv_1_label']

    # pri kazdom riadku pripocitat do tabulky mdx_other, na poziciu [mdx][other]
    isv_combined[combined_label][isv_label] = isv_combined[combined_label][isv_label] + 1

print(isv_combined)
path_to_save = './cnv_interpretation/data/evaluation_data/counts_mdx_other_compare/isv_vs_combined.tsv'
isv_combined.to_csv(path_to_save, sep='\t')

with open("./cnv_interpretation/data/evaluation_data/counts_mdx_other_compare/mdx_vs_other_sankey.txt",
          "a") as sankey_file:
    # zapis do suboru o ake porovnanie sa jedna
    sankey_file.write('\n isv vs combined \n')
    # prechadzaj tabulku poctov a vypis v sankey formate iba tie ktore sa maju zobrazit (> 0)
    for isv_label in columns_ci:
        for combined_label in columns_ci:
            if isv_combined[isv_label][combined_label] > 0:
                sankey_str = combined_label + ' ISV  [' + str(isv_combined[isv_label][combined_label]) + ']  ' \
                             + isv_label + ' combined'
                print(sankey_str)
                sankey_file.write(sankey_str + '\n')


# MarCNV vs ISV
marcnv_isv = pd.DataFrame(0, columns=columns_ci, index=columns_ci)
for i, row in cnvs_zjednotene_interpretacie.iterrows():
    isv_label = row['isv_label']
    marcnv_label = row['marcnv_label']

    # pri kazdom riadku pripocitat do tabulky mdx_other, na poziciu [mdx][other]
    marcnv_isv[isv_label][marcnv_label] = marcnv_isv[isv_label][marcnv_label] + 1

print(marcnv_isv)
path_to_save = './cnv_interpretation/data/evaluation_data/counts_mdx_other_compare/marcnv_vs_isv.tsv'
marcnv_isv.to_csv(path_to_save, sep='\t')

with open("./cnv_interpretation/data/evaluation_data/counts_mdx_other_compare/mdx_vs_other_sankey.txt",
          "a") as sankey_file:
    # zapis do suboru o ake porovnanie sa jedna
    sankey_file.write('\nMarCNV vs ISV\n')
    # prechadzaj tabulku poctov a vypis v sankey formate iba tie ktore sa maju zobrazit (> 0)
    for marcnv_label in columns_ci:
        for isv_label in columns_ci:
            if marcnv_isv[marcnv_label][isv_label] > 0:
                sankey_str = isv_label + ' MarCNV  [' + str(marcnv_isv[marcnv_label][isv_label]) + ']  ' \
                             + marcnv_label + ' ISV'
                print(sankey_str)
                sankey_file.write(sankey_str + '\n')
