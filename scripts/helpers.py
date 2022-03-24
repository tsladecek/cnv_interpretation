import os

import pandas as pd

from scripts.config import settings


def get_marcnv():
    return pd.read_csv(settings.MARCNV_TABLE, sep='\t', compression='gzip')


def get_isv():
    return pd.read_csv(settings.ISV_TABLE, sep='\t', compression='gzip')


def datacheck(func):
    def check_data_wrapper(*args, **kwargs):
        output = kwargs['output']
        force_recreate = True if 'force_recreate' in kwargs and kwargs['force_recreate'] else False
        if force_recreate:
            return func(*args, **kwargs)
        elif os.path.exists(output):
            while True:
                try:
                    recreate = int(input(f'Reacreate {output}? (0 = No, 1 = Yes): '))
                except ValueError:
                    print('Only allowed values are 0 and 1')
                else:
                    if recreate not in [0, 1]:
                        continue
                    break
            if recreate == 1:
                return func(*args, **kwargs)
            else:
                return
        else:
            return func(*args, **kwargs)

    return check_data_wrapper
