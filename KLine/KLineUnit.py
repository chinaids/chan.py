import copy
from typing import Dict, Optional

from KLine.KLine import CKLine
from Common.CEnum import DataField, TRADE_INFO_LST, TrendType
from Common.ChanException import CChanException, ErrCode
from Common.CTime import CTime
from Math.BOLL import BOLL_Metric, BollModel
from Math.Demark import CDemarkEngine, CDemarkIndex
from Math.KDJ import KDJ
from Math.MACD import CMACD, CMACD_item
from Math.RSI import RSI
from Math.TrendModel import CTrendModel

from .TradeInfo import CTradeInfo


class CKLineUnit:
    def __init__(self, kl_dict, autofix=False):
        # _time, _close, _open, _high, _low, _extra_info={}
        self.__idx = -1
        self.kl_type = None
        self.time: CTime = kl_dict[DataField.FIELD_TIME]
        self.close = kl_dict[DataField.FIELD_CLOSE]
        self.open = kl_dict[DataField.FIELD_OPEN]
        self.high = kl_dict[DataField.FIELD_HIGH]
        self.low = kl_dict[DataField.FIELD_LOW]
        self.volume = kl_dict[DataField.FIELD_VOLUME] if DataField.FIELD_VOLUME in kl_dict else None
        self.turnover = kl_dict[DataField.FIELD_TURNOVER] if DataField.FIELD_TURNOVER in kl_dict else None

        self.check(autofix)

        self.trade_info = CTradeInfo(kl_dict)

        self.demark: CDemarkIndex = CDemarkIndex()

        self.sub_kl_list = []  # 次级别KLU列表
        self.sup_kl: Optional[CKLineUnit] = None  # 指向更高级别KLU

        self._klc: Optional[CKLine] = None  # 指向KLine

        # self.macd: Optional[CMACD_item] = None
        # self.boll: Optional[BOLL_Metric] = None
        self.trend: Dict[TrendType, Dict[int, float]] = {}  # int -> float

        self.limit_flag = 0  # 0:普通 -1:跌停，1:涨停

        # self.set_idx(-1)

    def __deepcopy__(self, memo):
        _dict = {
            DataField.FIELD_TIME: self.time,
            DataField.FIELD_CLOSE: self.close,
            DataField.FIELD_OPEN: self.open,
            DataField.FIELD_HIGH: self.high,
            DataField.FIELD_LOW: self.low,
        }
        for metric in TRADE_INFO_LST:
            if metric in self.trade_info.metric:
                _dict[metric] = self.trade_info.metric[metric]
        obj = CKLineUnit(_dict)
        obj.demark = copy.deepcopy(self.demark, memo)
        obj.trend = copy.deepcopy(self.trend, memo)
        obj.limit_flag = self.limit_flag
        # obj.macd = copy.deepcopy(self.macd, memo)
        # obj.boll = copy.deepcopy(self.boll, memo)
        if hasattr(self, "rsi"):
            obj.rsi = copy.deepcopy(self.rsi, memo)
        if hasattr(self, "kdj"):
            obj.kdj = copy.deepcopy(self.kdj, memo)
        obj.set_idx(self.idx)
        memo[id(self)] = obj
        return obj

    @property
    def klc(self):
        assert self._klc is not None
        return self._klc

    def set_klc(self, klc):
        self._klc = klc

    @property
    def idx(self):
        return self.__idx

    def set_idx(self, idx):
        self.__idx: int = idx

    def __str__(self):
        return f"{self.idx}:{self.time}/{self.kl_type} open={self.open} close={self.close} high={self.high} low={self.low} {self.trade_info}"

    def check(self, autofix=False):
        if self.low > min([self.low, self.open, self.high, self.close]):
            if autofix:
                self.low = min([self.low, self.open, self.high, self.close])
            else:
                raise CChanException(f"{self.time} low price={self.low} is not min of [low={self.low}, open={self.open}, high={self.high}, close={self.close}]", ErrCode.KL_DATA_INVALID)
        if self.high < max([self.low, self.open, self.high, self.close]):
            if autofix:
                self.high = max([self.low, self.open, self.high, self.close])
            else:
                raise CChanException(f"{self.time} high price={self.high} is not max of [low={self.low}, open={self.open}, high={self.high}, close={self.close}]", ErrCode.KL_DATA_INVALID)

    def add_children(self, child):
        self.sub_kl_list.append(child)

    def set_parent(self, parent: 'CKLineUnit'):
        self.sup_kl = parent

    def get_children(self):
        yield from self.sub_kl_list

    def _low(self):
        return self.low

    def _high(self):
        return self.high

    def set_metric(self, metric_model_lst: list) -> None:
        for metric_model in metric_model_lst:
            if isinstance(metric_model, CMACD):
                self.macd: CMACD_item = metric_model.add(self.close)
            elif isinstance(metric_model, CTrendModel):
                if metric_model.type not in self.trend:
                    self.trend[metric_model.type] = {}
                self.trend[metric_model.type][metric_model.T] = metric_model.add(self.close)
            elif isinstance(metric_model, BollModel):
                self.boll: BOLL_Metric = metric_model.add(self.close)
            elif isinstance(metric_model, CDemarkEngine):
                self.demark = metric_model.update(idx=self.idx, close=self.close, high=self.high, low=self.low)
            elif isinstance(metric_model, RSI):
                self.rsi = metric_model.add(self.close)
            elif isinstance(metric_model, KDJ):
                self.kdj = metric_model.add(self.high, self.low, self.close)

    def get_parent_klc(self):
        assert self.sup_kl is not None
        return self.sup_kl.klc
