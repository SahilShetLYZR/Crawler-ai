import asyncio
import os
from crawl4ai import AsyncWebCrawler

async def crawl_url(url: str):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return result.markdown

def lambda_handler(event, context):
    url = event.get("url")
    if not url:
        return {
            "statusCode": 400,
            "body": "Missing 'url' parameter in the event."
        }

    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/home/chromium"
    markdown_result = asyncio.run(crawl_url(url))

    return {
        "statusCode": 200,
        "body": markdown_result
    }
