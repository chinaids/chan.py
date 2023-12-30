import datetime
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Union

from

from BuySellPoint.BuySellPoint import CBuySellPoint
from chanconfig import CChanConfig
from Common.CEnum import AdjustmentType, DataSrc, KLineType
from Common.ChanException import CChanException, ErrCode
from Common.CTime import CTime
from Common.func_util import check_kltype_order, kltype_lte_day
from DataAPI.CommonStockAPI import CCommonStockApi
from kline.klinelist import KLineList
from kline.klineunit import KLineUnit


class DataLoader:
    """
    load data from file/data source
    return a list of k line for each specified level
    if begin_time or end_time is specified, return data between them
    """

    def __init__(self, begin_time=None, end_time=None, #config=None,
                 # lv_list=None,
                 # adjustment: AdjustmentType = AdjustmentType.QFQ,
                 # data_src: Union[DataSrc, str] = DataSrc.BAO_STOCK,
                 ):
        # if lv_list is None:
        #     lv_list = [KLineType.K_DAY, KLineType.K_60M]
        # check_kltype_order(lv_list)  # lv_list顺序从高到低
        # self.code = code
        self.begin_time = str(begin_time) if isinstance(begin_time, datetime.date) else begin_time
        self.end_time = str(end_time) if isinstance(end_time, datetime.date) else end_time
        # self.adjustment = adjustment
        # self.data_src = data_src
        # self.lv_list: List[KLineType] = lv_list

        # if config is None:
        #     config = CChanConfig()
        # self.conf = config
        #
        # self.kl_misaligned_cnt = 0
        # self.kl_inconsistent_detail = defaultdict(list)
        #
        # self.g_kl_iter = defaultdict(list)
        #
        # self.kl_datas: Dict[KLineType, CKLine_List] = None
        # self.klu_cache: List[Optional[CKLineUnit]] = None
        # self.klu_last_t = None

        # self.do_init()

        # if not config.trigger_step:
        #     for _ in self.load():
        #         ...

    def load_from_file(self):



        return

    def load_from_source(self):
        return

