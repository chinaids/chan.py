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

    def __init__(self, klines: List[KLineUnit],
                 exclude_included: bool = False,
                 allow_top_equal: Literal[-1, 1] = None
                 ):
        self.raw_items = klines  # CCombine_Item(kl_unit)
        self.merged_items = []

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
        # if merged.end_time:
        #     del merged.end_time
        #
        # del merged.open
        # del merged.close
        # del merged.high
        # del merged.low
        # del merged.volume
        # del merged.turnover


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

    def merge_item(self, item: KLineUnit, merged: MergedKLineUnit) -> MergedKLineUnit:

        # combine_item = CCombine_Item(unit_kl)
        _dir = self.check_merge(item, merged)
        if _dir == KLineDir.COMBINE:
            merged.elements.append(item)
            # if isinstance(unit_kl, KLineUnit):
            #     unit_kl.set_klc(self)
            # if self.dir == KLineDir.UP:
            #     if combine_item.high != combine_item.low or combine_item.high != self.high:  # 处理一字K线
            #         self.__high = max([self.high, combine_item.high])
            #         self.__low = max([self.low, combine_item.low])
            # elif self.dir == KLineDir.DOWN:
            #     if combine_item.high != combine_item.low or combine_item.low != self.low:  # 处理一字K线
            #         self.__high = min([self.high, combine_item.high])
            #         self.__low = min([self.low, combine_item.low])
            # else:
            #     raise CChanException(f"KLINE_DIR = {self.dir} err!!! must be {KLineDir.UP}/{KLineDir.DOWN}",
            #                          ErrCode.COMBINER_ERR)
            self._time_end = combine_item.time_end
            # self.clean_cache()
        # 返回UP/DOWN/COMBINE给KL_LIST，设置下一个的方向
        return _dir

    def get_peak_klu(self, is_high) -> T:
        # 获取最大值 or 最小值所在klu/bi
        return self.get_high_peak_klu() if is_high else self.get_low_peak_klu()

    @make_cache
    def get_high_peak_klu(self) -> T:
        for kl in self.lst[::-1]:
            if CCombine_Item(kl).high == self.high:
                return kl
        raise CChanException("can't find peak...", ErrCode.COMBINER_ERR)

    @make_cache
    def get_low_peak_klu(self) -> T:
        for kl in self.lst[::-1]:
            if CCombine_Item(kl).low == self.low:
                return kl
        raise CChanException("can't find peak...", ErrCode.COMBINER_ERR)

    def update_fx(self, _pre: Self, _next: Self, exclude_included=False, allow_top_equal=None):
        # allow_top_equal = None普通模式
        # allow_top_equal = 1 被包含，顶部相等不合并
        # allow_top_equal = -1 被包含，底部相等不合并
        self.set_next(_next)
        self.set_pre(_pre)
        _next.set_pre(self)
        if exclude_included:
            if _pre.high < self.high and _next.high <= self.high and _next.low < self.low:
                if allow_top_equal == 1 or _next.high < self.high:
                    self.__fx = FenxingType.TOP
            elif _next.high > self.high and _pre.low > self.low and _next.low >= self.low:
                if allow_top_equal == -1 or _next.low > self.low:
                    self.__fx = FenxingType.BOTTOM
        elif _pre.high < self.high and _next.high < self.high and _pre.low < self.low and _next.low < self.low:
            self.__fx = FenxingType.TOP
        elif _pre.high > self.high and _next.high > self.high and _pre.low > self.low and _next.low > self.low:
            self.__fx = FenxingType.BOTTOM
        # self.clean_cache()

    def __str__(self):
        return f"{self.time_begin}~{self.time_end} {self.low}->{self.high}"

    @overload
    def __getitem__(self, index: int) -> T:
        ...

    @overload
    def __getitem__(self, index: slice) -> List[T]:
        ...

    def __getitem__(self, index: Union[slice, int]) -> Union[List[T], T]:
        return self.lst[index]

    def __len__(self):
        return len(self.lst)

    def __iter__(self) -> Iterable[T]:
        yield from self.lst

    def set_pre(self, _pre: Self):
        self.__pre = _pre
        # self.clean_cache()

    def set_next(self, _next: Self):
        self.__next = _next
        # self.clean_cache()
