import asyncio
import os
import shutil
import glob
from playwright.async_api import async_playwright
import imageio_ffmpeg
import subprocess

APP_URL = "https://tricoach-ai-frontend-250828361255.us-central1.run.app"
RECORDING_DIR = "recordings"

async def record_demo():
    if os.path.exists(RECORDING_DIR):
        shutil.rmtree(RECORDING_DIR)
    os.makedirs(RECORDING_DIR, exist_ok=True)
    
    print(f"Launching Playwright Chromium recording to {RECORDING_DIR}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=RECORDING_DIR,
            record_video_size={"width": 1280, "height": 720}
        )
        
        page = await context.new_page()
        print(f"Navigating to {APP_URL}...")
        await page.goto(APP_URL, wait_until="networkidle")
        await asyncio.sleep(2.0)
        
        # 1. Toggle Dark Mode
        print("Toggling Dark Theme...")
        await page.click("#themeToggle")
        await asyncio.sleep(2.0)
        
        # 2. Click HR Zones Prompt Chip
        print("Clicking HR Zones prompt chip...")
        chips = await page.query_selector_all(".chip")
        if chips:
            await chips[0].click()
        else:
            await page.fill("#input", "Calculate heart rate zones for Max HR 181 bpm")
            await page.click("button.send-btn")
            
        print("Waiting for HR Zones response...")
        await asyncio.sleep(8.0)
        
        # 3. Toggle back to Light Theme
        print("Toggling Light Theme...")
        await page.click("#themeToggle")
        await asyncio.sleep(2.0)
        
        # 4. Ask for Bike Workout Card
        print("Asking for Bike Workout summary card...")
        if len(chips) > 1:
            await chips[1].click()
        else:
            await page.fill("#input", "Give me a summary card of a recommended 45-minute triathlon bike workout")
            await page.click("button.send-btn")
            
        print("Waiting for A2UI response...")
        await asyncio.sleep(9.0)
        
        # 5. Toggle Dark Theme again to demonstrate card in dark mode
        print("Toggling Dark Theme for A2UI card...")
        await page.click("#themeToggle")
        await asyncio.sleep(3.0)
        
        print("Closing browser context to finalize video recording...")
        await page.close()
        await context.close()
        await browser.close()
        
    # Locate recorded webm file
    files = glob.glob(os.path.join(RECORDING_DIR, "*.webm"))
    if not files:
        raise RuntimeError("No recorded video found in recordings folder!")
    raw_video_path = files[0]
    print(f"Recorded raw video: {raw_video_path}")
    return raw_video_path

def combine_video_audio(video_path, audio_path, output_mp4):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Using FFmpeg binary: {ffmpeg_exe}")
    
    # Run FFmpeg command to merge video & audio, loop/trim audio to match video duration
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        output_mp4
    ]
    
    print("Combining video and upbeat lo-fi audio...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg error:", res.stderr)
        raise RuntimeError(f"FFmpeg failed with code {res.returncode}")
        
    print(f"Demo video with upbeat lo-fi music successfully created at: {output_mp4}")
    return output_mp4

if __name__ == "__main__":
    raw_video = asyncio.run(record_demo())
    audio_file = "lofi_music.wav"
    output_mp4 = "demo_with_lofi_music.mp4"
    combine_video_audio(raw_video, audio_file, output_mp4)
    
    # Also copy to artifacts folder
    artifact_dest = "/config/.gemini/antigravity/brain/9a9e4e8c-be2e-43c9-87fb-2608c44c212e/tricoach_demo.mp4"
    shutil.copy(output_mp4, artifact_dest)
    print(f"Copied demo artifact to: {artifact_dest}")
