import os
from argparse import ArgumentParser

from scripts.config import settings
from scripts.helpers import get_classifycnv
from scripts.tables.classifycnv_raw import classifycnv_raw
from scripts.tables.classifycnv_summary_table import classify_table
from scripts.tables.isv_table import isv_table
from scripts.tables.main_table import main_table


if __name__ == '__main__':
    parser = ArgumentParser('CNV Interpretation - Results')

    parser.add_argument('-f', '--force', required=False, action='store_true', help='Force Recreate')
    parser.add_argument('-r', '--recompute', required=False, action='store_true')

    args = parser.parse_args()
    print('\n##########################################################')
    print('################### CNV Interpretation ###################')
    print('##########################################################\n')
    # Download and install ClassifyCNV
    get_classifycnv()

    # Run ClassifyCNV
    if args.recompute:
        for dataset in ['train', 'validation', 'test', 'test-long', 'test-multiple', 'likely', 'uncertain']:
            for cnv_type in ['loss', 'gain']:
                classifycnv_raw(output=os.path.join(settings.ROOT_DIR,
                                                    'tables', f'classifycnv/{dataset}_{cnv_type}.tsv'))

    # TABLES
    isv_table(output=settings.ISV_TABLE, force_recreate=args.force)
    classify_table(output=settings.CLASSIFYCNV_TABLE, force_recreate=args.force)
    main_table(output=settings.MAIN_TABLE, force_recreate=args.force)

    # PLOTS
