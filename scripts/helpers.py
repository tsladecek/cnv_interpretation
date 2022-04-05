import os
import subprocess

import numpy as np
import pandas as pd
import requests as requests
from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix, matthews_corrcoef

from scripts.config import settings


def get_marcnv():
    return pd.read_csv(settings.MARCNV_TABLE, sep='\t', compression='gzip')


def get_isv():
    return pd.read_csv(settings.ISV_TABLE, sep='\t', compression='gzip')


def get_classifycnv():
    return pd.read_csv(settings.CLASSIFYCNV_TABLE, sep='\t', compression='gzip')


def get_main(evaluation=True, final=False):
    df = pd.read_csv(settings.MAIN_TABLE, sep='\t', compression='gzip')
    if evaluation:
        df = df.query(' | '.join([f'dataset == "{d}"' for d in settings.EVALUATION_DATASETS]))

    if final:
        df = df.query(
            f'benign_database == "{settings.MARCNV_BENIGN_DATABASE}" & hi_all == {settings.MARCNV_HI} & loss_benign_cnvs_with_gains == {settings.MARCNV_LB}')
    df = df.reset_index(drop=True)
    return df


def install_classifycnv():
    if os.path.exists(os.path.join(settings.ROOT_DIR, settings.CLASSIFYCNV_DIR_NAME)):
        print('ClassifyCNV already installed. If you wish to download and reinstall it, '
              f'remove the {settings.CLASSIFYCNV_DIR_NAME}/ directory')
        return
    else:
        # Download
        print('Downloading ClassifyCNV')
        url = 'https://github.com/Genotek/ClassifyCNV/archive/refs/tags/v1.1.1.tar.gz'
        r = requests.get(url, allow_redirects=True)
        with open(os.path.join(settings.ROOT_DIR, settings.CLASSIFYCNV_DIR_NAME + '.tar.gz'), 'wb') as f:
            f.write(r.content)

        # Extract
        print('Extracting ClassifyCNV')
        subprocess.run(['tar', 'xzf', os.path.join(settings.ROOT_DIR, settings.CLASSIFYCNV_DIR_NAME + '.tar.gz')])

        # Install requirements
        print('Installing ClassifyCNV requirements')
        os.chdir(os.path.join(settings.ROOT_DIR, settings.CLASSIFYCNV_DIR_NAME))
        subprocess.run(['sh', 'update_clingen.sh'])

        os.chdir(os.path.join(settings.ROOT_DIR))


def datacheck(func):
    def check_data_wrapper(*args, **kwargs):
        output = kwargs['output']
        force_recreate = True if 'force_recreate' in kwargs and kwargs['force_recreate'] else False
        if force_recreate:
            return func(*args, **kwargs)
        elif os.path.exists(output):
            while True:
                recreate = input(f'Recreate {output}? ([No] - default, Yes): ') or 'No'
                recreate = recreate.lower()
                if recreate in ['yes', 'no']:
                    break
            if recreate == 'yes':
                return func(*args, **kwargs)
            else:
                return
        else:
            return func(*args, **kwargs)

    return check_data_wrapper


def acmg_severity(score: float):
    """https://www.nature.com/articles/s41436-019-0686-8"""

    if score >= 0.99:
        return 'Pathogenic'
    elif score >= 0.9:
        return 'Likely pathogenic'
    elif score >= -0.89:
        return 'Uncertain significance'
    elif score > -0.99:
        return 'Likely benign'
    else:
        return 'Benign'


def isv_severity(probability: float, threshold: float = 0.95):
    if probability >= threshold:
        return 'Pathogenic'
    elif probability <= 1 - threshold:
        return 'Benign'
    return 'Uncertain significance'


def bar_update(results, y, yh, method, likely_is_uncertain=True):
    if likely_is_uncertain:
        yh = np.where(yh == "Likely pathogenic", "Uncertain significance", yh)
        yh = np.where(yh == "Likely benign", "Uncertain significance", yh)

    else:
        yh = np.where(yh == "Likely pathogenic", "Pathogenic", yh)
        yh = np.where(yh == "Likely benign", "Benign", yh)

    correct = np.sum(yh == y)
    uncertain = np.sum(yh == "Uncertain significance")
    incorrect = np.sum(yh != y) - uncertain

    print(np.unique(yh))
    print(f"{method}\t{correct}\t{incorrect}\t{uncertain}")

    accuracy = correct / (correct + incorrect)
    included = (correct + incorrect) / (correct + incorrect + uncertain)

    label = '{}\nAccuracy: {:2.2f} %\nIncluded: {:2.2f} %' \
        .format(method, 100 * accuracy, 100 * included)
    results.append([label, correct, uncertain, incorrect])


def barchart(results, ax, stacked=True):
    results = pd.DataFrame(results, columns=["label", "Correct", "Uncertain", "Incorrect"])

    if stacked:
        results.iloc[::-1].set_index('label').plot(kind='barh', stacked=True,
                                                   ax=ax, width=0.8,
                                                   color=["#009900", "#C0C0C0", "#FF0000"])


def save_fig(output: str, fig):
    fig.tight_layout()
    plt.savefig(output, dpi=settings.DPI)


class Metrics:
    def __init__(self, y, y_hat=None, isv_raw=None, marcnv=None, isv_ratio=1, likely_is_uncertain=True):

        if y_hat is None:
            isv = (isv_raw - 0.5) * isv_ratio
            y_hat = marcnv + isv

        y_hat_acmg = [acmg_severity(score) for score in y_hat]

        temp = pd.DataFrame({"y": y, "marcnv_isv": y_hat_acmg})

        if likely_is_uncertain:
            temp = temp.replace({"Likely pathogenic": "Uncertain significance",
                                 "Likely benign": "Uncertain significance"})
        else:
            temp = temp.replace({"Likely pathogenic": "Pathogenic",
                                 "Likely benign": "Benign"})

        temp = temp.query("marcnv_isv != 'Uncertain significance'")
        temp = temp.replace({"Pathogenic": 1, "Benign": 0})

        y = temp.y.values
        y_hat = temp.marcnv_isv.values

        self.y = y
        self.y_hat = y_hat

        self.n = len(y_hat_acmg)
        self.included = len(temp) / len(y_hat_acmg)

        TN, FP, FN, TP = confusion_matrix(y, y_hat).ravel()
        self.TN, self.FP, self.FN, self.TP = TN, FP, FN, TP

        self.accuracy = np.mean(y == y_hat)
        self.sensitivity = TP / (TP + FN)
        self.specificity = TN / (TN + FP)
        self.mcc = matthews_corrcoef(y, y_hat)
