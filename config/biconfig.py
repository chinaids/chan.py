from Common.CEnum import FenxingCheckMethod
from Common.ChanException import CChanException, ErrCode


class BiConfig:
    bi_algo: str = "normal"
    is_strict: bool = True
    gap_as_kl: bool = True
    bi_end_is_peak: bool = True
    bi_allow_sub_peak: bool = True
    bi_fx_check: FenxingCheckMethod = FenxingCheckMethod.HALF
