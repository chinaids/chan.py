from Common.CEnum import TrendType
from Common.ChanException import CChanException, ErrCode


class CTrendModel:
    def __init__(self, trend_type: TrendType, T: int):
        self.T = T
        self.arr = []
        self.type = trend_type

    def add(self, value) -> float:
        self.arr.append(value)
        if len(self.arr) > self.T:
            self.arr = self.arr[-self.T:]
        if self.type == TrendType.MEAN:
            return sum(self.arr)/len(self.arr)
        elif self.type == TrendType.MAX:
            return max(self.arr)
        elif self.type == TrendType.MIN:
            return min(self.arr)
        else:
            raise CChanException(f"Unknown trendModel Type = {self.type}", ErrCode.PARA_ERROR)
