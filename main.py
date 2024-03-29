import os
import sys
from argparse import ArgumentParser

from scripts.config import settings
from scripts.helpers import install_classifycnv
from scripts.plots.bars import bars_database_comparison, bars_marcnv_options, bars_method_comparison, \
    bars_method_comparison_together
from scripts.plots.benign_db_comparison import benign_db_comparison
from scripts.plots.marcnv_isv_split_distribution import marcnv_isv_split_distribution
from scripts.plots.marcnv_isv_stack import marcnv_isv_stack
from scripts.plots.marcnv_vs_isv import marcnv_vs_isv
from scripts.tables.classifycnv_raw import classifycnv_raw
from scripts.tables.classifycnv_summary_table import classify_table
from scripts.tables.clinvar_marcnv_isv import clinvar_vs_marcnv_vs_isv, conflicting_predictions
from scripts.tables.isv_table import isv_table
from scripts.tables.main_table import main_table
from scripts.tables.method_comparison import method_comparison, mcnemar_bowker

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
        clinvar_vs_marcnv_vs_isv(output='tables/clinvar_vs_marcnv_vs_isv.tsv', force_recreate=args.force)
        conflicting_predictions(output='tables/conflicting_predictions.tsv', force_recreate=args.force)
        method_comparison(output='tables/method_comparison.tsv', force_recreate=args.force)
        mcnemar_bowker(output='tables/mcnemar_bowker.json', force_recreate=args.force)

    # PLOTS
    if args.recompute_plots or args.force:
        benign_db_comparison(output='plots/figure_1' + settings.FIGURE_FORMAT, force_recreate=args.force)
        bars_marcnv_options(output='plots/figure_2' + settings.FIGURE_FORMAT, force_recreate=args.force)
        bars_method_comparison(output='plots/figure_3' + settings.FIGURE_FORMAT,
                               force_recreate=args.force)
        marcnv_isv_stack(output='plots/figure_4' + settings.FIGURE_FORMAT, force_recreate=args.force)
        bars_database_comparison(output='plots/bars_database_comparison' + settings.FIGURE_FORMAT,
                                 force_recreate=args.force)
        bars_method_comparison_together(output='plots/bars_method_comparison_both_cnv_types' + settings.FIGURE_FORMAT,
                                        force_recreate=args.force)
        marcnv_vs_isv(output='plots/marcnv_vs_isv' + settings.FIGURE_FORMAT, force_recreate=args.force)
        marcnv_isv_split_distribution(output='plots/marcnv_isv_split_distribution' + settings.FIGURE_FORMAT,
                                      force_recreate=args.force)
        bars_method_comparison(output='plots/benign_cnvs_method_comparison' + settings.FIGURE_FORMAT,
                               clinsig='Benign',
                               force_recreate=args.force)
        bars_method_comparison(output='plots/pathogenic_cnvs_method_comparison' + settings.FIGURE_FORMAT,
                               clinsig='Pathogenic',
                               force_recreate=args.force)