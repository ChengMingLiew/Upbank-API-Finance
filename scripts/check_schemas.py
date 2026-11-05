from apps.schemas import AccountsPage

sample = """
{
  "data": [
    {
      "type": "accounts",
      "id": "e7d94d11-198f-48e9-bde7-c79042969595",
      "attributes": {
        "displayName": "Spending",
        "accountType": "TRANSACTIONAL",
        "ownershipType": "INDIVIDUAL",
        "balance": {
          "currencyCode": "AUD",
          "value": "1.00",
          "valueInBaseUnits": 100
        },
        "createdAt": "2024-09-20T13:14:06+10:00"
      },
      "relationships": {
        "transactions": {
          "links": {
            "related": "https://api.up.com.au/api/v1/accounts/e7d94d11-198f-48e9-bde7-c79042969595/transactions"
          }
        }
      },
      "links": {
        "self": "https://api.up.com.au/api/v1/accounts/e7d94d11-198f-48e9-bde7-c79042969595"
      }
    }
  ],
  "links": {
    "prev": null,
    "next": "https://api.up.com.au/api/v1/accounts?page%5Bafter%5D=WyIyMDI0LTA5LTIwVDAzOjE0OjA2LjcyMDQ4ODAwMFoiLCJlN2Q5NGQxMS0xOThmLTQ4ZTktYmRlNy1jNzkwNDI5Njk1OTUiXQ%3D%3D&page%5Bsize%5D=1"
  }
}
"""

page = AccountsPage.model_validate_json(sample)

for account in page.data:
    print(account.attributes.display_name)
    print(account.attributes.balance.value_in_base_units)
    print(account.attributes.created_at)

print("next page:", page.links.next)