#!/usr/bin/env python3
"""
Browser verification script to ensure Playwright and Chromium are working properly.
This runs at container build time to verify the setup.
"""
import os
import sys
import asyncio
from playwright.async_api import async_playwright

async def verify_browser():
    """Test that we can launch a browser and load a page"""
    print("Starting browser verification...")
    
    try:
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '/tmp/ms-playwright'
        
        async with async_playwright() as p:
            # Launch with specific args for containerized environments
            browser = await p.chromium.launch(
                executable_path='/tmp/ms-playwright/chromium-1169/chrome-linux/chrome',
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            context = await browser.new_context()
            page = await context.new_page()
            
            # Try to load a simple page
            await page.goto('https://example.com')
            title = await page.title()
            
            # Get some page info
            content = await page.content()
            
            # Close everything properly
            await context.close()
            await browser.close()
            
            print(f"✅ Browser verification successful!")
            print(f"   Page title: {title}")
            print(f"   Content length: {len(content)} bytes")
            return True
            
    except Exception as e:
        print(f"❌ Browser verification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_browser())
    sys.exit(0 if success else 1)
