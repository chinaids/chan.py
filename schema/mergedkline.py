from pydantic import BaseModel, field_validator
from typing import List, Optional
from functools import cached_property

from schema.klineunit import KLineUnit
from Common.CEnum import FenxingType, KLineDir


# 合并后的K线
class MergedKLineUnit(BaseModel):

    _idx: int = -1
    direction: KLineDir
    elements: List[KLineUnit]
    fenxing: Optional[FenxingType] = FenxingType.UNKNOWN

    @cached_property
    def begin_time(self):
        return self.elements[0].time

    @cached_property
    def end_time(self):
        return self.elements[-1].time

    @cached_property
    def open(self):
        return self.elements[0].open

    @cached_property
    def close(self):
        return self.elements[-1].close

    @cached_property
    def high(self):
        price_high = [e.high for e in self.elements]
        return max(price_high) if self.direction == KLineDir.UP else min(price_high)

    @cached_property
    def low(self):
        price_low = [e.low for e in self.elements]
        return max(price_low) if self.direction == KLineDir.UP else min(price_low)

    @cached_property
    def volume(self):
        vol = [e.volume for e in self.elements if e.volume]
        return sum(vol) if vol else None

    @cached_property
    def turnover(self):
        to = [e.turnover for e in self.elements if e.turnover]
        return sum(to) if to else None

    def get_peak_klu(self, is_high) -> KLineUnit:
        # 获取最大值 or 最小值所在 KLineUnit
        return self.get_high_peak_klu() if is_high else self.get_low_peak_klu()

    def get_high_peak_klu(self) -> KLineUnit:
        for kl in self.elements[::-1]:
            if kl.high == self.high:
                return kl
        raise ValueError(f"can't find peak with high price {self.high}")

    def get_low_peak_klu(self) -> KLineUnit:
        for kl in self.elements[::-1]:
            if kl.low == self.low:
                return kl
        raise ValueError(f"can't find bottom with low price {self.low}")


    # @field_validator('direction', mode='after')
    # # @classmethod
    # def validate_direction(self):
    #     assert self.direction in [KLineDir.UP, KLineDir.DOWN], f'direction should be up or down, got {cls.direction}'


class MergedKLine(BaseModel):
    elements: List[MergedKLineUnit]

    # self.__time_begin = item.time_begin
# self.__time_end = item.time_end
# self.__high = item.high
# self.__low = item.low
#
# self.__lst: List[T] = [kl_unit]  # 本级别每一根单位K线
#
# self.__dir = _dir
# self.__fx = FenxingType.UNKNOWN
# self.__pre: Optional[Self] = None
# self.__next: Optional[Self] = None

# def __init__(self, kl_unit: KLineUnit, idx, _dir=KLineDir.UP):
#     super(KLine, self).__init__(kl_unit, _dir)
#     self.idx: int = idx
#     self.kl_type = kl_unit.kl_type
#     kl_unit.set_klc(self)
#
# def __str__(self):
#     fx_token = ""
#     if self.fx == FenxingType.TOP:
#         fx_token = "^"
#     elif self.fx == FenxingType.BOTTOM:
#         fx_token = "_"
#     return f"{self.idx}th{fx_token}:{self.time_begin}~{self.time_end}({self.kl_type}|{len(self.lst)}) low={self.low} high={self.high}"
#
# def GetSubKLC(self):
#     # 可能会出现相邻的两个KLC的子KLC会有重复
#     # 因为子KLU合并时正好跨过了父KLC的结束时间边界
#     last_klc = None
#     for klu in self.lst:
#         for sub_klu in klu.get_children():
#             if sub_klu.klc != last_klc:
#                 last_klc = sub_klu.klc
#                 yield sub_klu.klc
#
# def get_klu_max_high(self) -> float:
#     return max(x.high for x in self.lst)
#
# def get_klu_min_low(self) -> float:
#     return min(x.low for x in self.lst)
#
# def has_gap_with_next(self) -> bool:
#     assert self.next is not None
#     # 相同也算重叠，也就是没有gap
#     return not has_overlap(self.get_klu_min_low(), self.get_klu_max_high(), self.next.get_klu_min_low(), self.next.get_klu_max_high(), equal=True)
#
# def check_fx_valid(self, item2: "kline", method, for_virtual=False):
#     # for_virtual: 虚笔时使用
#     assert self.next is not None and item2.pre is not None
#     assert self.pre is not None
#     assert item2.idx > self.idx
#     if self.fx == FenxingType.TOP:
#         assert for_virtual or item2.fx == FenxingType.BOTTOM
#         if method == FenxingCheckMethod.HALF:  # 检测前两KLC
#             item2_high = max([item2.pre.high, item2.high])
#             self_low = min([self.low, self.next.low])
#         elif method == FenxingCheckMethod.LOSS:  # 只检测顶底分形KLC
#             item2_high = item2.high
#             self_low = self.low
#         elif method in (FenxingCheckMethod.STRICT, FenxingCheckMethod.TOTALLY):
#             if for_virtual:
#                 item2_high = max([item2.pre.high, item2.high])
#             else:
#                 assert item2.next is not None
#                 item2_high = max([item2.pre.high, item2.high, item2.next.high])
#             self_low = min([self.pre.low, self.low, self.next.low])
#         else:
#             raise CChanException("bi_fx_check config error!", ErrCode.CONFIG_ERROR)
#         if method == FenxingCheckMethod.TOTALLY:
#             return self.low > item2_high
#         else:
#             return self.high > item2_high and item2.low < self_low
#     elif self.fx == FenxingType.BOTTOM:
#         assert for_virtual or item2.fx == FenxingType.TOP
#         if method == FenxingCheckMethod.HALF:
#             item2_low = min([item2.pre.low, item2.low])
#             cur_high = max([self.high, self.next.high])
#         elif method == FenxingCheckMethod.LOSS:
#             item2_low = item2.low
#             cur_high = self.high
#         elif method in (FenxingCheckMethod.STRICT, FenxingCheckMethod.TOTALLY):
#             if for_virtual:
#                 item2_low = min([item2.pre.low, item2.low])
#             else:
#                 assert item2.next is not None
#                 item2_low = min([item2.pre.low, item2.low, item2.next.low])
#             cur_high = max([self.pre.high, self.high, self.next.high])
#         else:
#             raise CChanException("bi_fx_check config error!", ErrCode.CONFIG_ERROR)
#         if method == FenxingCheckMethod.TOTALLY:
#             return self.high < item2_low
#         else:
#             return self.low < item2_low and item2.high > cur_high
#     else:
#         raise CChanException("only top/bottom fx can check_valid_top_button", ErrCode.BI_ERR)
