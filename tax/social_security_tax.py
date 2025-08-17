from income_tax import FilingStatus

social_security_tax_brackets = {
    FilingStatus.SINGLE: [
        (0, 25000, 0.0),
        (25001, 34000, 0.5),
        (34000, float('inf'), 0.85)
    ],
    FilingStatus.MARRIED_JOINTLY: [
        (0, 32000, 0.0),
        (32001, 44000, 0.5),
        (44000, float('inf'), 0.85)
    ],
    FilingStatus.MARRIED_SEPARATELY: [
        (0, 25000, 0.0),
        (25001, 34000, 0.5),
        (34000, float('inf'), 0.85)
    ],
    FilingStatus.HEAD_OF_HOUSEHOLD: [
        (0, 25000, 0.0),
        (25001, 34000, 0.5),
        (34000, float('inf'), 0.85)
    ],
}


def calculate_combined_income(adjusted_gross_income=0.0, non_taxable_interest=0.0, social_security_benefit=0.0):
    return round(adjusted_gross_income + non_taxable_interest + 0.5*social_security_benefit, 2)


class SocialSecurityTax:
    def __init__(self, combined_income, filing_status: FilingStatus, verbose=False):
        self._combined_income = combined_income
        self._filing_status = filing_status
        self.verbose = verbose

    @property
    def combined_income(self):
        return self._combined_income

    @property
    def filing_status(self):
        return self._filing_status

    def taxable_percentage(self, digits=1):
        for lower_bound, upper_bound, fraction in social_security_tax_brackets[self.filing_status]:
            if upper_bound >= self.combined_income >= lower_bound:
                if self.verbose:
                    print(f"For combined income ${self.combined_income:,} using filing status '{itx.filing_status}': "
                          f" social security income tax percentage is {fraction * 100:.1f}%")
                return round(fraction, digits)

