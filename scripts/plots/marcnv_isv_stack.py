import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from scripts.config import settings
from scripts.helpers import Metrics, get_main, save_fig, datacheck


@datacheck
def marcnv_isv_stack(output: str, **kwargs):
    df = get_main(final=True)

    ALPHA = 0.7

    fig, ax = plt.subplots(2, 2, figsize=(7, 4), sharey=True, sharex=True)
    pal = [settings.COLORS['TP'], settings.COLORS['TN'], settings.COLORS['Uncertain'], settings.COLORS['FP'],
           settings.COLORS['FN']]

    for c, cnv_type in enumerate(['DEL', 'DUP']):
        temp = df.query(f'cnv_type == "{cnv_type}"')
        results = []
        for r in np.linspace(0, 3, 301):
            m = Metrics(y=temp.clinsig,
                        isv_raw=temp.isv_probability,
                        marcnv=temp.marcnv_score,
                        isv_ratio=r)

            results.append([r, m.included, m.TP, m.FP, m.TN, m.FN,
                            m.accuracy, m.sensitivity, m.specificity, m.mcc,
                            (m.TP + m.TN) / m.n, (m.FP + m.FN) / m.n])

        res = pd.DataFrame(results, columns=["isv_ratio", "included", "TP", "FP", "TN", "FN",
                                             "accuracy", "sensitivity", "specificity", "mcc",
                                             "true", "false"])

        stacks = ax[c, 0].stackplot(res.isv_ratio,
                                    res.TP / m.n,
                                    res.TN / m.n,
                                    1 - res.included,
                                    res.FP / m.n,
                                    res.FN / m.n,
                                    labels=["TP", "TN", "Uncertain", "FP", "FN"],
                                    baseline='zero',
                                    # hatch='...'
                                    )

        for i, stack in enumerate(stacks):
            stack.set_color(pal[i])
            stack.set_edgecolor(pal[i])

        for i, col in enumerate([res.TP / m.n, res.TN / m.n, 1 - res.included, res.FP / m.n, res.FN / m.n]):
            ax[c, 1].plot(res.isv_ratio, col, color=pal[i], lw=5, alpha=ALPHA)

    ax[0, 0].set_ylabel('DEL')
    ax[1, 0].set_ylabel('DUP')

    ax[1, 0].set_xlabel('ISV ratio')
    ax[1, 1].set_xlabel('ISV ratio')

    # for tick in ax[0, 0].yaxis.get_major_ticks() + ax[1, 0].yaxis.get_major_ticks() + ax[1, 0].xaxis.get_major_ticks() + \
    #             ax[1, 1].xaxis.get_major_ticks():

    ax[0, 0].set_xlim(0, 3)
    ax[0, 0].set_ylim(0, 1)

    legend_elements = [
        Line2D([0], [0], color=pal[0], lw=4, label='TP', ),
        Line2D([0], [0], color=pal[1], lw=4, label='TN'),
        Line2D([0], [0], color=pal[2], lw=4, label='Uncertain'),
        Line2D([0], [0], color=pal[3], lw=4, label='FP'),
        Line2D([0], [0], color=pal[4], lw=4, label='FN')
    ]

    ax[0, 1].legend(handles=legend_elements, loc='upper right')
    fig.tight_layout()

    save_fig(output=output, fig=fig)
