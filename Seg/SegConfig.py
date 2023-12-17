from Common.CEnum import LeftSegMethod
from Common.ChanException import CChanException, ErrCode


class CSegConfig:
    def __init__(self, seg_algo="chan", left_method="peak"):
        self.seg_algo = seg_algo
        if left_method == "all":
            self.left_method = LeftSegMethod.ALL
        elif left_method == "peak":
            self.left_method = LeftSegMethod.PEAK
        else:
            raise CChanException(f"unknown left_seg_method={left_method}", ErrCode.PARA_ERROR)
