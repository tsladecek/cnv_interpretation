from scripts.helpers import get_marcnv, datacheck, get_isv


##
@datacheck
def main_table(output: str, **kwargs):
    marcnv = get_marcnv()
    isv_df = get_isv()

    return marcnv, isv_df
