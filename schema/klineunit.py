from pydantic import BaseModel, model_validator
from typing import Literal, Optional

from schema.ctime import CTime


class KLineUnit(BaseModel):
    _idx: int = -1
    time: CTime
    open: float
    close: float
    high: float
    low: float
    volume: Optional[float] = None
    turnover: Optional[float] = None  # 交易量
    limit_flag: Literal['normal', 'up_limit', 'down_limit', 'suspended'] = 'normal'

    @model_validator(mode='after')
    def verify_price(self):
        assert self.low <= min([self.low, self.open, self.high, self.close]), 'price low not lowest'
        assert self.high >= min([self.low, self.open, self.high, self.close]), 'price high not highest'
        return self
