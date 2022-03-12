from dataclasses import dataclass
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from typing import Optional


@dataclass
class LyricsData:
    resolved_title: str
    lyrics: str


async def get_genius_lyrics(session: ClientSession, **params) -> Optional[LyricsData]:
    async with session.get("https://genius.com/api/search/song", params=params) as r:
        if not r.ok:
            return

        res = await r.json()
        if res["meta"]["status"] != 200:
            return

    try:
        song = res["response"]["sections"][0]["hits"][0]["result"]
    except (IndexError, KeyError):
        return

    async with session.get(song["url"]) as r:
        if not r.ok:
            return

        text = await r.text()

    soup = BeautifulSoup(text.replace("<br/>", "\n"), "lxml")
    tags = soup.select("div[data-lyrics-container=true]")

    return LyricsData(
        resolved_title=song["full_title"], lyrics="\n".join([tag.text for tag in tags])
    )
