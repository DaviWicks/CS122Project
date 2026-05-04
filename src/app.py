import os
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import webbrowser
import urllib.parse


RAW_HTML_PATH = "data/raw/all_genres_chart_source.html"
RAW_CSV_PATH = "data/raw/all_genres_chart.csv"
PROCESSED_CSV_PATH = "data/processed/all_genres_chart_clean.csv"


def parse_points_days(text: str):
    points_match = re.search(r"(\d+)\s+POINTS", text)
    days_match = re.search(r"(\d+)\s+DAYS", text)

    points = int(points_match.group(1)) if points_match else None
    days = int(days_match.group(1)) if days_match else None
    return points, days


def parse_artists(artist_text: str):
    if not artist_text:
        return []
    return [a.strip() for a in artist_text.split(",") if a.strip()]


def parse_genre_from_row(row):
    genre_div = row.find("div", id="genreplacement")
    if genre_div:
        genre_text = genre_div.get_text(" ", strip=True)
        if genre_text:
            return genre_text

    for tag in row.find_all(["div", "span"]):
        tag_id = (tag.get("id") or "").lower()
        tag_classes = " ".join(tag.get("class", [])).lower()
        text = tag.get_text(" ", strip=True)

        if ("genre" in tag_id or "genre" in tag_classes) and text:
            return text

    return ""


def scrape_saved_chart_html(html_path: str) -> pd.DataFrame:
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"Could not find HTML file: {html_path}")

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "lxml")
    rows = soup.find_all("div", id="top10artistchart-full")

    if not rows:
        raise ValueError("No chart rows found. Make sure you saved the correct page source.")

    chart_data = []

    for row in rows:
        rank_tag = row.find("div", id="top10artistchart-number")
        artist_tag = row.find("div", id="top10trackchart-artistname")
        title_tag = row.find("div", id="top10trackchart-title")
        points_tag = row.find("div", id="top10trackchart-points")

        rank_text = rank_tag.get_text(" ", strip=True) if rank_tag else ""
        numbers = re.findall(r"\d+", rank_text)

        rank = int(numbers[0]) if len(numbers) >= 1 else None
        rise_amount = int(numbers[1]) if len(numbers) >= 2 else 0

        artist_text = artist_tag.get_text(strip=True) if artist_tag else ""
        title = title_tag.get_text(strip=True) if title_tag else ""
        points_text = points_tag.get_text(" ", strip=True) if points_tag else ""

        points, days = parse_points_days(points_text)
        artists = parse_artists(artist_text)
        genre = parse_genre_from_row(row)

        beatport_link = ""
        for a in row.find_all("a", href=True):
            href = a["href"]
            if "beatport.com/track/" in href:
                beatport_link = href
                break

        chart_data.append({
            "rank": rank,
            "rise_amount": rise_amount,
            "is_rising": rise_amount > 0,
            "artist_raw": artist_text,
            "artists": " | ".join(artists),
            "num_artists": len(artists),
            "title": title,
            "genre": genre,
            "points": points,
            "days": days,
            "beatport_link": beatport_link,
        })

    df = pd.DataFrame(chart_data)
    df = df.drop_duplicates(subset=["rank", "artist_raw", "title"])
    df = df.sort_values("rank").reset_index(drop=True)
    return df

# Import the scraper function from your scraper.py file
try:
    from scraper import scrape_beatstats_full_100
except ImportError:
    # Defining a placeholder if the file isn't found immediately
    def scrape_beatstats_full_100():
        print("Error: scraper.py not found in the same directory.")

class BeatStatsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Beatport Music Trends Analysis")
        self.geometry("1300x800")
        self.df = pd.DataFrame()

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (HomePage, AnalysisPage):
            frame = F(parent=container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.sort_reverse = {}

        title = tk.Label(self, text="BeatStats Data Center", font=("Arial", 20, "bold"))
        title.pack(pady=15)

        # Main Control Panel
        controls = tk.Frame(self)
        controls.pack(pady=10)

        # Option 1: Live Scrape Button
        self.scrape_btn = tk.Button(
            controls, 
            text="🚀 Start Live Scrape (100 Tracks)", 
            command=self.start_scrape_thread,
            width=25, bg="#e1f5fe"
        )
        self.scrape_btn.grid(row=0, column=0, padx=10)

        # Option 2: Load CSV Button
        load_btn = tk.Button(
            controls, 
            text="📂 Load Existing CSV", 
            command=self.load_csv_file,
            width=25
        )
        load_btn.grid(row=0, column=1, padx=10)

        # Analysis Navigation
        analysis_btn = tk.Button(
            controls, 
            text="View Analysis", 
            command=lambda: controller.show_frame(AnalysisPage),
            width=15
        )
        analysis_btn.grid(row=0, column=2, padx=10)

        # Status and Progress
        self.status_var = tk.StringVar(value="Ready. Choose an option to begin.")
        status_label = tk.Label(self, textvariable=self.status_var, fg="blue", font=("Arial", 10, "italic"))
        status_label.pack(pady=5)

        # Table View
        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Updated columns based on your scraper output
        self.columns = ("rank", "momentum", "artist", "title", "genre", "label", "bpm", "key", "points", "days")
        self.tree = ttk.Treeview(table_frame, columns=self.columns, show="headings", height=20)

        for col in self.columns:
            self.tree.heading(col, text=col.title(), command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=100, anchor="center")
        
        # Adjusting specific column widths
        self.tree.column("artist", width=200, anchor="w")
        self.tree.column("title", width=200, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def start_scrape_thread(self):
        """Launches the scraper in a separate thread so the GUI doesn't freeze."""
        self.scrape_btn.config(state="disabled")
        self.status_var.set("Scraping in progress... this will take a few minutes. DO NOT CLOSE.")
        thread = threading.Thread(target=self.run_live_scrape)
        thread.daemon = True
        thread.start()

    def run_live_scrape(self):
        """Executes the scraper and updates the UI when finished."""
        try:
            # Calls the function from your scraper.py
            scrape_beatstats_full_100()
            
            # Look for the output file your scraper generates
            output_file = "beatstats_100_report.csv"
            if os.path.exists(output_file):
                df = pd.read_csv(output_file)
                self.controller.df = df
                self.after(0, self.refresh_table)
                self.after(0, lambda: self.status_var.set(f"Successfully scraped {len(df)} tracks!"))
            else:
                self.after(0, lambda: self.status_var.set("Error: Scraper finished but no CSV was found."))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Scrape Error", f"An error occurred: {e}"))
            self.after(0, lambda: self.status_var.set("Scrape failed."))
        finally:
            self.after(0, lambda: self.scrape_btn.config(state="normal"))

    def load_csv_file(self):
        """Opens a file dialog to load a previously saved CSV."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                df = pd.read_csv(file_path)
                self.controller.df = df
                self.refresh_table()
                self.status_var.set(f"Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Load Error", f"Could not read file: {e}")

    def refresh_table(self):
        """Populates the Treeview with the current dataframe."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        df = self.controller.df
        if df.empty:
            return

        for _, row in df.iterrows():
            self.tree.insert("", "end", values=(
                row.get("rank", ""),
                row.get("momentum", ""),
                row.get("artist", ""),
                row.get("title", ""),
                row.get("genre", ""),
                row.get("label", ""),
                row.get("bpm", ""),
                row.get("key", ""),
                row.get("points", ""),
                row.get("days", "")
            ))

    def sort_by_column(self, col):
        if self.controller.df.empty: return
        reverse = self.sort_reverse.get(col, False)
        self.sort_reverse[col] = not reverse
        self.controller.df = self.controller.df.sort_values(by=col, ascending=reverse).reset_index(drop=True)
        self.refresh_table()




class AnalysisPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        title = tk.Label(self, text="Analysis & Visualization Page", font=("Arial", 18, "bold"))
        title.pack(pady=15)

        tk.Label(self, text="Partner 2: Data Analysis and Visualization").pack(pady=5)

        tk.Button(self, text="1. Top 10 Genres", command=self.plot_genres, width=35).pack(pady=5)
        tk.Button(self, text="2. Top 10 Artists", command=self.plot_artists, width=35).pack(pady=5)
        tk.Button(self, text="3. Points vs Days", command=self.plot_points_vs_days, width=35).pack(pady=5)
        tk.Button(self, text="4. Average Points by Genre", command=self.plot_avg_points_by_genre, width=35).pack(pady=5)
        tk.Button(self, text="5. Rank vs Points", command=self.plot_rank_vs_points, width=35).pack(pady=5)
        tk.Button(self, text="6. Top Rising Tracks", command=self.show_rising_tracks, width=35).pack(pady=5)
        tk.Button(self, text="7. Play Most Popular Song", command=self.play_top_song, width=35).pack(pady=5)

        tk.Button(
            self,
            text="Back to Data Page",
            command=lambda: controller.show_frame(HomePage),
            width=35
        ).pack(pady=15)

    def get_df(self):
        df = self.controller.df
        if df.empty:
            messagebox.showwarning("No Data", "Please load the data on the Home page first.")
            return None
        return df

    def plot_genres(self):
        df = self.get_df()
        if df is None:
            return

        genre_counts = df["genre"].value_counts().head(10)

        plt.figure(figsize=(10, 6))
        genre_counts.plot(kind="bar", color="mediumorchid", edgecolor="black")
        plt.title("Top 10 Genres", fontsize=16, fontweight="bold")
        plt.xlabel("Genre")
        plt.ylabel("Count")
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.show()

    def plot_artists(self):
        df = self.get_df()
        if df is None:
            return

        artist_counts = df["artist_raw"].value_counts().head(10)

        plt.figure(figsize=(10, 6))
        artist_counts.plot(kind="bar", color="coral", edgecolor="black")
        plt.title("Top 10 Artists", fontsize=16, fontweight="bold")
        plt.xlabel("Artist")
        plt.ylabel("Count")
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.show()

    def plot_points_vs_days(self):
        df = self.get_df()
        if df is None:
            return

        plt.figure(figsize=(10, 6))
        plt.scatter(df["days"], df["points"], color="teal", alpha=0.7)
        plt.title("Points vs Days", fontsize=16, fontweight="bold")
        plt.xlabel("Days")
        plt.ylabel("Points")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    def plot_avg_points_by_genre(self):
        df = self.get_df()
        if df is None:
            return

        avg_points = df.groupby("genre")["points"].mean().sort_values(ascending=False).head(10)

        plt.figure(figsize=(10, 6))
        avg_points.plot(kind="bar", color="seagreen", edgecolor="black")
        plt.title("Average Points by Genre", fontsize=16, fontweight="bold")
        plt.xlabel("Genre")
        plt.ylabel("Average Points")
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.show()

    def plot_rank_vs_points(self):
        df = self.get_df()
        if df is None:
            return

        plt.figure(figsize=(10, 6))
        plt.scatter(df["rank"], df["points"], color="darkorange", alpha=0.7)
        plt.title("Rank vs Points", fontsize=16, fontweight="bold")
        plt.xlabel("Rank")
        plt.ylabel("Points")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    def show_rising_tracks(self):
        df = self.get_df()
        if df is None:
            return

        rising = df[df["rise_amount"] > 0].sort_values(by="rise_amount", ascending=False).head(10)

        if rising.empty:
            messagebox.showinfo("Top Rising Tracks", "No rising tracks found.")
            return

        lines = []
        for i, row in enumerate(rising.itertuples(), start=1):
            lines.append(
                f"{i}. {row.title}\n"
                f"   Artist: {row.artist_raw}\n"
                f"   Rose by: {row.rise_amount} spots\n"
            )

        messagebox.showinfo("Top Rising Tracks", "\n".join(lines))

    def play_top_song(self):
        df = self.get_df()
        if df is None:
            return

        top_song = df.sort_values(by="points", ascending=False).iloc[0]
        title = top_song["title"]
        artist = top_song["artist_raw"]

        query = urllib.parse.quote_plus(f"{title} {artist} official music video")
        url = f"https://www.youtube.com/results?search_query={query}"

        messagebox.showinfo(
            "Most Popular Song",
            f"{title}\nby {artist}\n\nOpening on YouTube..."
        )

        webbrowser.open(url)
