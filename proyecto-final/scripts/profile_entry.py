import asyncio
from app.main import stream_with_sentiment
from app.windows import time_window

async def main():
    i = 0
    async for batch in time_window(stream_with_sentiment(), 5):
        i += 1
        if i >= 3:
            break

if __name__ == "__main__":
    asyncio.run(main())
