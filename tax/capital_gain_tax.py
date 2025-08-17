from typing import List
from enum import Enum
from collections import deque, namedtuple
from datetime import datetime
from income_tax import IncomeTax, FilingStatus, income_tax_brackets


class Operation(Enum):
    BUY = "buy"
    SELL = "sell"


# Read-only
Transaction = namedtuple('Transaction', ['date', 'operation', 'quantity', 'price'])


class UpdatableTransaction:
    def __init__(self, t:Transaction):
        self.date = t.date
        self.operation = t.operation
        self.quantity = t.quantity
        self.price = t.price


long_term_tax_brackets = {
    FilingStatus.SINGLE: [
        (0, 48350, 0.0),
        (48351, 533400, 0.15),
        (533401, float('inf'), 0.20),
    ],
    FilingStatus.MARRIED_JOINTLY: [
        (0, 97600, 0.0),
        (96701, 600500, 0.15),
        (600501, float('inf'), 0.20),
    ],
    FilingStatus.MARRIED_SEPARATELY: [
        (0, 48350, 0.0),
        (48351, 300000, 0.15),
        (300001, float('inf'), 0.20),
    ],
    FilingStatus.HEAD_OF_HOUSEHOLD: [
        (0, 63000, 0.0),
        (63001, 535130, 0.15),
        (535351, float('inf'), 0.20),
    ],
}


def niit_rate(income, filing_status: FilingStatus):
    if ((filing_status == FilingStatus.SINGLE and income > 200000) or
        (filing_status == FilingStatus.MARRIED_JOINTLY and income > 250000) or
        (filing_status == FilingStatus.MARRIED_SEPARATELY and income > 125000) or
        (filing_status == FilingStatus.HEAD_OF_HOUSEHOLD and income > 200000)
    ):
        return 0.0038
    else:
        return 0.0


def get_long_term_rate(income, filing_status: FilingStatus):
    for lower_bound, upper_bound, rate in long_term_tax_brackets[filing_status]:
        if upper_bound >= income >= lower_bound:
            return rate
    raise RuntimeError(f"No long-term tax bracket found for income=${income:,}, filing_status={filing_status}")


def get_short_term_rate(income, filing_status: FilingStatus):
    for lower_bound, upper_bound, rate in income_tax_brackets[filing_status]:
        if upper_bound >= income >= lower_bound:
            return rate
    raise RuntimeError(f"No short-term tax bracket found for income=${income:,}, filing_status={filing_status}")


class CapitalGainTax:
    def __init__(self, tr_list: List[Transaction], verbose=False):
        self._transactions = tr_list
        self.verbose = verbose

    @property
    def transactions(self):
        return [UpdatableTransaction(t) for t in self._transactions]

    def calculate_fifo_capital_gains(self):
        _buys = [t for t in self.transactions if t.operation == Operation.BUY]
        _sales = [t for t in self.transactions if t.operation == Operation.SELL]
        _gains_and_losses = list()
        # sort purchases by date
        purchase_queue = deque(sorted(_buys, key=lambda x: x.date))
        for sale in sorted(_sales, key=lambda x: x.date):
            remaining_sale_quantity = sale.quantity
            while remaining_sale_quantity > 0 and  purchase_queue:
                oldest_purchase = purchase_queue.popleft()
                matched_quantity = min(remaining_sale_quantity, oldest_purchase.quantity)
                cost_basis = matched_quantity * oldest_purchase.price
                sale_proceeds = matched_quantity * sale.price
                gain_or_loss = sale_proceeds - cost_basis

                holding_period = (sale.date - oldest_purchase.date).days
                if holding_period > 365:
                    gain_type = "long-term"
                else:
                    gain_type = "short-term"

                _gains_and_losses.append({"sale_date": sale.date, "purchase_date": oldest_purchase.date,
                                          "quantity": matched_quantity, "cost_basis": cost_basis,
                                          "sale_proceeds": sale_proceeds, "gain_loss": gain_or_loss,
                                          "tax_type": gain_type})
                remaining_sale_quantity -= matched_quantity
                if oldest_purchase.quantity > matched_quantity: # if purchase is not fully used
                    oldest_purchase.quantity -= matched_quantity
                    purchase_queue.appendleft(oldest_purchase) # put the remain portion back

        return _gains_and_losses

    def tax_due(self, itx: IncomeTax):
        my_niit_rate = niit_rate(itx.income, itx.filing_status)
        gains_and_losses = self.calculate_fifo_capital_gains()
        short_term_gain_loss = 0
        long_term_gain_loss = 0
        for gl in gains_and_losses:
            if gl['tax_type'] == "long-term":
                long_term_gain_loss += gl['gain_loss']
            else:
                # gl['tax_type'] == "short-term"
                short_term_gain_loss += gl['gain_loss']

        long_term_rate = get_long_term_rate(itx.income, itx.filing_status)
        short_term_rate = get_short_term_rate(itx.income, itx.filing_status)

        if self.verbose:
            print("Gains Losses Details:")
            for gl in gains_and_losses:
                print(gl)
            print(f"long_term_gain_loss = ${long_term_gain_loss:,}")
            print(f"long_term_rate = {long_term_rate*100:.1f}%")
            print(f"NIIT rate = {my_niit_rate*100:.1f}%")
            print(f"short_term_gain_loss = ${short_term_gain_loss:,}")
            print(f"short_term_rate = ${short_term_rate*100:.1f}%")

        tax_owed = 0
        if long_term_gain_loss > 0:
            rate = long_term_rate + my_niit_rate
            tax_owed += long_term_gain_loss * rate
        else:
            # it is a loss, offset short-term gain
            short_term_gain_loss += long_term_gain_loss

        if short_term_gain_loss > 0:
            tax_owed += short_term_gain_loss * short_term_rate
        elif short_term_gain_loss < 0:
            tax_owed = max(-3000, short_term_gain_loss)
            if short_term_gain_loss < -3000:
                print(f"short-term loss carry-over: {short_term_gain_loss + 3000:,}", file=sys.stderr)
        return round(tax_owed, 2)


def unit_test():
    transactions = list()
    purchases = [
        Transaction(datetime(2023, 1, 15), Operation.BUY, 100, 20.00),
        Transaction(datetime(2023, 3, 10), Operation.BUY, 50, 22.00),
        Transaction(datetime(2024, 2, 5), Operation.BUY, 75, 25.00),
    ]
    transactions.extend(purchases)
    sales = [
        Transaction(datetime(2024, 1, 20), Operation.SELL, 80, 28.00),
        Transaction(datetime(2024, 7, 1), Operation.SELL, 50, 30.00),
    ]
    transactions.extend(sales)
    print(f"There are {len(transactions)} transactions")
    cap_gain = CapitalGainTax(transactions, verbose=True)
    results = cap_gain.calculate_fifo_capital_gains()
    for r in results:
        print(r)
    print("-"*80)
    itx = IncomeTax(income=100000, filing_status=FilingStatus.MARRIED_JOINTLY)
    print(f"Tax due = ${cap_gain.tax_due(itx):.2f}")


if __name__ == "__main__":
    unit_test()
