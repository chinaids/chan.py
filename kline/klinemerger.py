# from functools import cached_property
from typing import Literal, Iterable, List, Optional, Self, TypeVar, Union, overload

from Common.cache import make_cache
from Common.CEnum import FenxingType, KLineDir
from Common.ChanException import CChanException, ErrCode
# from kline.klineunit import KLineUnit
from schema.klineunit import KLineUnit
from schema.mergedkline import MergedKLineUnit, MergedKLine

# from .Combine_Item import CCombine_Item

T = TypeVar('T')


class KLineMerger:
    """
    Given a list of K line units, return a list of merged K line
    """

    def __init__(self,
                 exclude_included: bool = False,
                 allow_top_equal: Literal[-1, 1] = None
                 ):

        self.exclude_included = exclude_included
        self.allow_top_equal = allow_top_equal
        # allow_top_equal = None普通模式
        # allow_top_equal = 1 被包含，顶部相等不合并
        # allow_top_equal = -1 被包含，底部相等不合并

        # self.__time_begin = item.time_begin
        # self.__time_end = item.time_end
        # self.__high = item.high
        # self.__low = item.low
        #
        # self.__lst: List[T] = [kl_unit]  # 本级别每一根单位K线
        #
        # # self.__dir = _dir
        # self.__fx = FenxingType.UNKNOWN
        # self.__pre: Optional[Self] = None
        # self.__next: Optional[Self] = None

    # def clean_cache(self):
    #     self._memoize_cache = {}

    # @property
    # def time_begin(self): return self.__time_begin
    #
    # @property
    # def time_end(self): return self.__time_end
    #
    # @property
    # def high(self): return self.__high
    #
    # @property
    # def low(self): return self.__low
    #
    # @property
    # def lst(self): return self.__lst
    #
    # @property
    # def dir(self): return self.__dir
    #
    # @property
    # def fx(self): return self.__fx
    #
    # @property
    # def pre(self) -> Self:
    #     assert self.__pre is not None
    #     return self.__pre
    #
    # @property
    # def next(self): return self.__next
    #
    # def get_next(self) -> Self:
    #     assert self.next is not None
    #     return self.next
    @staticmethod
    def clear_merged_cache(merged: MergedKLineUnit):
        attr_list = ['begin_time', 'end_time', 'open', 'close', 'high', 'low',
                     'volume', 'turnover']
        for a in attr_list:
            if getattr(merged, a):
                delattr(merged, a)

    def check_merge(self, item: KLineUnit, merged: MergedKLineUnit):
        if merged.high >= item.high and merged.low <= item.low:
            return KLineDir.COMBINE
        if merged.high <= item.high and merged.low >= item.low:
            if self.allow_top_equal == 1 and merged.high == item.high and merged.low > item.low:
                return KLineDir.DOWN
            elif self.allow_top_equal == -1 and merged.low == item.low and merged.high < item.high:
                return KLineDir.UP
            return KLineDir.INCLUDED if self.exclude_included else KLineDir.COMBINE
        if merged.high > item.high and merged.low > item.low:
            return KLineDir.DOWN
        if merged.high < item.high and merged.low < item.low:
            return KLineDir.UP

        raise CChanException("combine type unknown", ErrCode.COMBINER_ERR)

    # def add(self, unit_kl: T):
    #     # only for deepcopy
    #     self.__lst.append(unit_kl)
    #
    # def set_fx(self, fx: FenxingType):
    #     # only for deepcopy
    #     self.__fx = fx

    def merge_item(self, item: KLineUnit, merged: MergedKLineUnit) -> KLineDir:

        _dir = self.check_merge(item, merged)
        if _dir == KLineDir.COMBINE:
            merged.elements.append(item)
            self.clear_merged_cache(merged)

        # 返回UP/DOWN/COMBINE给KL_LIST，设置下一个的方向
        return _dir


    def update_fx(self, pre: MergedKLineUnit, mid: MergedKLineUnit, nxt: MergedKLineUnit):
        """
        update fenxing type of mid
        """

        if self.exclude_included:
            if pre.high < mid.high and nxt.high <= mid.high and nxt.low < mid.low:
                if self.allow_top_equal == 1 or nxt.high < mid.high:
                    mid.fenxing = FenxingType.TOP
            elif nxt.high > mid.high and pre.low > mid.low and nxt.low >= mid.low:
                if self.allow_top_equal == -1 or nxt.low > mid.low:
                    mid.fenxing = FenxingType.BOTTOM
        elif pre.high < mid.high and nxt.high < mid.high and pre.low < mid.low and nxt.low < mid.low:
            mid.fenxing = FenxingType.TOP
        elif pre.high > mid.high and nxt.high > mid.high and pre.low > mid.low and nxt.low > mid.low:
            mid.fenxing = FenxingType.BOTTOM

    # def __str__(self):
    #     return f"{self.time_begin}~{self.time_end} {self.low}->{self.high}"
    #
    # @overload
    # def __getitem__(self, index: int) -> T:
    #     ...
    #
    # @overload
    # def __getitem__(self, index: slice) -> List[T]:
    #     ...

    # def __getitem__(self, index: Union[slice, int]) -> Union[List[T], T]:
    #     return self.lst[index]
    #
    # def __len__(self):
    #     return len(self.lst)
    #
    # def __iter__(self) -> Iterable[T]:
    #     yield from self.lst

    # def set_pre(self, _pre: Self):
    #     self.__pre = _pre
    #     # self.clean_cache()
    #
    # def set_next(self, _next: Self):
    #     self.__next = _next
    #     # self.clean_cache()
