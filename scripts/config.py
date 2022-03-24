import os
import pathlib


class Settings:
    ROOT_DIR = pathlib.Path(__file__).parent.parent.resolve()
    MARCNV_TABLE = os.path.join(ROOT_DIR, 'data', 'marcnv.tsv.gz')
    ISV_TABLE = os.path.join(ROOT_DIR, 'tables', 'isv_table.tsv.gz')
    CLASSIFYCNV_TABLE = os.path.join(ROOT_DIR, 'tables', 'classifycnv_table.tsv.gz')
    MAIN_TABLE = os.path.join(ROOT_DIR, 'tables', 'main_table.tsv.gz')

    CLASSIFYCNV_DIR_NAME = 'ClassifyCNV-1.1.1'


settings = Settings()
