import matplotlib.pyplot as plt

from scripts.config import settings
from scripts.helpers import get_main, save_fig, datacheck


@datacheck
def marcnv_vs_isv(output: str, **kwargs):
    df = get_main(final=True)

    LINE_WIDTH = 1
    LINE_ALPHA = 0.5
    LINE_LS = '--'

    fig, ax = plt.subplots(1, 2, figsize=(12, 7))

    for c, cnv_type in enumerate(['DEL', 'DUP']):
        for clinsig in ['Pathogenic', 'Benign']:
            temp = df.query(f'cnv_type == "{cnv_type}" & clinsig == "{clinsig}"')
            ax[c].plot(temp.isv_probability, temp.marcnv_score, '.', alpha=0.5,
                       c=settings.COLORS[clinsig])

            ax[c].axhline(0.99, ls=LINE_LS, c=settings.COLORS['Pathogenic'],
                          lw=LINE_WIDTH, alpha=LINE_ALPHA)
            ax[c].axhline(0.9, ls=LINE_LS, c=settings.COLORS['Likely pathogenic'],
                          lw=LINE_WIDTH, alpha=LINE_ALPHA)
            ax[c].axhline(-0.9, ls=LINE_LS, c=settings.COLORS['Likely benign'],
                          lw=LINE_WIDTH, alpha=LINE_ALPHA)
            ax[c].axhline(-0.99, ls=LINE_LS, c=settings.COLORS['Benign'],
                          lw=LINE_WIDTH, alpha=LINE_ALPHA)

            ax[c].axvline(0.05, ls=LINE_LS, c=settings.COLORS['Benign'],
                          lw=LINE_WIDTH, alpha=LINE_ALPHA)
            ax[c].axvline(0.95, ls=LINE_LS, c=settings.COLORS['Pathogenic'],
                          lw=LINE_WIDTH, alpha=LINE_ALPHA)

            ax[c].axhline(0, ls=LINE_LS, c=settings.COLORS['Uncertain significance'],
                          lw=LINE_WIDTH, alpha=LINE_ALPHA)
            ax[c].axvline(0.5, ls=LINE_LS, c=settings.COLORS['Uncertain significance'],
                          lw=LINE_WIDTH, alpha=LINE_ALPHA)

            ax[c].set_ylim(-3, 3)
            ax[c].set_xlim(-0.05, 1.05)
            ax[c].set_ylabel('MarCNV score')
            ax[c].set_xlabel('ISV probability')
        ax[c].set_title(cnv_type)

    save_fig(output=output, fig=fig)
