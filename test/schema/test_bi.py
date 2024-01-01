import pytest

from kline.klinemerger import KLineMerger
from schema.ctime import CTime
from schema.klineunit import KLineUnit
from schema.mergedkline import MergedKLineUnit
from schema.bi import Bi

from Common.CEnum import FenxingType, KLineDir


class TestBi:

    def test_bi(self):
        b_time1 = CTime(year=2023, month=12, day=30)
        b_time2 = CTime(year=2023, month=12, day=31)
        kline1 = KLineUnit(time=b_time1, open=10, close=20, high=30, low=9)
        kline2 = KLineUnit(time=b_time2, open=1, close=2, high=3, low=1)
        merged1 = MergedKLineUnit(elements=[kline1], direction='up', fenxing='top')
        merged2 = MergedKLineUnit(elements=[kline2], direction='up', fenxing='bottom')

        assert Bi(beg_unit=merged1, end_unit=merged2)
