import pandas as pd

from scripts.helpers import get_main, datacheck


@datacheck
def clinvar_vs_marcnv_vs_isv(output: str, **kwargs):
    df = get_main(final=True)

    acmg_labels = ['Benign', 'Likely benign', 'Uncertain significance',
                   'Likely pathogenic', 'Pathogenic']
    isv_labels = ['Benign', 'Uncertain significance', 'Pathogenic']

    res = {'cnv_type': [], 'clinvar': [], 'marcnv': [], 'isv': [], 'count': []}

    for cnv_type in ['DEL', 'DUP']:
        for clinvar in acmg_labels:
            for marcnv in acmg_labels:
                for isv in isv_labels:
                    temp = df.query(
                        f"cnv_type == '{cnv_type}' & clinsig == '{clinvar}' & marcnv_severity == '{marcnv}' & isv_severity == '{isv}'")
                    res['cnv_type'].append(cnv_type)
                    res['clinvar'].append(clinvar)
                    res['marcnv'].append(marcnv)
                    res['isv'].append(isv)
                    res['count'].append(len(temp))

    res = pd.DataFrame(res)
    res.to_csv(output, index=False, sep='\t')


@datacheck
def conflicting_predictions(output: str, **kwargs):
    df = get_main(final=True)

    conflicts = []
    conflicting_labels = {'Benign': 'Pathogenic',
                          'Pathogenic': 'Benign'}

    for label, conflicting in conflicting_labels.items():
        conflicts.append(
            df.query(f'clinsig == "{label}" & marcnv_severity == "{conflicting}" & isv_severity == "{conflicting}"'))

    conflicts = pd.concat(conflicts)
    conflicts.to_csv(output, index=False, sep='\t')
