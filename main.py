import os
import sys
from argparse import ArgumentParser

from scripts.config import settings
from scripts.helpers import install_classifycnv
from scripts.tables.classifycnv_raw import classifycnv_raw
from scripts.tables.classifycnv_summary_table import classify_table
from scripts.tables.isv_table import isv_table
from scripts.tables.main_table import main_table

if __name__ == '__main__':
    parser = ArgumentParser('python main.py')

    parser.add_argument('-f', '--force', required=False, action='store_true', help='Force Recompute All')
    parser.add_argument('-rc', '--recompute_classifycnv', required=False, action='store_true')
    parser.add_argument('-rt', '--recompute_tables', required=False, action='store_true')
    parser.add_argument('-rp', '--recompute_plots', required=False, action='store_true')

    print('\n##########################################################')
    print('################### CNV Interpretation ###################')
    print('##########################################################\n')

    args = parser.parse_args()
    if sum([args.recompute_classifycnv, args.recompute_tables, args.recompute_plots, args.force]) == 0:
        parser.print_help()
        sys.exit()

    if args.recompute_classifycnv or args.force:
        # Download and install ClassifyCNV
        install_classifycnv()

        # Run ClassifyCNV
        for dataset in ['train', 'validation', 'test', 'test-long', 'test-multiple', 'likely', 'uncertain']:
            for cnv_type in ['loss', 'gain']:
                classifycnv_raw(output=os.path.join(settings.ROOT_DIR,
                                                    'tables', f'classifycnv/{dataset}_{cnv_type}.tsv'),
                                force_recreate=args.force)

    # TABLES
    if args.recompute_tables or args.force:
        isv_table(output=settings.ISV_TABLE, force_recreate=args.force)
        classify_table(output=settings.CLASSIFYCNV_TABLE, force_recreate=args.force)
        main_table(output=settings.MAIN_TABLE, force_recreate=args.force)

    # PLOTS
    if args.recompute_plots or args.force:
        pass
