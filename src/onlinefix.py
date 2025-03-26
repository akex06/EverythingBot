from typing import AsyncGenerator, AsyncIterable

import httpx
from bs4 import BeautifulSoup


class OnlineFix:
    GAME_PAGE_HEADERS = {
        "Host": "uploads.online-fix.me:2053",
        "Referer": "https://online-fix.me/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0"
    }

    def __init__(self) -> None:
        self.session = httpx.AsyncClient()
        self.session.headers = {
            "Host": "online-fix.me",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0"
        }

    async def start(self) -> None:
        await self.set_cookies()
        await self.login()

    async def set_cookies(self) -> None:
        await self.session.get("https://online-fix.me/")

    async def login(self) -> None:
        AJAX_HEADERS = self.session.headers.copy()
        AJAX_HEADERS["X-Requested-With"] = "XMLHttpRequest"
        AJAX_HEADERS["Referer"] = "https://online-fix.me/"

        token = (await self.session.get(
            "https://online-fix.me/engine/ajax/authtoken.php",
            headers=AJAX_HEADERS
        )).json()

        await self.session.post(
            "https://online-fix.me/",
            headers=AJAX_HEADERS,
            data={
                "login_name": "testakek69",
                "login_password": "#Test12345",
                "login": "submit",
                token["field"]: token["value"]
            })

    @staticmethod
    def get_game_header(game_url: str) -> dict:
        return {
            "Host": "uploads.online-fix.me:2053",
            "Referer": game_url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0"
        }

    async def get_page_amount(self, url: str) -> int:
        soup = await self.get_soup(url)
        try:
            return int(soup.find("nav").find_all("a")[-2].text)
        except AttributeError:
            return 1

    async def get_pages(self, url: str) -> AsyncGenerator[BeautifulSoup, None]:
        if not url.endswith("/"):
            url += "/"

        page_amount = await self.get_page_amount(url)
        for page_num in range(1, page_amount + 1):
            soup = await self.get_soup(f"{url}page/{page_num}")
            yield soup

    async def get_soup(self, url: str, headers: dict | None = None) -> BeautifulSoup:
        headers = headers if headers is not None else self.session.headers
        content = (await self.session.get(url, headers=headers, follow_redirects=True)).content
        soup = BeautifulSoup(content, "html.parser")
        return soup

    async def download_game(self, url: str) -> tuple[bytes, str]:
        torrent_url = (await self.get_soup(url)).find("a", string="Скачать Torrent")["href"]
        game_url = (await self.get_soup(torrent_url, headers=OnlineFix.GAME_PAGE_HEADERS)).find_all("a")[-1]["href"]

        req = await self.session.get(
            f"{torrent_url}{game_url}",
            headers=OnlineFix.get_game_header(torrent_url)
        )

        return req.content, game_url
