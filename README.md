# capital-gains-calculator
UK capital gains calculator for Portfolio Performance

## Prepare your portfolio
This code will categorise transactions based on the following:

- `Buy` transactions will be recorded as `Purchase`s
- `Sell` transactions will be recorded as `Sale`s
- Transactions with a `Note` of "Excess reportable income" will be recorded as `ExcessReportableIncome`
- `Sell` transactions with a `Note` containing "Exchange" will be marked as share splits and must involve the sale of all shares currently in the pool

## Generate CSV input
- Go to `All transactions`
- Click the `Export` icon on the right-hand side

## Analyse CSV
- Run `./process.py --csv <path to csv> --tax-year <year in form YYYY-YYYY or YYYY-YY> --account-names <comma separated account names>`