from enum import Enum
from collections import namedtuple

TaxAmount = namedtuple('TaxAmount', ['amount', 'rate', 'tax'])


class FilingStatus(Enum):
    SINGLE = "single"
    MARRIED_JOINTLY = "married_jointly"
    MARRIED_SEPARATELY = "married_separately"
    HEAD_OF_HOUSEHOLD = "head_of_household"


income_tax_brackets = {
    FilingStatus.SINGLE: [
        (0, 11160, 0.10),
        (11161, 47150, 0.12),
        (47151, 100525, 0.22),
        (100526, 191950, 0.24),
        (191951, 243725, 0.32),
        (243726, 609350, 0.35),
        (609351, float('inf'), 0.37),
    ],
    FilingStatus.MARRIED_JOINTLY: [
        (0, 23200, 0.10),
        (23201, 94300, 0.12),
        (94301, 201050, 0.22),
        (201051, 383900, 0.24),
        (383901, 487450, 0.32),
        (487451, 731200, 0.35),
        (731201, float('inf'), 0.37),
    ],
    FilingStatus.MARRIED_SEPARATELY: [
        (0, 11160, 0.10),
        (11161, 47150, 0.12),
        (47151, 100525, 0.22),
        (100526, 191950, 0.24),
        (191951, 243725, 0.32),
        (243726, 365600, 0.35),
        (365601, float('inf'), 0.37),
    ],
    FilingStatus.HEAD_OF_HOUSEHOLD: [
        (0, 16550, 0.10),
        (16551, 63100, 0.12),
        (63101, 100500, 0.22),
        (100501, 191950, 0.24),
        (191951, 243700, 0.32),
        (243701, 609350, 0.35),
        (609351, float('inf'), 0.37),
    ],
}

ALL_FILING_STATUS = [k.value for k in income_tax_brackets]


class IncomeTax:
    def __init__(self, income, filing_status: FilingStatus, verbose=False):
        self._income = income
        self._filing_status = filing_status
        self.verbose = verbose

    @property
    def income(self):
        return self._income

    @property
    def filing_status(self):
        return self._filing_status

    @property
    def tax_details(self):
        remaining_income = self.income
        tax_amounts = list()
        for lower_bound, upper_bound, rate in income_tax_brackets[self.filing_status]:
            if remaining_income <= 0:
                break

            taxable_in_bracket = min(remaining_income, upper_bound - lower_bound + 1) if upper_bound != float('inf') \
                else remaining_income
            tax_amount = taxable_in_bracket * rate
            remaining_income -= taxable_in_bracket
            tax_amounts.append(TaxAmount(taxable_in_bracket, rate, tax_amount))
            if self.verbose:
                print(f"{taxable_in_bracket:,}\t@{rate*100:.1f}% = ${tax_amount:.2f}")
        return tax_amounts

    @property
    def tax_due(self):
        tax_due = 0
        for ta in self.tax_details:
            tax_due += ta.tax
        return tax_due

    @property
    def average_tax_rate(self):
        return round(self.tax_due/self.income, 3)


def cli():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--income", type=int, default=100000, required=False)
    parser.add_argument("--filing_status", choices=ALL_FILING_STATUS, default=FilingStatus.SINGLE.value)
    parser.add_argument("--verbose", action="store_true", required=False)
    args = parser.parse_args()
    if args.verbose:
        print(args)

    itx = IncomeTax(args.income, FilingStatus(args.filing_status), verbose=args.verbose)
    print(f"Income ${itx.income:,} using filing status '{itx.filing_status}': "
          f"Tax due is ${itx.tax_due:,} and average tax rate: {itx.average_tax_rate*100:.1f}%")


if __name__ == "__main__":
    cli()


