from apps.up_client import AuthenticationError, UpClient

up = UpClient()

try:
    up.ping()
    print("Token OK")

    # accounts = up.list_accounts()
    # print(f"found {len(accounts)} accounts")

    # for account in accounts:
    #     attrs = account.attributes
    #     dollars = attrs.balance.value_in_base_units / 100
    #     print(f"{attrs.display_name} ({attrs.account_type}): ${dollars:,.2f}")

    # categories = up.list_categories()
    # print(categories)

    transactions = up.list_transactions()
    print(transactions)
    
except AuthenticationError:
    print("token rejected: check validity of UpBank API token")

finally:
    up.close()