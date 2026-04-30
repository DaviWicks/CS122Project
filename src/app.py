import os
import re
import tkinter as tk
from tkinter import ttk, messagebox

import pandas as pd
from bs4 import BeautifulSoup


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


class BeatStatsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Beatport Music Trends Analysis")
        self.geometry("1300x760")

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

        title = tk.Label(self, text="Data Collection & Organization", font=("Arial", 20, "bold"))
        title.pack(pady=15)

        controls = tk.Frame(self)
        controls.pack(pady=10)

        tk.Label(controls, text="Chart:").grid(row=0, column=0, padx=8)

        self.chart_var = tk.StringVar(value="TOP 100 (ALL GENRES)")
        chart_dropdown = ttk.Combobox(
            controls,
            textvariable=self.chart_var,
            values=["TOP 100 (ALL GENRES)"],
            state="readonly",
            width=24
        )
        chart_dropdown.grid(row=0, column=1, padx=8)

        load_button = tk.Button(
            controls,
            text="Load / Refresh Data",
            command=self.load_data,
            width=20
        )
        load_button.grid(row=0, column=2, padx=8)

        partner_page_button = tk.Button(
            controls,
            text="Go to Analysis Page",
            command=lambda: controller.show_frame(AnalysisPage),
            width=18
        )
        partner_page_button.grid(row=0, column=3, padx=8)

        self.status_var = tk.StringVar(value="Load the saved BeatStats all-genres page source to begin.")
        status_label = tk.Label(self, textvariable=self.status_var, fg="blue")
        status_label.pack(pady=8)

        self.summary_var = tk.StringVar(value="No data loaded.")
        summary_label = tk.Label(self, textvariable=self.summary_var, font=("Arial", 11))
        summary_label.pack(pady=5)

        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self.columns = ("rank", "rise_amount", "genre", "artist_raw", "title", "points", "days", "num_artists")
        self.tree = ttk.Treeview(table_frame, columns=self.columns, show="headings", height=24)

        for col in self.columns:
            self.tree.heading(col, text=col.title(), command=lambda c=col: self.sort_by_column(c))

            if col == "title":
                self.tree.column(col, width=300)
            elif col == "artist_raw":
                self.tree.column(col, width=260)
            elif col == "genre":
                self.tree.column(col, width=170)
            else:
                self.tree.column(col, width=100)

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")

    def load_data(self):
        try:
            df = scrape_saved_chart_html(RAW_HTML_PATH)
            self.controller.df = df

            # Auto-save CSVs
            os.makedirs("data/raw", exist_ok=True)
            os.makedirs("data/processed", exist_ok=True)

            df.to_csv(RAW_CSV_PATH, index=False)

            clean_df = df[[
                "rank",
                "rise_amount",
                "is_rising",
                "artist_raw",
                "artists",
                "num_artists",
                "title",
                "genre",
                "points",
                "days",
                "beatport_link"
            ]].copy()

            clean_df.to_csv(PROCESSED_CSV_PATH, index=False)

            self.refresh_table()

            self.status_var.set("Data loaded and CSV files updated successfully.")
            self.summary_var.set(
                f"Tracks loaded: {len(df)} | Genres found: {df['genre'].nunique()} | "
                f"Avg points: {df['points'].mean():.2f} | Avg days: {df['days'].mean():.2f}"
            )
        except Exception as e:
            messagebox.showerror("Load Error", str(e))
            self.status_var.set("Failed to load data.")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        df = self.controller.df
        for _, row in df.iterrows():
            rise_display = f"+{row['rise_amount']}" if row["rise_amount"] > 0 else "0"
            self.tree.insert(
                "",
                "end",
                values=(
                    row["rank"],
                    rise_display,
                    row["genre"],
                    row["artist_raw"],
                    row["title"],
                    row["points"],
                    row["days"],
                    row["num_artists"]
                )
            )

    def sort_by_column(self, col):
        df = self.controller.df
        if df.empty:
            return

        reverse = self.sort_reverse.get(col, False)
        self.sort_reverse[col] = not reverse

        df_sorted = df.sort_values(by=col, ascending=reverse).reset_index(drop=True)
        self.controller.df = df_sorted
        self.refresh_table()


class AnalysisPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        title = tk.Label(self, text="Analysis & Visualization Page", font=("Arial", 20, "bold"))
        title.pack(pady=20)

        info = tk.Label(
            self,
            text=(
                "This page is for Partner 2.\n\n"
                "Suggested analyses with all-genres data:\n"
                "- Top genres by chart appearances\n"
                "- Top artists by chart appearances\n"
                "- Average points by genre\n"
                "- Average days on chart by genre\n"
                "- Rising tracks using rise_amount\n"
                "- Songs with the most collaborating artists\n"
            ),
            justify="left",
            font=("Arial", 12)
        )
        info.pack(pady=20)

        back_button = tk.Button(
            self,
            text="Back to Data Page",
            command=lambda: controller.show_frame(HomePage),
            width=18
        )
        back_button.pack(pady=10)