import asyncio
import os
import sys
import traceback
import json
import time
import subprocess
from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright
from utils import extract_links, remove_duplicate_links, classify_url

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("crawler-api")

# Create FastAPI app
app = FastAPI(
    title="Web Crawler API",
    description="API for crawling web pages using Playwright",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class CrawlRequest(BaseModel):
    url: str
    bypass_cache: bool = Field(default=False)
    # You can add other parameters here as needed

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"error": f"Internal server error: {str(exc)}"},
    )

# Define the crawler endpoint
@app.post("/crawl")
async def crawl(request: CrawlRequest):
    """
    Crawl a web page using Playwright directly
    """
    start_time = time.time()
    logger.info(f"Crawling URL: {request.url}")
    
    if not request.url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
    
    try:
        # Use direct Playwright approach
        async with async_playwright() as p:
            # Launch browser with specific args
            browser = await p.chromium.launch(
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            # Create a new context and page
            context = await browser.new_context()
            page = await context.new_page()
            
            # Navigate to the URL
            await page.goto(request.url, wait_until="load", timeout=120000)

            # Extract content
            title = await page.title()
            content = await page.content()
            text = await page.evaluate('() => document.body.innerText')
            
            # Get all links
            links = await page.evaluate("""
                () => Array.from(document.querySelectorAll('a')).map(a => {
                    return {
                        href: a.href,
                        text: a.innerText.trim()
                    };
                })
            """)
            
            # Get meta tags
            meta_tags = await page.evaluate("""
                () => Array.from(document.querySelectorAll('meta')).map(meta => {
                    return {
                        name: meta.getAttribute('name'),
                        property: meta.getAttribute('property'),
                        content: meta.getAttribute('content')
                    };
                })
            """)
            
            # Close browser
            await browser.close()
            
            # Create result
            result = {
                "url": request.url,
                "title": title,
                "text": text[:10000] if len(text) > 10000 else text,  # Truncate if too long
                "links": links[:100] if len(links) > 100 else links,  # Limit number of links
                "meta_tags": meta_tags,
                "html_length": len(content),
                "crawl_time": time.time() - start_time
            }
            
            elapsed_time = time.time() - start_time
            logger.info(f"Crawl successful. Time: {elapsed_time:.2f}s")
            return result
                
    except Exception as e:
        error_message = f"Error during crawling: {str(e)}"
        logger.error(error_message)
        logger.error(traceback.format_exc())
        return {"error": error_message, "url": request.url}

# Direct JSON endpoint for simpler testing
@app.post("/crawl-json")
async def crawl_json(body: Dict[str, Any] = Body(...)):
    """
    Alternative endpoint that accepts raw JSON
    """
    url = body.get("url")
    bypass_cache = body.get("bypass_cache", False)
    
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
        
    request = CrawlRequest(url=url, bypass_cache=bypass_cache)
    return await crawl(request)

# Health check endpoint
@app.get("/health")
async def health():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": "Web Crawler API",
        "version": "1.0.0",
        "endpoints": {
            "POST /crawl": "Crawl a web page using Pydantic model",
            "POST /crawl-json": "Crawl a web page using raw JSON",
            "GET /health": "Health check",
            "GET /docs": "API documentation"
        }
    }

# Handle direct function invocation through API Gateway
@app.post("/lyzr-scrapper-master")
async def direct_function(body: Dict[str, Any] = Body(...)):
    """
    Direct function endpoint for API Gateway integration
    """
    url = body.get("url")
    bypass_cache = body.get("bypass_cache", False)
    
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
        
    request = CrawlRequest(url=url, bypass_cache=bypass_cache)
    return await crawl(request)


@app.post("/fetch_link")
async def fetch_link(request: CrawlRequest):
    if classify_url(request.url) != "Website":
        return request.url

    start_time = time.time()
    logger.info(f"Crawling URL: {request.url}")

    if not request.url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    try:
        # Use direct Playwright approach
        async with async_playwright() as p:
            # Launch browser with specific args
            browser = await p.chromium.launch(
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )

            # Create a new context and page
            context = await browser.new_context()
            page = await context.new_page()

            # Navigate to the URL
            await page.goto(request.url, wait_until="load", timeout=120000)


            # Extract content
            title = await page.title()
            content = await page.content()
            text = await page.evaluate('() => document.body.innerText')

            # Get all links
            links = await page.evaluate("""
                    () => Array.from(document.querySelectorAll('a')).map(a => {
                        return {
                            href: a.href,
                            text: a.innerText.trim()
                        };
                    })
                """)

            # Get meta tags
            meta_tags = await page.evaluate("""
                    () => Array.from(document.querySelectorAll('meta')).map(meta => {
                        return {
                            name: meta.getAttribute('name'),
                            property: meta.getAttribute('property'),
                            content: meta.getAttribute('content')
                        };
                    })
                """)

            # Close browser
            await browser.close()

            # Create result
            result = {
                "url": request.url,
                "title": title,
                "text": text[:10000] if len(text) > 10000 else text,  # Truncate if too long
                "links": links[:100] if len(links) > 100 else links,  # Limit number of links
                "meta_tags": meta_tags,
                "html_length": len(content),
                "crawl_time": time.time() - start_time
            }

            rdl = remove_duplicate_links(links)
            clean_data = extract_links(rdl)

            elapsed_time = time.time() - start_time
            logger.info(f"Crawl successful. Time: {elapsed_time:.2f}s")
            return clean_data

    except Exception as e:
        error_message = f"Error during crawling: {str(e)}"
        logger.error(error_message)
        logger.error(traceback.format_exc())
        return {"error": error_message, "url": request.url}

