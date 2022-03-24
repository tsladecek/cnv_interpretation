import os

import pandas as pd
from isv import isv

from scripts.config import settings
from scripts.helpers import datacheck


@datacheck
def isv_table(output: str, **kwargs):
    isv_df = []

    beds_path = os.path.join(settings.ROOT_DIR, 'data', 'beds')
    for bed in os.listdir(beds_path):
        bed_df = pd.read_csv(os.path.join(beds_path, bed), sep='\t', header=None)
        bed_df.columns = ['chrom', 'start', 'end', 'cnv_type']
        bed_isv = isv(cnvs=bed_df, proba=True, shap=False)
        bed_isv['dataset'] = bed.split('_')[0]
        isv_df.append(bed_isv)

    isv_df = pd.concat(isv_df)

    isv_df.to_csv(output, sep='\t', compression='gzip', index=False)


if __name__ == '__main__':
    isv_table(output=settings.ISV_TABLE)
