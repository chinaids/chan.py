import pytest
# from Common.CTime import CTime
from kline.klinemerger import KLineMerger
from schema.ctime import CTime
from schema.klineunit import KLineUnit
from schema.mergedkline import MergedKLineUnit, MergedKLine


class TestKLineMerger:

    def test_clear_merged_cache(self):
        b_time1 = CTime(year=2023, month=12, day=30)
        b_time2 = CTime(year=2023, month=12, day=31)
        kline1 = KLineUnit(time=b_time1, open=1, close=2, high=3, low=0)
        kline2 = KLineUnit(time=b_time2, open=1, close=2, high=3, low=1)
        merged = MergedKLineUnit(elements=[kline1, kline2], direction='up')

        assert merged.high == 3.0

        kline3 = KLineUnit(time=b_time2, open=1, close=2, high=4, low=1)
        merged.elements.append(kline3)

        assert merged.high == 3.0

        KLineMerger.clear_merged_cache(merged)

        assert merged.high == 4.0
