import pytest
import pandas as pd

from kline.klinemerger import KLineMerger
from schema.ctime import CTime
from schema.klineunit import KLineUnit
from schema.mergedkline import MergedKLineUnit, MergedKLine

from Common.CEnum import FenxingType, KLineDir


@pytest.fixture()
def k_lines():
    data_path = 'test/data/kline_100days.csv'
    data = pd.read_csv(data_path, index_col=0)
    klines = []
    for idx, row in data.iterrows():
        date = [int(d) for d in row['date'].split('-')]
        t = CTime(year=date[0], month=date[1], day=date[2])
        kline = KLineUnit(time=t, open=row['open'], close=row['close'],
                          high=row['high'], low=row['low'])
        klines.append(kline)

    return klines


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

    def test_check_merge(self):
        b_time1 = CTime(year=2023, month=12, day=30)
        b_time2 = CTime(year=2023, month=12, day=31)
        kline1 = KLineUnit(time=b_time1, open=6, close=7, high=8, low=5)
        kline2 = KLineUnit(time=b_time2, open=10, close=9, high=10, low=9)
        merged = MergedKLineUnit(elements=[kline1, kline2], direction='up')

        merger = KLineMerger()

        kline3 = KLineUnit(time=b_time2, open=1, close=2, high=4, low=0)
        direction = merger.check_merge(kline3, merged)
        assert direction == KLineDir.DOWN

        kline3 = KLineUnit(time=b_time2, open=12, close=13, high=13, low=12)
        direction = merger.check_merge(kline3, merged)
        assert direction == KLineDir.UP

    def test_update_fx(self):
        b_time1 = CTime(year=2023, month=12, day=30)
        b_time2 = CTime(year=2023, month=12, day=31)
        kline1 = KLineUnit(time=b_time1, open=6, close=7, high=8, low=5)
        kline2 = KLineUnit(time=b_time2, open=10, close=9, high=10, low=9)
        merged1 = MergedKLineUnit(elements=[kline1], direction='up')
        merged2 = MergedKLineUnit(elements=[kline2], direction='up')

        kline3 = KLineUnit(time=b_time2, open=1, close=2, high=4, low=0)
        merged3 = MergedKLineUnit(elements=[kline3], direction='up')

        merger = KLineMerger()

        merger.update_fx(merged1, merged2, merged3)
        assert merged2.fenxing == FenxingType.TOP

        merged2 = MergedKLineUnit(elements=[kline2], direction='up')
        kline3 = KLineUnit(time=b_time2, open=12, close=13, high=13, low=12)
        merged3 = MergedKLineUnit(elements=[kline3], direction='up')
        merger.update_fx(merged1, merged2, merged3)
        assert merged2.fenxing == FenxingType.UNKNOWN

        merged1 = MergedKLineUnit(elements=[kline3], direction='up')
        merged2 = MergedKLineUnit(elements=[kline2], direction='up')
        merged3 = MergedKLineUnit(elements=[kline3], direction='up')
        merger.update_fx(merged1, merged2, merged3)
        assert merged2.fenxing == FenxingType.BOTTOM

    def test_merge_klineunits(self, k_lines):

        merger = KLineMerger()
        merged = merger.merge_klineunits(k_lines)

        merged_elements = [len(m.elements) for m in merged]
        # print('total elements:', len(k_lines), sum(merged_elements))
        assert len(k_lines) == sum(merged_elements)

        # merged_dates = []
        for pre_m, m in zip(merged[:-1], merged[1:]):
            if m.direction == KLineDir.UP:
                print(pre_m.direction, pre_m.begin_time, pre_m.high)
                print(m.begin_time, m.high)
                print('-'*20)
                # break
            # merged_dates.extend([str(e.time) for e in m.elements])
            # if len(m.elements) > 1:
            #     print(m.high, m.low, m.direction)
            #     inside = [(e.time, e.high, e.low, e.open, e.close) for e in m.elements]
            #     print('merged: ', len(m.elements))
            #     for i in inside:
            #         print(i)
            #     print('-'*20)
            # else:
            #     print('single:', m.elements[0].time, m.high, m.low, m.direction)
            #     print('=' * 20)
            # break
        # from collections import Counter
        # print(Counter(merged_dates).most_common(2))