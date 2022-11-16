import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from scripts.helpers import get_main, datacheck, save_fig


@datacheck
def marcnv_isv_split_distribution(output: str, **kwargs):
    df = get_main(final=True, evaluation=False)

    fig, ax = plt.subplots(2, 1, figsize=(7, 4))

    for c, cnv_type in enumerate(['DEL', 'DUP']):
        temp = df.query(f'cnv_type == "{cnv_type}"').reset_index(drop=True)
        temp = temp.loc[:, ["clinsig", "isv_probability", "marcnv_score"]]
        temp = pd.melt(temp,
                       id_vars=['clinsig'],
                       value_vars=['marcnv_score', 'isv_probability'],
                       var_name='method'
                       )

        sns.violinplot(x='clinsig',
                       y='value',
                       hue='method',
                       data=temp,
                       ax=ax[c],
                       order=['Benign', 'Likely benign', 'Uncertain significance', 'Likely pathogenic', 'Pathogenic'],
                       split=True)
        ax[c].set_title(cnv_type)
        ax[c].set_xlabel('')
        ax[c].set_ylabel('')
        ax[c].legend(loc='lower right')
    save_fig(output=output, fig=fig)
