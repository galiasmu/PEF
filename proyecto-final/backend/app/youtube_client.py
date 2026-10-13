import asyncio
from typing import AsyncGenerator, Dict, Any, Optional
import aiohttp

BASE = "https://www.googleapis.com/youtube/v3"

class YouTubePoller:
    def __init__(self, api_key: str, target_type: str, target_id: str, poll_interval: int = 5):
        self.api_key = api_key
        self.target_type = target_type
        self.target_id = target_id
        self.poll_interval = poll_interval
        self._page_token: Optional[str] = None

    async def _fetch(self, session: aiohttp.ClientSession, url: str, params: Dict[str, str]) -> Dict[str, Any]:
        async with session.get(url, params=params, timeout=30) as r:
            r.raise_for_status()
            return await r.json()

    async def comments_stream(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Generador asíncrono que emite comentarios nuevos en cada poll."""
        if not self.target_id:
            raise RuntimeError("TARGET_ID requerido.")
        url = f"{BASE}/commentThreads"
        params: Dict[str, str] = {
            "key": self.api_key,
            "part": "snippet",
            "maxResults": "100",
            "order": "time",
        }
        if self.target_type == "video":
            params["videoId"] = self.target_id
        else:
            params["allThreadsRelatedToChannelId"] = self.target_id

        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    if self._page_token:
                        params["pageToken"] = self._page_token
                    data = await self._fetch(session, url, params)
                    self._page_token = data.get("nextPageToken")
                    items = data.get("items", [])
                    for it in items:
                        sn = it.get("snippet", {})
                        c = sn.get("topLevelComment", {}).get("snippet", {})
                        yield {
                            "id": it.get("id"),
                            "text": c.get("textDisplay", ""),
                            "author": c.get("authorDisplayName", ""),
                            "publishedAt": c.get("publishedAt"),
                            "likeCount": c.get("likeCount", 0),
                            "videoId": c.get("videoId"),
                        }
                except Exception:
                    # backoff simple
                    await asyncio.sleep(self.poll_interval * 2)
                await asyncio.sleep(self.poll_interval)
