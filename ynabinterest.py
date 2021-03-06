import json
import requests
import datetime
import calendar
import argparse

GET = "GET"
POST = "POST"
BASEURL = "https://api.youneedabudget.com/v1"
BUDGETS = {}
TOKEN = ""
DEFAULT_PAYEE = "Interest"


def request(method, endpoint, params=None):
    response = requests.request(method, "{}{}".format(BASEURL, endpoint), json=params,
                                headers={'Authorization': 'Bearer {}'.format(TOKEN)})
    if response.status_code != 200:
        pass  # TODO: raise exception?
    return response.json()


def days_in_year():
    return 366.0 if calendar.isleap(datetime.datetime.now().year) else 365.0


def calculate_amount(account_data, rate, schedule):
    balance = account_data['balance']/1000.0
    period_interest = (rate/100.0)/(12 if schedule else days_in_year())
    return balance * period_interest


def get_transaction(account_data, amount, transaction_date, payee_name):
    milliamount = int(amount * 1000.0)
    return {
        "account_id": account_data['id'],
        "date": transaction_date,
        "amount": milliamount,
        "payee_id": None,
        "payee_name": payee_name,
        "category_id": None,
        "memo": "Entered automatically by YNABInterestAdder",
        "cleared": "uncleared",
        "approved": True,
        "flag_color": None,
        "import_id": "YNAB:{}:{}:1".format(milliamount, transaction_date)
    }


def is_last_day_of_month():
    now = datetime.datetime.now()
    year, month = now.year, now.month
    return calendar.monthrange(year, month)[1] == now.day


def process_budget(budget, transaction_date):
    transactions = []
    budgetid = BUDGETS[budget.get("name")]
    account_map = {account['name']: account for account in request(GET, '/budgets/{}/accounts'.format(budgetid))['data']['accounts']}
    for account in budget['accounts']:
        name, rate, schedule, payee = account['name'], account['rate'], account['schedule'], account.get("payee", DEFAULT_PAYEE)
        if not schedule or schedule == datetime.datetime.now().day or (schedule == -1 and is_last_day_of_month()):
            account_data = account_map[name]
            amount = calculate_amount(account_data, rate, schedule)
            transactions.append(get_transaction(account_data, amount, transaction_date, payee_name=payee))
    submit_transactions(budgetid, transactions)


def get_budget_map():
    return {budget['name']: budget['id'] for budget in request(GET, "/budgets")['data']['budgets']}


def submit_transactions(budgetid, transactions):
    data = {"transactions": transactions}
    response = request(POST, "/budgets/{}/transactions/bulk".format(budgetid), params=data)


def main():
    global TOKEN, BUDGETS
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json",
                        help="path to config.json file")
    parser.add_argument("--date", default=datetime.datetime.now().strftime("%Y-%m-%d"),
                        help="date to enter transactions for (YYYY-MM-DD)")
    args = parser.parse_args()
    config = None
    with open(args.config, "r") as cfgfile:
        config = json.load(cfgfile)
    transaction_date = args.date
    TOKEN = config.get("apitoken")
    BUDGETS = get_budget_map()
    for budget in config.get("budgets"):
        process_budget(budget, transaction_date)


if __name__ == "__main__":
    main()
