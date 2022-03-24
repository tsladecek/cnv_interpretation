from scripts.config import settings
from scripts.tables.isv_table import isv_table
from scripts.tables.main_table import main_table

FORCE_RECREATE = False
if __name__ == '__main__':
    isv_table(output=settings.ISV_TABLE, force_recreate=FORCE_RECREATE)
    main_table(output='tables/main_table.tsv.gz', force_recreate=FORCE_RECREATE)
