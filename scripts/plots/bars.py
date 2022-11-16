import matplotlib.pyplot as plt
import numpy as np

from scripts.config import settings
from scripts.helpers import get_main, bar_update, barchart, acmg_severity, save_fig, datacheck


@datacheck
def bars_database_comparison(output: str, **kwargs):
    df = get_main()

    fig, ax = plt.subplots(2, 1, figsize=(7, 4))

    for c, cnv_type in enumerate(['DEL', 'DUP']):
        res = []
        temp = df.query(f'cnv_type == "{cnv_type}"')

        for db in ['DGV-GS-OUTER', 'DGV-GS-INNER', 'DGV-ALL']:
            marcnv = temp.query(f'benign_database == "{db}" & hi_all == 0 & loss_benign_cnvs_with_gains == 0') \
                         .loc[:, ['chrom', 'start', 'end', 'cnv_type', 'marcnv_severity', 'clinsig']]
            bar_update(results=res, y=marcnv.clinsig, yh=marcnv.marcnv_severity, method=f'{db}')
        barchart(res, ax=ax[c])
        ax[c].set_ylabel('')
        ax[c].set_title(cnv_type)
    ax[1].set_xlabel('Number of CNVs')
    # fig.suptitle('MarCNV Comparison of Databases of Benign CNVs for section 2 evaluation')
    save_fig(output=output, fig=fig)


@datacheck
def bars_marcnv_options(output: str, **kwargs):
    df = get_main()
    fig, ax = plt.subplots(2, 1, figsize=(7, 4), gridspec_kw={'height_ratios': [1, 1]})

    for c, cnv_type in enumerate(['DEL', 'DUP']):
        res = []
        temp = df.query(f'cnv_type == "{cnv_type}"')

        if cnv_type == 'DUP':
            for hi in [0, 1]:
                marcnv = temp.query(
                    f'benign_database == "{settings.MARCNV_BENIGN_DATABASE}" & hi_all == {hi} & loss_benign_cnvs_with_gains == 0').loc[
                         :, ['chrom', 'start', 'end', 'cnv_type', 'marcnv_severity', 'clinsig']]
                bar_update(results=res, y=marcnv.clinsig, yh=marcnv.marcnv_severity, method=f'HI (1, 2, 3): {hi}')
        else:
            for hi in [0, 1]:
                # for lb in [0, 1]:
                marcnv = temp.query(
                    f'benign_database == "{settings.MARCNV_BENIGN_DATABASE}" & hi_all == {hi} & loss_benign_cnvs_with_gains == 0').loc[
                         :, ['chrom', 'start', 'end', 'cnv_type', 'marcnv_severity', 'clinsig']]
                bar_update(results=res, y=marcnv.clinsig, yh=marcnv.marcnv_severity,
                           method=f'HI (1, 2, 3): {hi}')
                # method=f'HI (1, 2, 3): {hi}\nOnly Loss CNVs: {lb}')

        barchart(res, ax=ax[c])
        ax[c].set_ylabel('')
        ax[c].set_title(cnv_type)
    # fig.suptitle('MarCNV Comparison of Options for HI/TS genes and choice of Benign CNVs')
    ax[1].set_xlabel('Number of CNVs')
    save_fig(output=output, fig=fig)


@datacheck
def bars_method_comparison(output: str, **kwargs):
    df = get_main()
    LIKELY_IS_UNCERTAIN = True
    fig, ax = plt.subplots(2, 1, figsize=(7, 4))

    for c, cnv_type in enumerate(['DEL', 'DUP']):
        res = []
        temp = df.query(f'cnv_type == "{cnv_type}"')

        # CLASSIFYCNV
        ccnv = temp.loc[:, ['chrom', 'start', 'end', 'cnv_type', 'classifycnv_severity', 'clinsig']].drop_duplicates()
        bar_update(results=res, y=ccnv.clinsig, yh=ccnv.classifycnv_severity, method=f'ClassifyCNV',
                   likely_is_uncertain=LIKELY_IS_UNCERTAIN)

        # MARCNV
        marcnv = temp.query(
            f'benign_database == "{settings.MARCNV_BENIGN_DATABASE}" & hi_all == {settings.MARCNV_HI} & loss_benign_cnvs_with_gains == {settings.MARCNV_LB}').loc[
                 :, ['chrom', 'start', 'end', 'cnv_type', 'marcnv_severity', 'marcnv_score', 'clinsig']]
        bar_update(results=res, y=marcnv.clinsig, yh=marcnv.marcnv_severity, method=f'MarCNV',
                   likely_is_uncertain=LIKELY_IS_UNCERTAIN)

        # ISV
        isv_df = temp.loc[:,
                 ['chrom', 'start', 'end', 'cnv_type', 'isv_severity', 'isv_probability', 'clinsig']].drop_duplicates()
        bar_update(results=res, y=isv_df.clinsig, yh=isv_df.isv_severity, method=f'ISV')

        # MARCNV + ISV
        yh = marcnv.marcnv_score.values + isv_df.isv_probability.values - 0.5
        yh = np.array([acmg_severity(s) for s in yh])
        bar_update(results=res, y=isv_df.clinsig.values, yh=yh, method='MarCNV + ISV',
                   likely_is_uncertain=LIKELY_IS_UNCERTAIN)

        barchart(res, ax=ax[c])
        ax[c].set_ylabel('')
        ax[c].set_title(cnv_type)
    # fig.suptitle('Method Comparison')
    ax[1].set_xlabel('Number of CNVs')
    save_fig(output=output, fig=fig)


@datacheck
def bars_method_comparison_together(output: str, **kwargs):
    df = get_main()
    LIKELY_IS_UNCERTAIN = True
    fig, ax = plt.subplots(1, 1, figsize=(7, 4))

    res = []

    # CLASSIFYCNV
    ccnv = df.loc[:, ['chrom', 'start', 'end', 'cnv_type', 'classifycnv_severity', 'clinsig']].drop_duplicates()
    bar_update(results=res, y=ccnv.clinsig, yh=ccnv.classifycnv_severity, method=f'ClassifyCNV',
               likely_is_uncertain=LIKELY_IS_UNCERTAIN)

    # MARCNV
    marcnv = df.query(
        f'benign_database == "{settings.MARCNV_BENIGN_DATABASE}" & hi_all == {settings.MARCNV_HI} & loss_benign_cnvs_with_gains == {settings.MARCNV_LB}').loc[
             :, ['chrom', 'start', 'end', 'cnv_type', 'marcnv_severity', 'marcnv_score', 'clinsig']]
    bar_update(results=res, y=marcnv.clinsig, yh=marcnv.marcnv_severity, method=f'MarCNV',
               likely_is_uncertain=LIKELY_IS_UNCERTAIN)

    # ISV
    isv_df = df.loc[:,
             ['chrom', 'start', 'end', 'cnv_type', 'isv_severity', 'isv_probability', 'clinsig']].drop_duplicates()
    bar_update(results=res, y=isv_df.clinsig, yh=isv_df.isv_severity, method=f'ISV')

    # MARCNV + ISV
    yh = marcnv.marcnv_score.values + isv_df.isv_probability.values - 0.5
    yh = np.array([acmg_severity(s) for s in yh])
    bar_update(results=res, y=isv_df.clinsig.values, yh=yh, method='MarCNV + ISV',
               likely_is_uncertain=LIKELY_IS_UNCERTAIN)

    barchart(res, ax=ax)
    ax.set_ylabel('')
    # fig.suptitle('Method Comparison')
    ax.set_xlabel('Number of CNVs')
    save_fig(output=output, fig=fig)
