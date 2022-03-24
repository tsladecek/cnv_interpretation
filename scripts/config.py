import os
import pathlib


class Settings:
    ROOT_DIR = pathlib.Path(__file__).parent.parent.resolve()
    MARCNV_TABLE = os.path.join(ROOT_DIR, 'data', 'marcnv.tsv.gz')
    ISV_TABLE = os.path.join(ROOT_DIR, 'tables', 'isv_table.tsv.gz')


settings = Settings()
