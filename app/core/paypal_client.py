from decimal import Decimal
from typing import Any, Dict, Optional

import httpx


class PayPalClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str,
        timeout: float = 10.0,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get_access_token(self) -> str:
        url = f"{self.base_url}/v1/oauth2/token"
        response = httpx.post(
            url,
            data={"grant_type": "client_credentials"},
            auth=(self.client_id, self.client_secret),
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["access_token"]

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        response = httpx.request(
            method,
            f"{self.base_url}{endpoint}",
            json=json,
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def create_order(
        self,
        *,
        order_id: int,
        total_amount: Decimal,
        currency: str,
    ) -> Dict[str, Any]:
        token = self._get_access_token()
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": str(order_id),
                    "amount": {
                        "value": f"{total_amount:.2f}",
                        "currency_code": currency,
                    },
                }
            ],
        }
        return self._request(
            "POST",
            "/v2/checkout/orders",
            json=payload,
            token=token,
        )

    def capture_order(self, *, provider_payment_id: str) -> Dict[str, Any]:
        token = self._get_access_token()
        return self._request(
            "POST",
            f"/v2/checkout/orders/{provider_payment_id}/capture",
            token=token,
        )
