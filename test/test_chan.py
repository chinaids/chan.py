import pytest
from chan.chan import CChan
from chan.chanconfig import CChanConfig
from Common.CEnum import AdjustmentType, DataSrc, KLineType


class TestChan:

    def test_main(self):
        code = "sz.002466"
        begin_time = "2018-01-01"
        end_time = None
        data_src = DataSrc.BAO_STOCK
        lv_list = [KLineType.K_DAY]

        config = CChanConfig({
            "bi_strict": True,
            "trigger_step": False,
            "skip_step": 0,
            "divergence_rate": float("inf"),
            "bsp2_follow_1": False,
            "bsp3_follow_1": False,
            "min_zs_cnt": 0,
            "bs1_peak": False,
            "macd_algo": "peak",
            "bs_type": '1,2,3a,1p,2s,3b',
            "print_warning": True,
            "zs_algo": "normal",
        })

        chan = CChan(
            code=code,
            begin_time=begin_time,
            end_time=end_time,
            data_src=data_src,
            lv_list=lv_list,
            config=config,
            adjustment=AdjustmentType.QFQ,
        )
