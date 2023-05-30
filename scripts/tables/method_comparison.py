##
import json

import numpy as np
import pandas as pd
from scipy import stats

from scripts.helpers import get_main, acmg_severity, datacheck

@datacheck
def method_comparison(output: str, **kwargs):
    df = get_main(final=True)

    # Get scores
    isv_score = df.isv_probability.values
    marcnv_score = df.marcnv_score.values
    ccnv_score = df.classifycnv_score.values
    ccnv_isv_score = ccnv_score + isv_score - 0.5
    marcnv_isv_score = marcnv_score + isv_score - 0.5

    # Translate scores to ACMG severities
    clinsig = df.clinsig.values
    severities = {
        'isv': df.isv_severity.values,
        'marcnv': np.array([acmg_severity(i) for i in marcnv_score]),
        'classifycnv': np.array([acmg_severity(i) for i in ccnv_score]),
        'classifycnv_isv': np.array([acmg_severity(i) for i in ccnv_isv_score]),
        'marcnv_isv': np.array([acmg_severity(i) for i in marcnv_isv_score])
    }

    # Calculate metrics
    metrics = {}
    for method, y in severities.items():
        # Replace "Likely benign" and "Likely pathogenic" with "Uncertain significance"
        y = np.where(y == 'Likely pathogenic', 'Uncertain significance', y)
        y = np.where(y == 'Likely benign', 'Uncertain significance', y)

        true_pathogenic = np.sum(y[np.where(clinsig == 'Pathogenic')[0]] == 'Pathogenic')
        true_benign = np.sum(y[np.where(clinsig == 'Benign')[0]] == 'Benign')

        unambiguous_clinsig = np.array(clinsig[np.where(y != 'Uncertain significance')[0]])
        unambiguous_y = np.array(y[np.where(y != 'Uncertain significance')[0]])

        metrics[method] = {
            'true_pathogenic': true_pathogenic,
            'false_pathogenic': np.sum(y[np.where(clinsig == 'Benign')[0]] == 'Pathogenic'),
            'true_benign': true_benign,
            'false_benign': np.sum(y[np.where(clinsig == 'Pathogenic')[0]] == 'Benign'),
            'discovered_pathogenic': 100 * true_pathogenic / np.sum(clinsig == 'Pathogenic'),
            'discovered_benign': 100 * true_benign / np.sum(clinsig == 'Benign'),
            'sensitivity': 100 * np.mean(unambiguous_y[np.where(unambiguous_clinsig == 'Pathogenic')] == 'Pathogenic'),
            'specificity': 100 * np.mean(unambiguous_y[np.where(unambiguous_clinsig == 'Benign')] == 'Benign'),
        }

    # Create dataframe and save it
    metrics_df = {
        'method': []
    }
    for method, method_metrics in metrics.items():
        metrics_df['method'].append(method)

        for m in method_metrics:
            if m not in metrics_df:
                metrics_df[m] = []

            metrics_df[m].append(method_metrics[m])

    metrics_df = pd.DataFrame(metrics_df)
    metrics_df.to_csv(output, sep='\t', index=False)


@datacheck
def mcnemar_bowker(output, **kwargs):
    df = get_main(final=True)

    # df = (k(k - 1) / 2) -> k = 3
    degrees_of_freedom = 3

    results = {'DEL': {}, 'DUP': {}}

    for cnv_type in ['DEL', 'DUP']:
        temp = df.query(f'cnv_type == "{cnv_type}"')
        # Get scores
        isv_score = temp.isv_probability.values
        marcnv_score = temp.marcnv_score.values
        ccnv_score = temp.classifycnv_score.values
        ccnv_isv_score = ccnv_score + isv_score - 0.5
        marcnv_isv_score = marcnv_score + isv_score - 0.5

        severities = {
            'isv': temp.isv_severity.values,
            'classifycnv': np.array([acmg_severity(i) for i in ccnv_score]),
            'marcnv': np.array([acmg_severity(i) for i in marcnv_score]),
            'classifycnv_isv': np.array([acmg_severity(i) for i in ccnv_isv_score]),
            'marcnv_isv': np.array([acmg_severity(i) for i in marcnv_isv_score])
        }

        for mi1 in range(len(severities) - 1):
            for mi2 in range(mi1 + 1, len(severities)):
                method1 = list(severities.keys())[mi1]
                method2 = list(severities.keys())[mi2]

                m1 = severities[method1]
                # Replace "Likely benign" and "Likely pathogenic" with "Uncertain significance"
                m1 = np.where(m1 == 'Likely pathogenic', 'Uncertain significance', m1)
                m1 = np.where(m1 == 'Likely benign', 'Uncertain significance', m1)

                m2 = severities[method2]
                # Replace "Likely benign" and "Likely pathogenic" with "Uncertain significance"
                m2 = np.where(m2 == 'Likely pathogenic', 'Uncertain significance', m2)
                m2 = np.where(m2 == 'Likely benign', 'Uncertain significance', m2)

                # Build contingency table
                contingency_table = []

                for method1_severity in ['Benign', 'Uncertain significance', 'Pathogenic']:
                    temp = []
                    for method2_severity in ['Benign', 'Uncertain significance', 'Pathogenic']:
                        temp.append(sum([m1[i] == method1_severity and m2[i] == method2_severity for i in range(len(m1))]))
                    contingency_table.append(temp)

                n = np.array(contingency_table)

                # Calculate Test statistic
                # https://real-statistics.com/non-parametric-tests/mcnemar-bowker-test/
                B = 0
                for i, j in [(0, 1), (0, 2), (1, 2)]:
                    B += (n[i, j] - n[j, i]) ** 2 / (
                        np.max([n[i, j] + n[j, i], 1]))  # the max ensures that we do not divide by 0

                p_value = 1 - stats.chi2.cdf(B, degrees_of_freedom)

                results[cnv_type][f'{method1} vs {method2}'] = {
                    'Test Statistic': B,
                    'p-value': p_value,
                    'contingency_table': contingency_table
                }

    with open(output, 'w') as f:
        json.dump(results, f, indent=2)
