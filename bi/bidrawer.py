from typing import List, Optional

# from Common.cache import make_cache
from Common.CEnum import BiDirection, BiType, DataField, FenxingType, MACDAlgo
from Common.ChanException import CChanException, ErrCode
# from kline.kline import KLine
# from kline.klineunit import KLineUnit

# from Seg.Seg import CSeg
# from BuySellPoint.BuySellPoint import CBuySellPoint

from typing import List, Optional, Union, overload

from Common.CEnum import FenxingType, KLineDir
from kline.kline import KLine

from .Bi import CBi
from config.biconfig import BiConfig


from schema.bi import Bi
from schema.klineunit import KLineUnit
from schema.mergedkline import MergedKLineUnit


class BiDrawer:
    """
    # Given an unfinished Bi, add new k lines unit to the Bi and detect whether it is finished
    """
    def __init__(self, config: BiConfig):
        self.bi_list: List[Bi] = []
        self.last_end = None  # 最后一笔的尾部
        self.config = config

        self.free_klc_lst = []  # 仅仅用作第一笔未画出来之前的缓存，为了获得更精准的结果而已，不加这块逻辑其实对后续计算没太大影响
        # self.bi = bi
        # self.finished = bi.finished

    # def update_virtual_end(self, kline: MergedKLineUnit):
    #     # self._sure_end = self.end_klc
    #     self.update_new_end(new_klc)
    #     self.finished = False
    #     # self.clean_cache()
    #
    # def restore_from_virtual_end(self):
    #     self._is_sure = True
    #     assert self.sure_end is not None
    #     self.update_new_end(new_klc=self.sure_end)
    #     self._sure_end = None
    #     self.clean_cache()
    #
    # def is_virtual_end(self):
    #     return self.sure_end is not None
    #
    # def update_new_end(self, new_klc: KLine):
    #     self._end_klc = new_klc
    #     self.check()
    #     self.clean_cache()

    def try_create_first_bi(self, klc: KLine) -> bool:
        for exist_free_klc in self.free_klc_lst:
            if exist_free_klc.fx == klc.fx:
                continue
            if self.can_make_bi(klc, exist_free_klc):
                self.add_new_bi(exist_free_klc, klc)
                self.last_end = klc
                return True
        self.free_klc_lst.append(klc)
        self.last_end = klc
        return False

    def update_bi(self, klc: KLine, last_klc: KLine, cal_virtual: bool) -> bool:
        # klc: 倒数第二根klc
        # last_klc: 倒数第1根klc
        flag1 = self.update_bi_sure(klc)
        if cal_virtual:
            flag2 = self.try_add_virtual_bi(last_klc)
            return flag1 or flag2
        else:
            return flag1

    def can_update_peak(self, klc: KLine):
        if self.config.bi_allow_sub_peak or len(self.bi_list) < 2:
            return False
        if self.bi_list[-1].is_down() and klc.high < self.bi_list[-1].get_begin_val():
            return False
        if self.bi_list[-1].is_up() and klc.low > self.bi_list[-1].get_begin_val():
            return False
        if not end_is_peak(self.bi_list[-2].begin_klc, klc):
            return False
        if self[-1].is_down() and self[-1].get_end_val() < self[-2].get_begin_val():
            return False
        if self[-1].is_up() and self[-1].get_end_val() > self[-2].get_begin_val():
            return False
        return True

    def update_bi_sure(self, klc: KLine) -> bool:
        # klc: 倒数第二根klc
        _tmp_end = self.get_last_klu_of_last_bi()
        self.delete_virtual_bi()
        # 返回值：是否出现新笔
        if klc.fx == FenxingType.UNKNOWN:
            return _tmp_end != self.get_last_klu_of_last_bi()  # 虚笔是否有变
        if self.last_end is None or len(self.bi_list) == 0:
            return self.try_create_first_bi(klc)
        if klc.fx == self.last_end.fx:
            return self.try_update_end(klc)
        elif self.can_make_bi(klc, self.last_end):
            self.add_new_bi(self.last_end, klc)
            self.last_end = klc
            return True
        elif self.can_update_peak(klc):
            self.bi_list = self.bi_list[:-1]
            return self.try_update_end(klc)
        return _tmp_end != self.get_last_klu_of_last_bi()

    def delete_virtual_bi(self):
        if len(self) > 0 and not self.bi_list[-1].is_sure:
            if self.bi_list[-1].is_virtual_end():
                self.bi_list[-1].restore_from_virtual_end()
            else:
                del self.bi_list[-1]

    def try_add_virtual_bi(self, klc: KLine, need_del_end=False):
        if need_del_end:
            self.delete_virtual_bi()
        if len(self) == 0:
            return False
        if klc.idx == self[-1].end_klc.idx:
            return False
        if (self[-1].is_up() and klc.high >= self[-1].end_klc.high) or (
                self[-1].is_down() and klc.low <= self[-1].end_klc.low):
            # 更新最后一笔
            self.bi_list[-1].update_virtual_end(klc)
            return True
        _tmp_klc = klc
        while _tmp_klc and _tmp_klc.idx > self[-1].end_klc.idx:
            assert _tmp_klc is not None
            if not self.satisfy_bi_span(_tmp_klc, self[-1].end_klc):
                return False
            if ((self[-1].is_down() and _tmp_klc.dir == KLineDir.UP and _tmp_klc.low > self[-1].end_klc.low) or (
                    self[-1].is_up() and _tmp_klc.dir == KLineDir.DOWN and _tmp_klc.high < self[-1].end_klc.high)) and \
                    self[-1].end_klc.check_fx_valid(_tmp_klc, self.config.bi_fx_check, for_virtual=True):
                # 新增一笔
                self.add_new_bi(self.last_end, _tmp_klc, is_sure=False)
                return True
            _tmp_klc = _tmp_klc.pre
        return False

    def add_new_bi(self, pre_klc, cur_klc, is_sure=True):
        self.bi_list.append(CBi(pre_klc, cur_klc, idx=len(self.bi_list), is_sure=is_sure))
        if len(self.bi_list) >= 2:
            self.bi_list[-2].next = self.bi_list[-1]
            self.bi_list[-1].pre = self.bi_list[-2]

    def satisfy_bi_span(self, klc: KLine, last_end: KLine):
        bi_span = self.get_klc_span(klc, last_end)
        if self.config.is_strict:
            return bi_span >= 4
        uint_kl_cnt = 0
        tmp_klc = last_end.next
        while tmp_klc:
            uint_kl_cnt += len(tmp_klc.lst)
            if not tmp_klc.next:  # 最后尾部虚笔的时候，可能klc.idx == last_end.idx+1
                return False
            if tmp_klc.next.idx < klc.idx:
                tmp_klc = tmp_klc.next
            else:
                break
        return bi_span >= 3 and uint_kl_cnt >= 3

    def get_klc_span(self, klc: KLine, last_end: KLine) -> int:
        span = klc.idx - last_end.idx
        if not self.config.gap_as_kl:
            return span
        if span >= 4:  # 加速运算，如果span需要真正精确的值，需要去掉这一行
            return span
        tmp_klc = last_end
        while tmp_klc and tmp_klc.idx < klc.idx:
            if tmp_klc.has_gap_with_next():
                span += 1
            tmp_klc = tmp_klc.next
        return span

    def can_make_bi(self, klc: KLine, last_end: KLine):
        if self.config.bi_algo == "fx":
            return True
        satisify_span = self.satisfy_bi_span(klc, last_end) if last_end.check_fx_valid(klc,
                                                                                       self.config.bi_fx_check) else False
        if satisify_span and self.config.bi_end_is_peak:
            return end_is_peak(last_end, klc)
        else:
            return satisify_span

    def try_update_end(self, klc: KLine) -> bool:
        if len(self.bi_list) == 0:
            return False
        last_bi = self.bi_list[-1]
        if (last_bi.is_up() and klc.fx == FenxingType.TOP and klc.high >= last_bi.get_end_val()) or \
                (last_bi.is_down() and klc.fx == FenxingType.BOTTOM and klc.low <= last_bi.get_end_val()):
            last_bi.update_new_end(klc)
            self.last_end = klc
            return True
        else:
            return False

    def get_last_klu_of_last_bi(self) -> Optional[int]:
        return self.bi_list[-1].get_end_klu().idx if len(self) > 0 else None

    def end_is_peak(last_end: KLine, cur_end: KLine) -> bool:
        if last_end.fx == FenxingType.BOTTOM:
            cmp_thred = cur_end.high  # 或者严格点选择get_klu_max_high()
            klc = last_end.get_next()
            while True:
                if klc.idx >= cur_end.idx:
                    return True
                if klc.high > cmp_thred:
                    return False
                klc = klc.get_next()
        elif last_end.fx == FenxingType.TOP:
            cmp_thred = cur_end.low  # 或者严格点选择get_klu_min_low()
            klc = last_end.get_next()
            while True:
                if klc.idx >= cur_end.idx:
                    return True
                if klc.low < cmp_thred:
                    return False
                klc = klc.get_next()
        return True

    # def cal_macd_metric(self, macd_algo, is_reverse):
    #     if macd_algo == MACDAlgo.AREA:
    #         return self.cal_macd_half(is_reverse)
    #     elif macd_algo == MACDAlgo.PEAK:
    #         return self.cal_macd_peak()
    #     elif macd_algo == MACDAlgo.FULL_AREA:
    #         return self.cal_macd_area()
    #     elif macd_algo == MACDAlgo.DIFF:
    #         return self.cal_macd_diff()
    #     elif macd_algo == MACDAlgo.SLOPE:
    #         return self.cal_macd_slope()
    #     elif macd_algo == MACDAlgo.AMP:
    #         return self.cal_macd_amp()
    #     elif macd_algo == MACDAlgo.AMOUNT:
    #         return self.cal_macd_trade_metric(DataField.FIELD_TURNOVER, cal_avg=False)
    #     elif macd_algo == MACDAlgo.VOLUME:
    #         return self.cal_macd_trade_metric(DataField.FIELD_VOLUME, cal_avg=False)
    #     elif macd_algo == MACDAlgo.VOLUME_AVG:
    #         return self.cal_macd_trade_metric(DataField.FIELD_VOLUME, cal_avg=True)
    #     elif macd_algo == MACDAlgo.AMOUNT_AVG:
    #         return self.cal_macd_trade_metric(DataField.FIELD_TURNOVER, cal_avg=True)
    #     elif macd_algo == MACDAlgo.TURNRATE_AVG:
    #         return self.cal_macd_trade_metric(DataField.FIELD_TURNRATE, cal_avg=True)
    #     elif macd_algo == MACDAlgo.RSI:
    #         return self.Cal_Rsi()
    #     else:
    #         raise CChanException(f"unsupport macd_algo={macd_algo}, should be one of area/full_area/peak/diff/slope/amp", ErrCode.PARA_ERROR)

    # @make_cache
    # def Cal_Rsi(self):
    #     rsi_lst: List[float] = []
    #     for klc in self.klc_lst:
    #         rsi_lst.extend(klu.rsi for klu in klc.lst)
    #     return 10000.0/(min(rsi_lst)+1e-7) if self.is_down() else max(rsi_lst)
    #
    # @make_cache
    # def cal_macd_area(self):
    #     _s = 1e-7
    #     for klc in self.klc_lst:
    #         for klu in klc.lst:
    #             _s += abs(klu.macd.macd)
    #     return _s
    #
    # @make_cache
    # def cal_macd_peak(self):
    #     peak = 1e-7
    #     for klc in self.klc_lst:
    #         for klu in klc.lst:
    #             if abs(klu.macd.macd) > peak:
    #                 if self.is_down() and klu.macd.macd < 0:
    #                     peak = abs(klu.macd.macd)
    #                 elif self.is_up() and klu.macd.macd > 0:
    #                     peak = abs(klu.macd.macd)
    #     return peak
    #
    # def cal_macd_half(self, is_reverse):
    #     if is_reverse:
    #         return self.cal_macd_half_reverse()
    #     else:
    #         return self.cal_macd_half_obverse()
    #
    # @make_cache
    # def cal_macd_half_obverse(self):
    #     _s = 1e-7
    #     begin_klu = self.get_begin_klu()
    #     peak_macd = begin_klu.macd.macd
    #     for klc in self.klc_lst:
    #         for klu in klc.lst:
    #             if klu.idx < begin_klu.idx:
    #                 continue
    #             if klu.macd.macd*peak_macd > 0:
    #                 _s += abs(klu.macd.macd)
    #             else:
    #                 break
    #         else:  # 没有被break，继续找写一个KLC
    #             continue
    #         break
    #     return _s
    #
    # @make_cache
    # def cal_macd_half_reverse(self):
    #     _s = 1e-7
    #     begin_klu = self.get_end_klu()
    #     peak_macd = begin_klu.macd.macd
    #     for klc in self.klc_lst[::-1]:
    #         for klu in klc[::-1]:
    #             if klu.idx > begin_klu.idx:
    #                 continue
    #             if klu.macd.macd*peak_macd > 0:
    #                 _s += abs(klu.macd.macd)
    #             else:
    #                 break
    #         else:  # 没有被break，继续找写一个KLC
    #             continue
    #         break
    #     return _s
    #
    # @make_cache
    # def cal_macd_diff(self):
    #     """
    #     macd红绿柱最大值最小值之差
    #     """
    #     _max, _min = float("-inf"), float("inf")
    #     for klc in self.klc_lst:
    #         for klu in klc.lst:
    #             macd = klu.macd.macd
    #             if macd > _max:
    #                 _max = macd
    #             if macd < _min:
    #                 _min = macd
    #     return _max-_min
    #
    # @make_cache
    # def cal_macd_slope(self):
    #     begin_klu = self.get_begin_klu()
    #     end_klu = self.get_end_klu()
    #     if self.is_up():
    #         return (end_klu.high - begin_klu.low)/end_klu.high/(end_klu.idx - begin_klu.idx + 1)
    #     else:
    #         return (begin_klu.high - end_klu.low)/begin_klu.high/(end_klu.idx - begin_klu.idx + 1)
    #
    # @make_cache
    # def cal_macd_amp(self):
    #     begin_klu = self.get_begin_klu()
    #     end_klu = self.get_end_klu()
    #     if self.is_down():
    #         return (begin_klu.high-end_klu.low)/begin_klu.high
    #     else:
    #         return (end_klu.high-begin_klu.low)/begin_klu.low
    #
    # def cal_macd_trade_metric(self, metric: str, cal_avg=False) -> float:
    #     _s = 0
    #     for klc in self.klc_lst:
    #         for klu in klc.lst:
    #             metric_res = klu.trade_info.metric[metric]
    #             if metric_res is None:
    #                 return 0.0
    #             _s += metric_res
    #     return _s / self.get_klu_cnt() if cal_avg else _s
    #
    # def set_klc_lst(self, lst):
    #     self._klc_lst = lst
