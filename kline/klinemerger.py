# from functools import cached_property
from typing import Literal, Iterable, List, Optional, Self, TypeVar, Union, overload

from Common.cache import make_cache
from Common.CEnum import FenxingType, KLineDir
from Common.ChanException import CChanException, ErrCode
from schema.klineunit import KLineUnit
from schema.mergedkline import MergedKLineUnit, MergedKLine

# from .Combine_Item import CCombine_Item

T = TypeVar('T')


class KLineMerger:

    def __init__(self,
                 exclude_included: bool = False,
                 allow_top_equal: Literal[-1, 1] = None
                 ):
        """
        allow_top_equal = None普通模式
        allow_top_equal = 1 被包含，顶部相等不合并
        allow_top_equal = -1 被包含，底部相等不合并
        """

        self.exclude_included = exclude_included
        self.allow_top_equal = allow_top_equal

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

    def merge_single_item(self, item: KLineUnit, merged: MergedKLineUnit) -> KLineDir:
        """
        - 假设，第 n 根 K 线满足第 n 根与第 n+1 根的包含关系，而第 n 根与第 n-1 根不是包含关系，那么如果 gn>=gn-1，那么称第 n-1、n、n+1 根 K 线是向上的；
        - 如果 dn<=dn-1，那么称第 n-1、n、n+1根 K 线是向下的。
        - 有人可能又要问，如果 gn<gn-1 且 dn>dn-1，算什么？那就是一种包含关系，这就违反了前面第 n根与第 n-1 根不是包含关系的假设。
        - 同样道理，gn>=gn-1 与 dn<=dn-1 不可能同时成立。

        """
        _dir = self.check_merge(item, merged)
        if _dir == KLineDir.COMBINE:
            merged.elements.append(item)
            self.clear_merged_cache(merged)
        # else:
        #     if not merged.direction:
        #         print('update merged direction to:', _dir)
        #         merged.direction = _dir

        # 返回UP/DOWN/COMBINE给KL_LIST，设置下一个的方向
        return _dir

    def update_fx(self, pre: MergedKLineUnit, mid: MergedKLineUnit, nxt: MergedKLineUnit):
        """
        Update fenxing type of mid
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

    def merge_klineunits(self, units: List[KLineUnit]) -> List[MergedKLineUnit]:
        """
        Given a list of K line units, return a list of merged K line
        """
        first_merged = MergedKLineUnit(elements=[units[0]])
        not_contain_idx = 1
        for u in units[1:]:
            _dir = self.check_merge(u, first_merged)
            if _dir == KLineDir.COMBINE:
                first_merged.elements.append(u)
                not_contain_idx += 1
            else:
                first_merged.direction = _dir
                break  # merge until the first kline that is not contained

        merged_list = [first_merged]
        merged = MergedKLineUnit(elements=[units[not_contain_idx]])

        for u in units[not_contain_idx+1:]:
            _dir = self.check_merge(u, merged)
            if _dir == KLineDir.COMBINE:
                merged.elements.append(u)
                self.clear_merged_cache(merged)
            else:
                merged.direction = _dir
                merged_list.append(merged)
                merged = MergedKLineUnit(elements=[u])

        if merged.elements[0].time != merged_list[-1].elements[0].time:
            merged_list.append(merged)

        return merged_list





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
