from .CEnum import BiDirection, KlineType


def kltype_lt_day(_type):
    return _type in [KlineType.K_1M, KlineType.K_5M, KlineType.K_15M, KlineType.K_30M, KlineType.K_60M]


def kltype_lte_day(_type):
    return _type in [KlineType.K_1M, KlineType.K_5M, KlineType.K_15M, KlineType.K_30M, KlineType.K_60M, KlineType.K_DAY]


def check_kltype_order(type_list: list):
    _dict = {
        KlineType.K_1M: 1,
        KlineType.K_3M: 2,
        KlineType.K_5M: 3,
        KlineType.K_15M: 4,
        KlineType.K_30M: 5,
        KlineType.K_60M: 6,
        KlineType.K_DAY: 7,
        KlineType.K_WEEK: 8,
        KlineType.K_MON: 9,
        KlineType.K_QUARTER: 10,
        KlineType.K_YEAR: 11,
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
