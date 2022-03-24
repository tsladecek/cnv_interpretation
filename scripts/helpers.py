import os
import subprocess

import pandas as pd
import requests as requests

from scripts.config import settings


def get_marcnv():
    return pd.read_csv(settings.MARCNV_TABLE, sep='\t', compression='gzip')


def get_isv():
    return pd.read_csv(settings.ISV_TABLE, sep='\t', compression='gzip')


def get_classifycnv():
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
