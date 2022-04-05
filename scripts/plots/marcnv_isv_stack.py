import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.config import settings
from scripts.helpers import Metrics, get_main, save_fig


def marcnv_isv_stack(output: str, **kwargs):
    df = get_main()

    fig, ax = plt.subplots(2, 2, figsize=(20, 12), sharey=True, sharex=True)

    for c, cnv_type in enumerate(['DEL', 'DUP']):
        temp = df.query(f'cnv_type == "{cnv_type}"')
        results = []
        for r in np.linspace(0, 3, 21):
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
        pal = [settings.COLORS[clinsig] for clinsig in ['Benign', 'Likely benign',
                                                        'Uncertain significance',
                                                        'Likely pathogenic', 'Pathogenic']]

        ax[c, 0].stackplot(res.isv_ratio,
                           res.TP / m.n,
                           res.TN / m.n,
                           1 - res.included,
                           res.FP / m.n,
                           res.FN / m.n,
                           labels=["TP", "TN", "Uncertain", "FP", "FN"],
                           colors=pal)

        for i, col in enumerate([res.TP / m.n, res.TN / m.n, 1 - res.included, res.FP / m.n, res.FN / m.n]):
            ax[c, 1].plot(res.isv_ratio, col, color=pal[i], lw=5)

    ax[0, 0].set_ylabel('DEL\nISV probability')
    ax[1, 0].set_ylabel('DUP\nISV probability')

    ax[1, 0].set_xlabel('ISV ratio')
    ax[1, 1].set_xlabel('ISV ratio')

    save_fig(output=output, fig=fig)
