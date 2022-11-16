import os
import pathlib


class Settings:
    ROOT_DIR = pathlib.Path(__file__).parent.parent.resolve()
    MARCNV_TABLE = os.path.join(ROOT_DIR, 'data', 'marcnv.tsv.gz')
    ISV_TABLE = os.path.join(ROOT_DIR, 'tables', 'isv_table.tsv.gz')
    CLASSIFYCNV_TABLE = os.path.join(ROOT_DIR, 'tables', 'classifycnv_table.tsv.gz')
    MAIN_TABLE = os.path.join(ROOT_DIR, 'tables', 'main_table.tsv.gz')

    CLASSIFYCNV_DIR_NAME = 'ClassifyCNV-1.1.1'

    EVALUATION_DATASETS = ['test', 'test-multiple', 'test-long']

    MARCNV_BENIGN_DATABASE = 'DGV-GS-OUTER'
    MARCNV_HI = 1
    MARCNV_LB = 0

    DPI = 300
    FIGURE_FORMAT = '.png'
    FONT_SIZE = 5
    FONT_FAMILY = 'sans-serif'

    COLORS = {
        'TP': '#81B773',
        'TN': '#AAE59A',
        'Uncertain': '#D5DBD6',
        'FP': '#FDCBC0',
        'FN': '#F48B8B',
        'Benign': '#81B773',
        'Likely benign': '#AAE59A',
        'Likely pathogenic': '#FDCBC0',
        'Pathogenic': '#F48B8B'
    }


settings = Settings()
