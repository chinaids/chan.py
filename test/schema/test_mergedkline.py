from schema.ctime import CTime
from schema.klineunit import KLineUnit
from schema.mergedkline import MergedKLineUnit, MergedKLine


class TestKLineMerger:

    def test_get_peak_klu(self):
        b_time1 = CTime(year=2023, month=12, day=28)
        b_time2 = CTime(year=2023, month=12, day=29)
        b_time3 = CTime(year=2023, month=12, day=30)
        kline1 = KLineUnit(time=b_time1, open=1, close=2, high=3, low=0)
        kline2 = KLineUnit(time=b_time2, open=1, close=2, high=3, low=1)
        kline3 = KLineUnit(time=b_time3, open=1, close=2, high=4, low=1)
        merged = MergedKLineUnit(elements=[kline1, kline2, kline3], direction='up')

        klu = merged.get_peak_klu(True)
        assert klu.high == 4.0

        merged = MergedKLineUnit(elements=[kline1, kline2, kline3], direction='down')
        klu = merged.get_peak_klu(False)
        assert klu.low == 0.0
