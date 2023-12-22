from typing import List, Optional

from Common.cache import make_cache
from Common.CEnum import BiDirection, BiType, DataField, FenxingType, MACDAlgo
from Common.ChanException import CChanException, ErrCode
from KLine.KLine import CKLine
from KLine.KLineUnit import CKLineUnit

from Seg.Seg import CSeg
from BuySellPoint.BS_Point import CBS_Point


class CBi:
    def __init__(self, begin_klc: CKLine, end_klc: CKLine, idx: int, is_sure: bool):
        self._begin_klc = None  # begin_klc
        self._end_klc = None  # end_klc
        self._direction = None
        self._idx = idx
        self._type = BiType.STRICT

        self.set(begin_klc, end_klc)

        self._is_sure = is_sure
        self._sure_end = None

        self._klc_lst: List[CKLine] = []
        self._seg_idx: Optional[int] = None

        self.parent_seg: Optional[CSeg[CBi]] = None  # 在哪个线段里面

        self.bsp: Optional[CBS_Point] = None  # 尾部是不是买卖点

        self.next: Optional[CBi] = None
        self.pre: Optional[CBi] = None

        self._memorize_cache = {}

    def clean_cache(self):
        self._memorize_cache = {}

    @property
    def begin_klc(self):
        return self._begin_klc

    @property
    def end_klc(self):
        return self._end_klc

    @property
    def dir(self):
        return self._direction

    @property
    def idx(self):
        return self._idx

    @property
    def type(self):
        return self._type

    @property
    def is_sure(self):
        return self._is_sure

    @property
    def sure_end(self):
        return self._sure_end

    @property
    def klc_lst(self):
        return self._klc_lst

    @property
    def seg_idx(self):
        return self._seg_idx

    def set_seg_idx(self, idx):
        self._seg_idx = idx

    def __str__(self):
        return f"{self.dir}|{self.begin_klc} ~ {self.end_klc}"

    def check(self):
        if self.is_down():
            err = self.begin_klc.high > self.end_klc.low
        else:
            err = self.begin_klc.low < self.end_klc.high
        if err:
            raise CChanException(f"{self.idx}:{self.begin_klc[0].time}~{self.end_klc[-1].time}笔的方向和收尾位置不一致!", ErrCode.BI_ERR) from e

    def set(self, begin_klc: CKLine, end_klc: CKLine):
        self._begin_klc: CKLine = begin_klc
        self._end_klc: CKLine = end_klc
        if begin_klc.fx == FenxingType.BOTTOM:
            self._direction = BiDirection.UP
        elif begin_klc.fx == FenxingType.TOP:
            self._direction = BiDirection.DOWN
        else:
            raise CChanException("ERROR DIRECTION when creating bi", ErrCode.BI_ERR)
        self.check()
        self.clean_cache()

    @make_cache
    def get_begin_val(self):
        return self.begin_klc.low if self.is_up() else self.begin_klc.high

    @make_cache
    def get_end_val(self):
        return self.end_klc.high if self.is_up() else self.end_klc.low

    @make_cache
    def get_begin_klu(self) -> CKLineUnit:
        if self.is_up():
            return self.begin_klc.get_peak_klu(is_high=False)
        else:
            return self.begin_klc.get_peak_klu(is_high=True)

    @make_cache
    def get_end_klu(self) -> CKLineUnit:
        if self.is_up():
            return self.end_klc.get_peak_klu(is_high=True)
        else:
            return self.end_klc.get_peak_klu(is_high=False)

    @make_cache
    def amp(self):
        return abs(self.get_end_val() - self.get_begin_val())

    @make_cache
    def get_klu_cnt(self):
        return self.get_end_klu().idx - self.get_begin_klu().idx + 1

    @make_cache
    def get_klc_cnt(self):
        assert self.end_klc.idx == self.get_end_klu().klc.idx
        assert self.begin_klc.idx == self.get_begin_klu().klc.idx
        return self.end_klc.idx - self.begin_klc.idx + 1

    @make_cache
    def _high(self):
        return self.end_klc.high if self.is_up() else self.begin_klc.high

    @make_cache
    def _low(self):
        return self.begin_klc.low if self.is_up() else self.end_klc.low

    @make_cache
    def _mid(self):
        return (self._high() + self._low()) / 2  # 笔的中位价

    @make_cache
    def is_down(self):
        return self.dir == BiDirection.DOWN

    @make_cache
    def is_up(self):
        return self.dir == BiDirection.UP

    def update_virtual_end(self, new_klc: CKLine):
        self._sure_end = self.end_klc
        self.update_new_end(new_klc)
        self._is_sure = False
        self.clean_cache()

    def restore_from_virtual_end(self):
        self._is_sure = True
        assert self.sure_end is not None
        self.update_new_end(new_klc=self.sure_end)
        self._sure_end = None
        self.clean_cache()

    def is_virtual_end(self):
        return self.sure_end is not None

    def update_new_end(self, new_klc: CKLine):
        self._end_klc = new_klc
        self.check()
        self.clean_cache()

    def cal_macd_metric(self, macd_algo, is_reverse):
        if macd_algo == MACDAlgo.AREA:
            return self.cal_macd_half(is_reverse)
        elif macd_algo == MACDAlgo.PEAK:
            return self.cal_macd_peak()
        elif macd_algo == MACDAlgo.FULL_AREA:
            return self.cal_macd_area()
        elif macd_algo == MACDAlgo.DIFF:
            return self.cal_macd_diff()
        elif macd_algo == MACDAlgo.SLOPE:
            return self.cal_macd_slope()
        elif macd_algo == MACDAlgo.AMP:
            return self.cal_macd_amp()
        elif macd_algo == MACDAlgo.AMOUNT:
            return self.cal_macd_trade_metric(DataField.FIELD_TURNOVER, cal_avg=False)
        elif macd_algo == MACDAlgo.VOLUME:
            return self.cal_macd_trade_metric(DataField.FIELD_VOLUME, cal_avg=False)
        elif macd_algo == MACDAlgo.VOLUME_AVG:
            return self.cal_macd_trade_metric(DataField.FIELD_VOLUME, cal_avg=True)
        elif macd_algo == MACDAlgo.AMOUNT_AVG:
            return self.cal_macd_trade_metric(DataField.FIELD_TURNOVER, cal_avg=True)
        elif macd_algo == MACDAlgo.TURNRATE_AVG:
            return self.cal_macd_trade_metric(DataField.FIELD_TURNRATE, cal_avg=True)
        elif macd_algo == MACDAlgo.RSI:
            return self.Cal_Rsi()
        else:
            raise CChanException(f"unsupport macd_algo={macd_algo}, should be one of area/full_area/peak/diff/slope/amp", ErrCode.PARA_ERROR)

    @make_cache
    def Cal_Rsi(self):
        rsi_lst: List[float] = []
        for klc in self.klc_lst:
            rsi_lst.extend(klu.rsi for klu in klc.lst)
        return 10000.0/(min(rsi_lst)+1e-7) if self.is_down() else max(rsi_lst)

    @make_cache
    def cal_macd_area(self):
        _s = 1e-7
        for klc in self.klc_lst:
            for klu in klc.lst:
                _s += abs(klu.macd.macd)
        return _s

    @make_cache
    def cal_macd_peak(self):
        peak = 1e-7
        for klc in self.klc_lst:
            for klu in klc.lst:
                if abs(klu.macd.macd) > peak:
                    if self.is_down() and klu.macd.macd < 0:
                        peak = abs(klu.macd.macd)
                    elif self.is_up() and klu.macd.macd > 0:
                        peak = abs(klu.macd.macd)
        return peak

    def cal_macd_half(self, is_reverse):
        if is_reverse:
            return self.cal_macd_half_reverse()
        else:
            return self.cal_macd_half_obverse()

    @make_cache
    def cal_macd_half_obverse(self):
        _s = 1e-7
        begin_klu = self.get_begin_klu()
        peak_macd = begin_klu.macd.macd
        for klc in self.klc_lst:
            for klu in klc.lst:
                if klu.idx < begin_klu.idx:
                    continue
                if klu.macd.macd*peak_macd > 0:
                    _s += abs(klu.macd.macd)
                else:
                    break
            else:  # 没有被break，继续找写一个KLC
                continue
            break
        return _s

    @make_cache
    def cal_macd_half_reverse(self):
        _s = 1e-7
        begin_klu = self.get_end_klu()
        peak_macd = begin_klu.macd.macd
        for klc in self.klc_lst[::-1]:
            for klu in klc[::-1]:
                if klu.idx > begin_klu.idx:
                    continue
                if klu.macd.macd*peak_macd > 0:
                    _s += abs(klu.macd.macd)
                else:
                    break
            else:  # 没有被break，继续找写一个KLC
                continue
            break
        return _s

    @make_cache
    def cal_macd_diff(self):
        """
        macd红绿柱最大值最小值之差
        """
        _max, _min = float("-inf"), float("inf")
        for klc in self.klc_lst:
            for klu in klc.lst:
                macd = klu.macd.macd
                if macd > _max:
                    _max = macd
                if macd < _min:
                    _min = macd
        return _max-_min

    @make_cache
    def cal_macd_slope(self):
        begin_klu = self.get_begin_klu()
        end_klu = self.get_end_klu()
        if self.is_up():
            return (end_klu.high - begin_klu.low)/end_klu.high/(end_klu.idx - begin_klu.idx + 1)
        else:
            return (begin_klu.high - end_klu.low)/begin_klu.high/(end_klu.idx - begin_klu.idx + 1)

    @make_cache
    def cal_macd_amp(self):
        begin_klu = self.get_begin_klu()
        end_klu = self.get_end_klu()
        if self.is_down():
            return (begin_klu.high-end_klu.low)/begin_klu.high
        else:
            return (end_klu.high-begin_klu.low)/begin_klu.low

    def cal_macd_trade_metric(self, metric: str, cal_avg=False) -> float:
        _s = 0
        for klc in self.klc_lst:
            for klu in klc.lst:
                metric_res = klu.trade_info.metric[metric]
                if metric_res is None:
                    return 0.0
                _s += metric_res
        return _s / self.get_klu_cnt() if cal_avg else _s

    def set_klc_lst(self, lst):
        self._klc_lst = lst
