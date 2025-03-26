import base64
import json
import requests

BUILD = requests.get("https://valorant-api.com/v1/version").json()["data"]["riotClientBuild"]
CLIENT_PLATFORM = client_platform = base64.b64encode(
    json.dumps(
        {
            "platformType": "PC",
            "platformOS": "Windows",
            "platformOSVersion": "10.0.19042.1.256.64bit",
            "platformChipset": "Unknown",
        }
    ).encode("utf-8")
)
VERSION = version = requests.get("https://valorant-api.com/v1/version").json()["data"]


class Valorant:
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token

        self.session = requests.Session()
        self.set_headers()

        self.entitlements_token = self.get_entitlement_token()
        self.user_info = self.get_user_info()

    def reauth(self) -> None:
        self.entitlements_token = self.get_entitlement_token()
        self.user_info = self.get_user_info()

    def set_headers(self) -> None:
        self.session.headers.update({
            "User-Agent": f"RiotClient/{BUILD} riot-status (Windows;10;;Professional, x64)",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        })

    def get_user_info(self) -> dict:
        return self.session.post("https://auth.riotgames.com/userinfo").json()

    def get_entitlement_token(self) -> str:
        request = self.session.post(
            "https://entitlements.auth.riotgames.com/api/token/v1",
            data={}
        )
        if request.status_code == 401:
            raise ValueError("Access token is not valid")

        return request.json()["entitlements_token"]

    def get_store_skins(self) -> dict:
        return self.session.post(
            f"https://pd.eu.a.pvp.net/store/v3/storefront/{self.user_info["sub"]}",
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "X-Riot-Entitlements-JWT": self.entitlements_token,
                "X-Riot-ClientPlatform": client_platform,
                "X-Riot-ClientVersion": version["riotClientVersion"],
                "Content-Type": "application/json",
            },
            json={}
        ).json()["SkinsPanelLayout"]["SingleItemStoreOffers"]
