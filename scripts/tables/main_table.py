from scripts.config import settings
from scripts.helpers import get_marcnv, datacheck, get_isv, get_classifycnv


@datacheck
def main_table(output: str, **kwargs):
    marcnv = get_marcnv()
    isv_df = get_isv()
    classifycnv = get_classifycnv()

    return marcnv, isv_df


if __name__ == '__main__':
    main_table(output=settings.MAIN_TABLE)
