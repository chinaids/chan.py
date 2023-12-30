from .CEnum import BiDirection, KLineType


def kltype_lt_day(_type):
    return _type in [KLineType.K_1M, KLineType.K_5M, KLineType.K_15M, KLineType.K_30M, KLineType.K_60M]


def kltype_lte_day(_type):
    return _type in [KLineType.K_1M, KLineType.K_5M, KLineType.K_15M, KLineType.K_30M, KLineType.K_60M, KLineType.K_DAY]


def check_kltype_order(type_list: list):
    _dict = {
        KLineType.K_1M: 1,
        KLineType.K_3M: 2,
        KLineType.K_5M: 3,
        KLineType.K_15M: 4,
        KLineType.K_30M: 5,
        KLineType.K_60M: 6,
        KLineType.K_DAY: 7,
        KLineType.K_WEEK: 8,
        KLineType.K_MON: 9,
        KLineType.K_QUARTER: 10,
        KLineType.K_YEAR: 11,
    }
    last_lv = float("inf")
    for kl_type in type_list:
        cur_lv = _dict[kl_type]
        assert cur_lv < last_lv, "lv_list的顺序必须从大级别到小级别"
        last_lv = cur_lv


def revert_bi_dir(dir):
    return BiDirection.DOWN if dir == BiDirection.UP else BiDirection.UP


def has_overlap(l1, h1, l2, h2, equal=False):
    return h2 >= l1 and h1 >= l2 if equal else h2 > l1 and h1 > l2


def str2float(s):
    try:
        return float(s)
    except ValueError:
        return 0.0


def _parse_inf(v):
    if type(v) == float:
        if v == float("inf"):
            v = 'float("inf")'
        if v == float("-inf"):
            v = 'float("-inf")'
    return v
