# YNABInterestAdder
Adds interest transactions to accounts in YNAB

## Requirements
- Python 2.7
- [Requests](http://docs.python-requests.org/en/latest/)

## Sample Configuration
```
{
    "apitoken": "enter-your-token-here",
    "budgets": [
        {
            "name": "My Budget",
            "accounts": [
                {
                    "name": "Loan A",
                    "rate": 4.25,
                    "schedule": 15
                },
                {
                    "name": "Loan B",
                    "rate": 5.16,
                    "schedule": 0
                },
                {
                    "name": "Loan C",
                    "rate": 5.49,
                    "schedule": 1
                }
            ]
        }
    ]
}
```
* apitoken: Your [YNAB API token](https://app.youneedabudget.com/settings/developer)
* schedule: int value using either
    * Calendar day
    * 0 to run every day
    * -1 for last day of month