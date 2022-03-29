import os

import pandas as pd

from scripts.config import settings
from scripts.helpers import get_marcnv, datacheck, get_isv, get_classifycnv, acmg_severity, isv_severity


@datacheck
def main_table(output: str, **kwargs):
    marcnv = get_marcnv()
    isv_df = get_isv()
    classifycnv = get_classifycnv()
    metadata = pd.read_csv(os.path.join(settings.ROOT_DIR, 'data', 'metadata.tsv.gz'), sep='\t', compression='gzip')

    columns = ['chrom', 'start', 'end', 'cnv_type', 'dataset',
               'clinsig', 'clinsig_review', 'gold_stars',
               'benign_database', 'hi_all', 'loss_benign_cnvs_with_gains',
               'pop_freq', 'marcnv_score', 'marcnv_severity'] + \
              [f'marcnv_section{i}_option' for i in range(1, 6)] + \
              [f'marcnv_section{i}_score' for i in range(1, 6)] + \
              ["classifycnv_score", "classifycnv_severity"] + \
              [f'classifycnv_section{i}_option' for i in range(1, 6)] + \
              [f'classifycnv_section{i}_score' for i in range(1, 6)] + \
              ['isv_probability', 'isv_severity']

    final = {c: [] for c in columns}
    beds_path = os.path.join(settings.ROOT_DIR, 'data', 'beds')
    chromosomes = [f'chr{i}' for i in range(1, 23)] + ['chrX', 'chrY']

    cnvs_processed = 0

    for bed_fn in os.listdir(beds_path):
        bed = pd.read_csv(os.path.join(beds_path, bed_fn), sep='\t', header=None,
                          names=['chrom', 'start', 'end', 'cnv_type'])
        dataset, cnv_type = bed_fn.split('.')[0].split('_')
        cnv_type = ['DUP', 'DEL'][(cnv_type == 'loss') * 1]

        temp_marcnv = {
            'DUP': {c: marcnv.query(f'cnv_type == "DUP" & chrom == "{c}"') for c in chromosomes},
            'DEL': {c: marcnv.query(f'cnv_type == "DEL" & chrom == "{c}"') for c in chromosomes},
        }
        temp_isv = {
            'DUP': {c: isv_df.query(f'dataset == "{dataset}" & cnv_type == "DUP" & chrom == "{c}"') for c in
                    chromosomes},
            'DEL': {c: isv_df.query(f'dataset == "{dataset}" & cnv_type == "DEL" & chrom == "{c}"') for c in
                    chromosomes},
        }
        temp_classifycnv = {
            'DUP': {c: classifycnv.query(f'dataset == "{dataset}" & cnv_type == "DUP" & chrom == "{c}"') for c in
                    chromosomes},
            'DEL': {c: classifycnv.query(f'dataset == "{dataset}" & cnv_type == "DEL" & chrom == "{c}"') for c in
                    chromosomes},
        }

        temp_meta = {
            'DUP': {c: metadata.query(f'dataset == "{dataset}" & cnv_type == "DUP" & chrom == "{c}"') for c in
                    chromosomes},
            'DEL': {c: metadata.query(f'dataset == "{dataset}" & cnv_type == "DEL" & chrom == "{c}"') for c in
                    chromosomes},
        }

        for _, row in bed.iterrows():
            # ISV
            isv_row = temp_isv[cnv_type][row.chrom].query(f'start == {row.start} & end == {row.end}').squeeze()

            # ClassifyCNV
            classifycnv_row = temp_classifycnv[cnv_type][row.chrom].query(
                f'start == {row.start} & end == {row.end}').squeeze()

            # MarCNV
            marcnv_rows = temp_marcnv[cnv_type][row.chrom].query(f'start == {row.start} & end == {row.end}')

            # Metadata
            meta_row = temp_meta[cnv_type][row.chrom].query(f'start == {row.start} & end == {row.end}').squeeze()

            for _, mrow in marcnv_rows.iterrows():
                # COORDINATES
                final['chrom'].append(row.chrom)
                final['start'].append(row.start)
                final['end'].append(row.end)
                final['cnv_type'].append(cnv_type)
                final['dataset'].append(dataset)
                final['clinsig'].append(meta_row.clinsig)
                final['clinsig_review'].append(meta_row.clinsig_review)
                final['gold_stars'].append(meta_row.gold_stars)
                final['benign_database'].append(mrow.benign_database)
                final['hi_all'].append(mrow.hi_all)
                final['loss_benign_cnvs_with_gains'].append(mrow.loss_benign_cnvs_with_gains)
                final['pop_freq'].append(mrow.pop_freq)

                # MARCNV
                marcnv_score = 0
                for i in range(1, 6):
                    final[f'marcnv_section{i}_option'].append(mrow.loc[f'section{i}_option'])
                    final[f'marcnv_section{i}_score'].append(mrow.loc[f'section{i}_score'])
                    marcnv_score += mrow.loc[f'section{i}_score']

                final['marcnv_score'].append(marcnv_score)
                final['marcnv_severity'].append(acmg_severity(marcnv_score))

                # ISV
                final['isv_probability'].append(isv_row.ISV)
                final['isv_severity'].append(isv_severity(isv_row.ISV))

                # CLASSIFYCNV
                final[f'classifycnv_section1_option'].append('1A-B')
                final[f'classifycnv_section1_score'].append(classifycnv_row.loc['1A-B'])

                final[f'classifycnv_section3_option'].append('3')
                final[f'classifycnv_section3_score'].append(classifycnv_row.loc['3'])

                classifycnv_score = classifycnv_row.loc['1A-B'] + classifycnv_row.loc['3']
                for i in [2, 4, 5]:
                    cols = [c for c in classifycnv.columns if c.startswith(str(i))]
                    section = classifycnv_row.loc[cols]
                    not_zero = section.drop([c for c in cols if section.loc[c] == 0])
                    option = not_zero.keys()[0] if len(not_zero) > 0 else 'unknown'
                    score = not_zero.values[0] if len(not_zero) > 0 else 0
                    final[f'classifycnv_section{i}_option'].append(option)
                    final[f'classifycnv_section{i}_score'].append(score)
                    classifycnv_score += score

                final['classifycnv_score'].append(classifycnv_score)
                final['classifycnv_severity'].append(acmg_severity(classifycnv_score))

            cnvs_processed += 1
            if cnvs_processed % 1000 == 0:
                print('{:5d} cnvs processed'.format(cnvs_processed))

    final = pd.DataFrame(final)
    final.to_csv(output, sep='\t', compression='gzip', index=False)


if __name__ == '__main__':
    main_table(output=settings.MAIN_TABLE)
