from bi.Bi import CBi
from Combiner.KLine_Combiner import CKLine_Combiner
from Common.CEnum import BiDirection, FenxingType


class CEigen(CKLine_Combiner[CBi]):
    def __init__(self, bi, _dir):
        super(CEigen, self).__init__(bi, _dir)
        self.gap = False

    def update_fx(self, _pre: 'CEigen', _next: 'CEigen', exclude_included=False, allow_top_equal=None):
        super(CEigen, self).update_fx(_pre, _next, exclude_included, allow_top_equal)
        if (self.fx == FenxingType.TOP and _pre.high < self.low) or \
           (self.fx == FenxingType.BOTTOM and _pre.low > self.high):
            self.gap = True

    def __str__(self):
        return f"{self.lst[0].idx}~{self.lst[-1].idx} gap={self.gap} fx={self.fx}"

    def GetPeakBiIdx(self):
        assert self.fx != FenxingType.UNKNOWN
        bi_dir = self.lst[0].dir
        if bi_dir == BiDirection.UP:  # 下降线段
            return self.get_peak_klu(is_high=False).idx-1
        else:
            return self.get_peak_klu(is_high=True).idx-1
