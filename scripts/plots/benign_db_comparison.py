import os

import matplotlib.pyplot as plt
import pandas as pd

from scripts.config import settings
from scripts.helpers import datacheck, bar_update, barchart, save_fig


@datacheck
def benign_db_comparison(output: str, **kwargs):
    ben_db = pd.read_csv(os.path.join(settings.ROOT_DIR, 'data', 'benign_cnv_database_comparison.tsv.gz'), sep='\t',
                         compression='gzip')
    ben_db = ben_db.query('data != "test"')
    y = ben_db.clinsig.values
    LIKELY_IS_UNCERTAIN = True

    fig, ax = plt.subplots(4, 2, figsize=(7, 9))

    for i, cnv_types in enumerate(["losses", "gainslosses"]):
        for j, bd in enumerate(["dgv", "dgv_gold_inner", "dgv_gold_outer", "gnomad"]):
            res = []
            # bar_update(res, y, ben_db.marcnv.values, f"MarCNV", likely_is_uncertain=LIKELY_IS_UNCERTAIN)

            for frequency in [0, 0.01, 0.1, 0.5, 1, 2, 10]:
                yh = ben_db.loc[:, f"{bd}_{cnv_types}_{frequency}"].values
                bar_update(res, y, yh, f"MAF: {frequency} %", likely_is_uncertain=LIKELY_IS_UNCERTAIN)

            show_legend = False
            if i == 1 and j == 3:
                show_legend = True

            barchart(res, ax=ax[j, i], show_legend=show_legend)
            ax[j, i].set_title(bd.upper())


    ax[0, 0].set_title(f"LOSSES\nDGV")
    ax[0, 1].set_title(f"GAINS & LOSSES\nDGV")
    ax[3, 0].set_xlabel('Number of CNVs')
    ax[3, 1].set_xlabel('Number of CNVs')

    plt.tight_layout()

    save_fig(output=output, fig=fig)
