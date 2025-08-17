from enum import Enum
from datetime import datetime


class FREQ(Enum):
    DAY = 1
    WEEK = 7
    BI_WEEK = 14
    MONTH = 30
    QUARTER = 90
    YEAR = 365


def to_freq(days, freq: FREQ, digits=0):
    return round(days/freq.value, digits)


class Age:
    def __init__(self, years=0, months=0, days=0):
        """
        Initializes an Age object with years, months, and days.
        """
        if not all(isinstance(arg, int) and arg >= 0 for arg in [years, months, days]):
            raise ValueError("Years, months, and days must be non-negative integers.")
        self.years = years
        self.months = months
        self.days = days

    def _to_days(self):
        """
        Converts the age to a rough total number of days for comparison purposes.
        This is an approximation and does not account for leap years or varying month lengths precisely.
        """
        return self.years * 365 + self.months * 30 + self.days

    def in_months(self):
        return self.years*12 + self.months

    def __eq__(self, other):
        """
        Compares if two Age objects are equal.
        """
        if not isinstance(other, Age):
            return NotImplemented
        return self.years == other.years and self.months == other.months and self.days == other.days

    def __lt__(self, other):
        """
        Compares if this Age object is less than another.
        """
        if not isinstance(other, Age):
            return NotImplemented
        return self._to_days() < other._to_days()

    def __le__(self, other):
        """
        Compares if this Age object is less than or equal to another.
        """
        if not isinstance(other, Age):
            return NotImplemented
        return self._to_days() <= other._to_days()

    def __gt__(self, other):
        """
        Compares if this Age object is greater than another.
        """
        if not isinstance(other, Age):
            return NotImplemented
        return self._to_days() > other._to_days()

    def __ge__(self, other):
        """
        Compares if this Age object is greater than or equal to another.
        """
        if not isinstance(other, Age):
            return NotImplemented
        return self._to_days() >= other._to_days()

    def __sub__(self, other):
        """
        Computes the approximate difference between two Age objects.
        Returns a new Age object representing the difference.
        """
        if not isinstance(other, Age):
            raise TypeError("Can only subtract Age objects from other Age objects.")

        total_days_self = self._to_days()
        total_days_other = other._to_days()
        difference_days = abs(total_days_self - total_days_other)

        # Convert back to years, months, and days (approximate)
        diff_years = difference_days // 365
        remaining_days = difference_days % 365
        diff_months = remaining_days // 30
        diff_days = remaining_days % 30

        return Age(diff_years, diff_months, diff_days)

    def __str__(self):
        """
        Returns a string representation of the Age object.
        """
        return f"{self.years} years, {self.months} months, {self.days} days"

    def __repr__(self):
        """
        Returns a developer-friendly string representation of the Age object.
        """
        return f"Age(years={self.years}, months={self.months}, days={self.days})"


delta = Age(67, 0, 0) - Age(63, 6, 12)
print(delta)