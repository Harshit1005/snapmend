import os
import glob
import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir=".",
            record_video_size={"width": 390, "height": 844},
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            geolocation={"latitude": 28.366587, "longitude": 77.541848},
            permissions=["geolocation"],
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
        )
        
        page = context.new_page()
        
        print("Navigating to home page...")
        page.goto("http://localhost:5173/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        print("Clicking New Assessment...")
        # Try finding the nav link or button
        page.get_by_text("New Assessment").first.click()
        time.sleep(1)
        
        print("Filling form...")
        page.locator("#street_segment_id").fill("SEG-772A")
        time.sleep(0.5)
        page.locator("#inspector_name").fill("Jane Doe")
        time.sleep(0.5)
        
        print("Getting location...")
        page.get_by_text("Use My Location").click()
        time.sleep(1.5) # Wait for location to fetch
        
        print("Uploading image...")
        # Since it's a file input, we can set the files directly on the input element
        page.set_input_files("input[type='file']", "test_pothole.jpg")
        time.sleep(1)
        
        print("Submitting...")
        page.get_by_text("Analyze Pavement").click()
        
        print("Waiting for results to load...")
        # Wait for the results to appear.
        page.wait_for_selector("text=Start New Assessment", timeout=30000)
        time.sleep(2)
        
        print("Scrolling results...")
        page.mouse.wheel(0, 300)
        time.sleep(2)
        page.mouse.wheel(0, 300)
        time.sleep(2)
        page.mouse.wheel(0, -600)
        time.sleep(1)
        
        print("Going back to dashboard...")
        page.get_by_text("Start New Assessment").first.click()
        time.sleep(2)
        
        context.close()
        browser.close()

        # Find the saved webm video and rename it
        videos = glob.glob("*.webm")
        if videos:
            latest_video = max(videos, key=os.path.getctime)
            if os.path.exists("demo.webm"):
                os.remove("demo.webm")
            os.rename(latest_video, "demo.webm")
            print(f"Video saved as demo.webm")

if __name__ == "__main__":
    run()
