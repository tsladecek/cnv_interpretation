import os

import pandas as pd

from scripts.config import settings
from scripts.helpers import datacheck


@datacheck
def classify_table(output: str, **kwargs):
    ccnv = []

    ccnv_path = os.path.join(settings.ROOT_DIR, 'tables', 'classifycnv')
    for f in os.listdir(ccnv_path):
        df = pd.read_csv(os.path.join(ccnv_path, f), sep='\t')
        df = df.rename(columns={'Chromosome': 'chrom', 'Start': 'start', 'End': 'end', 'Type': 'cnv_type'})
        df['dataset'] = f.split('_')[0]
        ccnv.append(df)
    ccnv = pd.concat(ccnv)
    ccnv.to_csv(output, sep='\t', compression='gzip', index=False)


if __name__ == '__main__':
    classify_table(output=settings.CLASSIFYCNV_TABLE)
