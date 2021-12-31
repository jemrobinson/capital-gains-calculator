# capital-gains-calculator

UK capital gains calculator for `Portfolio Performance`

## Prepare your portfolio

This code will categorise transactions based on the following:

- `Buy` transactions will be recorded as `Purchase`s
- `Sell` transactions will be recorded as `Sale`s
- Transactions with a `Note` of "Excess reportable income" will be recorded as `ExcessReportableIncome`
- `Sell` transactions with a `Note` containing "Exchange" will be marked as share splits and must involve the sale of all shares currently in the pool

## Using CSV input

### Prepare a CSV

- Go to `All transactions`
- Click the `Export` icon on the right-hand side
- The following columns are expected:

| Date       | Type | Security  | Shares | Amount  | Fees | Taxes | Cash Account      | ISIN         | Symbol | Note |
| ---------- | ---- | --------- | ------ | ------- | ---- | ----- | ----------------- | ------------ | ------ | ---- |
| 2021-12-31 | Buy  | Tesla Inc | 1      | 1070.44 | 5.00 | 0.00  | Brokerage Account | US88160R1014 | TSLA   |      |

### Analyse a CSV

- Run `./process.py --csv <path to csv> --tax-year <year in form YYYY-YYYY or YYYY-YY> --account-names <space separated account names>`

## Using XML input

- Run `./process.py --xml <path to Portfolio Performance xml> --tax-year <year in form YYYY-YYYY or YYYY-YY> --account-names <space separated account names>`
