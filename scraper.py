import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random
import os

def scrape_beatstats_full_100():
    print("Launching stealth browser...")
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options, version_main=147)
    
    try:
        url = "https://www.beatstats.com/tracks/home/list?genre=0&period=2"
        driver.get(url)

        print("\n--- WAITING FOR DATA ---")
        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.ID, "top10artistchart-full")))
        time.sleep(5) 

        containers = driver.find_elements(By.ID, "top10artistchart-full")
        extracted_data = []

        for item in containers:
            try:
                rank_el = item.find_element(By.ID, "top10artistchart-number")
                rank = driver.execute_script("return arguments[0].firstChild.textContent;", rank_el).strip()
                
                try:
                    momentum = item.find_element(By.ID, "top10artistchart-arrowtext").text.strip()
                except:
                    momentum = "0"

                artist = item.find_element(By.ID, "top10trackchart-artistname").text.strip()
                title = item.find_element(By.ID, "top10trackchart-title").text.strip()
                
                points_container = item.find_element(By.ID, "top10trackchart-points")
                strong_tags = points_container.find_elements(By.TAG_NAME, "strong")
                points = strong_tags[0].text.strip() if len(strong_tags) > 0 else "0"
                days = strong_tags[1].text.strip() if len(strong_tags) > 1 else "0"
                
                try:
                    genre = points_container.find_element(By.CLASS_NAME, "curved-box").text.strip()
                except:
                    genre = "N/A"

                track_url = None
                potential_links = item.find_elements(By.XPATH, ".//a | .. | ../..")
                for l in potential_links:
                    href = l.get_attribute("href")
                    if href and "/track/track/" in href:
                        track_url = href
                        break

                extracted_data.append({
                    "rank": rank, "momentum": momentum, "artist": artist, 
                    "title": title, "points": points, "days": days, 
                    "genre": genre, "url": track_url
                })
            except:
                continue

        print(f"Successfully identified {len(extracted_data)} tracks.")

        final_results = []
        # --- SCALING TO 100 ---
        # Using [:] ensures we grab every single song found in the list
        print("Starting Deep Scrape of all 100 tracks. This will take a few minutes...")
        
        for i, song in enumerate(extracted_data, 1):
            if not song['url']:
                for field in ['label', 'released', 'bpm', 'key', 'length']: song[field] = "N/A"
                final_results.append(song)
                continue

            print(f"[{i}/100] Scraping: {song['artist']}")
            try:
                driver.get(song['url'])
                # Random delay between 2 and 4 seconds to avoid detection
                time.sleep(1.2)
                
                stats = driver.find_elements(By.CLASS_NAME, "tracktextb")
                song['length'] = stats[0].text.strip() if len(stats) > 0 else "N/A"
                song['released'] = stats[1].text.strip() if len(stats) > 1 else "N/A"
                song['bpm'] = stats[2].text.strip() if len(stats) > 2 else "N/A"
                song['key'] = stats[3].text.strip() if len(stats) > 3 else "N/A"
                
                try:
                    song['label'] = driver.find_element(By.CSS_SELECTOR, "a[href^='/label/']").text.strip()
                except:
                    song['label'] = "N/A"
            except:
                for field in ['label', 'released', 'bpm', 'key', 'length']: song[field] = "N/A"
            
            final_results.append(song)

            # Optional: Save every 10 tracks so you don't lose progress if it crashes
            if i % 10 == 0:
                pd.DataFrame(final_results).to_csv("beatstats_partial.csv", index=False)

        # Final Save

        output_dir = os.path.join("data", "processed")

        os.makedirs(output_dir, exist_ok=True)

        file_path = os.path.join(output_dir, "beatstats_100_report.csv")

        df = pd.DataFrame(final_results)
        cols = ['rank', 'momentum', 'artist', 'title', 'genre', 'points', 'days', 'label', 'released', 'bpm', 'key', 'length']
        for c in cols:
            if c not in df.columns: df[c] = "N/A"
        
        df[cols].to_csv(file_path, index=False)
        print(f"\nDONE! Full 100 tracks saved to 'beatstats_100_report.csv'")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_beatstats_full_100()