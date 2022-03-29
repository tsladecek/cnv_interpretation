import os
import subprocess

from scripts.config import settings
from scripts.helpers import datacheck


@datacheck
def classifycnv_raw(output: str, **kwargs):
    dataset, cnv_type = os.path.split(output)[1].split('.')[0].split('_')
    bed_path = os.path.join(settings.ROOT_DIR, 'data', 'beds', f'{dataset}_{cnv_type}.bed')
    output_dir = os.path.join(settings.ROOT_DIR, 'tables', 'classifycnv')

    # Create output dir if it does not exist
    subprocess.run(['mkdir', '-p', output_dir])

    # run classifycnv
    os.chdir(os.path.join(settings.ROOT_DIR, settings.CLASSIFYCNV_DIR_NAME))

    ccnv_results_dir = os.path.join('ClassifyCNV_results', f'{dataset}_{cnv_type}')

    subprocess.run(['python', 'ClassifyCNV.py',
                    '--infile', bed_path,
                    '--GenomeBuild', 'hg38',
                    '--outdir', ccnv_results_dir])

    # Move results to output
    ccnv_results = os.path.join(ccnv_results_dir, 'Scoresheet.txt')
    subprocess.run(['cp', ccnv_results, output])

    os.chdir(os.path.join(settings.ROOT_DIR))
