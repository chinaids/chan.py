from functools import cached_property
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CTime(BaseModel):
    year: int
    month: int
    day: int
    hour: Optional[int] = 0
    minute: Optional[int] = 0
    second: Optional[int] = 0
    auto: bool = True  # 自适应对天的理解

    # set_timestamp()  # set ts

    # def __init__(self, year: int, month, day, hour=0, minute=0, second=0, auto=True):
    #     year = year
    #     month = month
    #     day = day
    #     hour = hour
    #     minute = minute
    #     second = second
    #     auto = auto  # 自适应对天的理解
    #     set_timestamp()  # set ts
    #

    @cached_property
    def string(self):
        if self.hour == 0 and self.minute == 0:
            return f"{self.year:04}/{self.month:02}/{self.day:02}"
        else:
            return f"{self.year:04}/{self.month:02}/{self.day:02} {self.hour:02}:{self.minute:02}"

    # def toDateStr(self, splt=''):
    #     return f"{year:04}{splt}{month:02}{splt}{day:02}"
    #
    @cached_property
    def date(self):
        if self.hour == 0 and self.minute == 0 and self.auto:
            date = datetime(self.year, self.month, self.day, 23, 59, self.second)
        else:
            date = datetime(self.year, self.month, self.day, self.hour, self.minute, self.second)
        return date
    # 
    # def set_timestamp(self):
    #     if hour == 0 and minute == 0 and auto:
    #         date = datetime(year, month, day, 23, 59, second)
    #     else:
    #         date = datetime(year, month, day, hour, minute, second)
    #     ts = date.timestamp()
    # 
    # def __gt__(self, t2):
    #     return ts > t2.ts
    # 
    # def __ge__(self, t2):
    #     return ts >= t2.ts
