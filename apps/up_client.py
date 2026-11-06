import httpx

from apps.config import settings
from apps.schemas.accounts import AccountResource, AccountsPage
from apps.schemas.categories import CategoryResource, CategoriesPage

BASE_URL = "https://api.up.com.au/api/v1"

class UpError(Exception):
    pass

class AuthenticationError(UpError):
    pass

class ServerError(UpError):
    pass

class UpClient:

    def __init__(self) -> None:

        token = settings.upbank_token.get_secret_value()

        self.http = httpx.Client(
            base_url=BASE_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=20.0
        )
        
    def _get(self, url: str, params: dict | None = None) -> httpx.Response:
        
        response = self.http.get(url, params=params)

        try:
            response.raise_for_status()

        except httpx.HTTPStatusError as e:

            if e.response.status_code == 401:
                raise AuthenticationError("Up API Authentication Error 401: Invalid or expired token") from e

            elif e.response.status_code >= 500:
                raise ServerError(f"Up API Server Error {e.response.status_code}") from e

            else:
                raise

        return response

    def ping(self) -> bool:
        self._get(url="/util/ping")
        return True

    def list_accounts(self) -> list[AccountResource]:

        accounts: list[AccountResource] = []
        response = self._get(url="/accounts", params={"page[size]": 100})

        while True:
            page = AccountsPage.model_validate_json(response.text)
            accounts.extend(page.data)

            if page.links.next is None:
                break

            response = self._get(url=page.links.next)

        return accounts

    def list_categories(self) -> CategoriesPage:

        response = self._get(url="/categories")
        page = CategoriesPage.model_validate_json(response.text)

        return page

    def close(self) -> None:
        self.http.close()