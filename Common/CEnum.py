from enum import Enum, auto
from typing import Literal


class DataSrc(Enum):
    BAO_STOCK = 'bao_stock'
    CCXT = 'ccxt'  # crypto
    CSV = 'csv'


class KLineType(Enum):
    K_1M = '1m'
    K_DAY = 'day'
    K_WEEK = 'week'
    K_MON = 'month'
    K_YEAR = 'year'
    K_5M = '5m'
    K_15M = '15m'
    K_30M = '30m'
    K_60M = '60m'
    K_3M = '3m'
    K_QUARTER = 'quarter'


class KLineDir(Enum):
    UP = 'up'
    DOWN = 'down'
    COMBINE = 'combine'
    INCLUDED = 'included'


class FenxingType(Enum):
    BOTTOM = auto()
    TOP = auto()
    UNKNOWN = auto()


class BiDirection(Enum):
    UP = 'up'
    DOWN = 'down'


class BiType(Enum):
    UNKNOWN = auto()
    STRICT = auto()
    SUB_VALUE = auto()  # 次高低点成笔
    TIAOKONG_THRED = auto()
    DAHENG = auto()
    TUIBI = auto()
    UNSTRICT = auto()
    TIAOKONG_VALUE = auto()


BSP_MAIN_TYPE = Literal['1', '2', '3']


class BuySellPointType(Enum):
    T1 = '1'
    T1P = '1p'
    T2 = '2'
    T2S = '2s'
    T3A = '3a'  # 中枢在1类后面
    T3B = '3b'  # 中枢在1类前面

    def main_type(self) -> BSP_MAIN_TYPE:
        return self.value[0]  # type: ignore


class AdjustmentType(Enum):
    QFQ = auto()  # 前复权
    HFQ = auto()  # 后复权
    NONE = auto()  # 不复权


class TrendType(Enum):
    MEAN = "mean"
    MAX = "max"
    MIN = "min"


class TrendLineScope(Enum):
    INSIDE = 'inside'
    OUTSIDE = 'outside'


class LeftSegMethod(Enum):
    ALL = auto()
    PEAK = auto()


class FenxingCheckMethod(Enum):
    STRICT = auto()
    LOSS = auto()
    HALF = auto()
    TOTALLY = auto()


class SegType(Enum):
    BI = 'bi'
    SEG = 'seg'


class MACDAlgo(Enum):
    AREA = auto()
    PEAK = auto()
    FULL_AREA = auto()
    DIFF = auto()
    SLOPE = auto()
    AMP = auto()
    VOLUME = auto()
    AMOUNT = auto()
    VOLUME_AVG = auto()
    AMOUNT_AVG = auto()
    TURNRATE_AVG = auto()
    RSI = auto()


class DATA_FIELD:
    FIELD_TIME = "time_key"
    FIELD_OPEN = "open"
    FIELD_HIGH = "high"
    FIELD_LOW = "low"
    FIELD_CLOSE = "close"
    FIELD_VOLUME = "volume"  # 成交量
    FIELD_TURNOVER = "turnover"  # 成交额
    FIELD_TURNRATE = "turnover_rate"  # 换手率


TRADE_INFO_LST = [DATA_FIELD.FIELD_VOLUME, DATA_FIELD.FIELD_TURNOVER, DATA_FIELD.FIELD_TURNRATE]
