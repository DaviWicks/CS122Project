import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import threading
import matplotlib.pyplot as plt
import webbrowser
import urllib.parse

# Path Configuration - Now relative to root
PROCESSED_DIR = os.path.join("data", "processed")
REPORT_FILE = os.path.join(PROCESSED_DIR, "beatstats_100_report.csv")

# Standard import now that both are in the root directory
try:
    from scraper import scrape_beatstats_full_100
except ImportError:
    def scrape_beatstats_full_100():
        messagebox.showerror("Error", "scraper.py not found in the root directory.")

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
        self.frames[page_class].tkraise()

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.sort_reverse = {}

        tk.Label(self, text="BeatStats Data Center", font=("Arial", 22, "bold")).pack(pady=15)

        controls = tk.Frame(self)
        controls.pack(pady=10)

        self.scrape_btn = tk.Button(controls, text="🚀 Start Live Scrape", command=self.start_scrape_thread, width=20, bg="#e1f5fe")
        self.scrape_btn.grid(row=0, column=0, padx=10)

        tk.Button(controls, text="📂 Load CSV", command=self.load_csv_file, width=20).grid(row=0, column=1, padx=10)
        tk.Button(controls, text="📊 View Analysis", command=lambda: controller.show_frame(AnalysisPage), width=15).grid(row=0, column=2, padx=10)

        self.status_var = tk.StringVar(value="Ready. Files will be managed in data/processed/")
        tk.Label(self, textvariable=self.status_var, fg="blue").pack(pady=5)

        table_frame = tk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Columns configured to match partner's scraper output
        self.columns = ("rank", "momentum", "artist", "title", "label", "bpm", "key", "points", "days")
        self.tree = ttk.Treeview(table_frame, columns=self.columns, show="headings")

        for col in self.columns:
            self.tree.heading(col, text=col.title(), command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=100, anchor="center")
        
        self.tree.pack(side="left", fill="both", expand=True)

    def start_scrape_thread(self):
        self.scrape_btn.config(state="disabled")
        self.status_var.set("Scraping all 100 tracks... check terminal for live progress.")
        threading.Thread(target=self.run_live_scrape, daemon=True).start()

    def run_live_scrape(self):
        try:
            # Executes scraper.py logic
            scrape_beatstats_full_100()
            if os.path.exists(REPORT_FILE):
                self.controller.df = pd.read_csv(REPORT_FILE)
                self.after(0, self.refresh_table)
                self.after(0, lambda: self.status_var.set("Scrape Complete! Data refreshed."))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.after(0, lambda: self.scrape_btn.config(state="normal"))

    def load_csv_file(self):
        path = filedialog.askopenfilename(initialdir=PROCESSED_DIR, filetypes=[("CSV", "*.csv")])
        if path:
            self.controller.df = pd.read_csv(path)
            self.refresh_table()
            self.status_var.set(f"Loaded: {os.path.basename(path)}")

    def refresh_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        if self.controller.df.empty: return
        for _, row in self.controller.df.iterrows():
            self.tree.insert("", "end", values=[row.get(c, "N/A") for c in self.columns])

    def sort_by_column(self, col):
        if not self.controller.df.empty:
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

        # Restoring all original partner buttons
        tk.Button(self, text="1. Top 10 Genres", command=self.plot_genres, width=35).pack(pady=5)
        tk.Button(self, text="2. Top 10 Artists", command=self.plot_artists, width=35).pack(pady=5)
        tk.Button(self, text="3. Points vs Days", command=self.plot_points_vs_days, width=35).pack(pady=5)
        tk.Button(self, text="4. Average Points by Genre", command=self.plot_avg_points_by_genre, width=35).pack(pady=5)
        tk.Button(self, text="5. Rank vs Points", command=self.plot_rank_vs_points, width=35).pack(pady=5)
        tk.Button(self, text="6. Top Rising Tracks", command=self.show_rising_tracks, width=35).pack(pady=5)
        tk.Button(self, text="7. BPM Distribution", command=self.plot_bpm, width=35).pack(pady=5)
        tk.Button(self, text="8. Musical Key Pie Chart", command=self.plot_keys, width=35).pack(pady=5)
        tk.Button(self, text="9. Play Most Popular Song", command=self.play_top_song, width=35, bg="#ffcdd2").pack(pady=5)

        tk.Button(self, text="Back to Data Page", command=lambda: controller.show_frame(HomePage), width=35).pack(pady=15)

    def get_df(self):
        df = self.controller.df
        if df.empty:
            messagebox.showwarning("No Data", "Please load the data on the Home page first.")
            return None
        return df

    def plot_genres(self):
        df = self.get_df()
        if df is not None:
            genre_counts = df["genre"].value_counts().head(10)
            plt.figure(figsize=(10, 6))
            genre_counts.plot(kind="bar", color="mediumorchid", edgecolor="black")
            plt.title("Top 10 Genres", fontsize=16, fontweight="bold")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.show()

    def plot_artists(self):
        df = self.get_df()
        if df is None:
            return

        # 1. Take the artist column and split names by common separators
        # We handle commas, ampersands, and 'feat.' to be thorough
        all_artists = []
        for entry in df["artist"].dropna():
            # Replace common separators with a comma so we can split easily
            entry = entry.replace(" & ", ",").replace(" feat. ", ",").replace(" ft. ", ",")
            names = [name.strip() for name in entry.split(",")]
            all_artists.extend(names)

        # 2. Convert the list of individual names into a Series to count them
        artist_counts = pd.Series(all_artists).value_counts().head(10)

        # 3. Plotting
        plt.figure(figsize=(12, 7))
        artist_counts.plot(kind="bar", color="coral", edgecolor="black")
        plt.title("Top 10 Individual Artists (Including Collaborations)", fontsize=16, fontweight="bold")
        plt.xlabel("Artist Name")
        plt.ylabel("Number of Tracks in Top 100")
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.show()

    def plot_points_vs_days(self):
        df = self.get_df()
        if df is not None:
            plt.figure(figsize=(10, 6))
            plt.scatter(df["days"], df["points"], color="teal", alpha=0.7)
            plt.title("Points vs Days", fontsize=16, fontweight="bold")
            plt.xlabel("Days")
            plt.ylabel("Points")
            plt.show()

    def plot_avg_points_by_genre(self):
        df = self.get_df()
        if df is not None:
            avg_points = df.groupby("genre")["points"].mean().sort_values(ascending=False).head(10)
            plt.figure(figsize=(10, 6))
            avg_points.plot(kind="bar", color="seagreen", edgecolor="black")
            plt.title("Average Points by Genre", fontsize=16, fontweight="bold")
            plt.show()

    def plot_rank_vs_points(self):
        df = self.get_df()
        if df is not None:
            plt.figure(figsize=(10, 6))
            plt.scatter(df["rank"], df["points"], color="darkorange", alpha=0.7)
            plt.title("Rank vs Points", fontsize=16, fontweight="bold")
            plt.xlabel("Rank")
            plt.ylabel("Points")
            plt.show()

    def clean_data(self):
        """Helper to ensure numeric columns are actually numbers."""
        if self.controller.df.empty:
            return

        # 1. Convert momentum/rise_amount to numeric, stripping symbols like '+'
        if 'momentum' in self.controller.df.columns:
            # We use strings to replace '+' so pd.to_numeric doesn't fail
            self.controller.df['rise_amount'] = self.controller.df['momentum'].astype(str).str.replace('+', '', regex=False)
            self.controller.df['rise_amount'] = pd.to_numeric(self.controller.df['rise_amount'], errors='coerce').fillna(0)

        # 2. Ensure Points and Days are also numeric for the scatter plots
        self.controller.df['points'] = pd.to_numeric(self.controller.df['points'], errors='coerce').fillna(0)
        self.controller.df['days'] = pd.to_numeric(self.controller.df['days'], errors='coerce').fillna(0)
        self.controller.df['rank'] = pd.to_numeric(self.controller.df['rank'], errors='coerce').fillna(0)

    def show_rising_tracks(self):
        df = self.get_df()
        if df is None:
            return

        # Ensure we have clean numbers before filtering
        self.clean_data()

        # Filter for tracks that rose at least 1 spot
        rising = self.controller.df[self.controller.df["rise_amount"] > 0].sort_values(by="rise_amount", ascending=False).head(10)

        if rising.empty:
            messagebox.showinfo("Top Rising Tracks", "No tracks are currently rising in the charts (all are stable or falling).")
            return

        lines = []
        for i, row in enumerate(rising.itertuples(), start=1):
            # Using getattr to handle potential column name mismatches safely
            title = getattr(row, 'title', 'Unknown')
            artist = getattr(row, 'artist', 'Unknown')
            rise = int(getattr(row, 'rise_amount', 0))
            
            lines.append(f"{i}. {title}\n   Artist: {artist}\n   Rose by: {rise} spots\n")

        messagebox.showinfo("Top Rising Tracks", "\n".join(lines))

    def plot_bpm(self):
        df = self.get_df()
        if df is not None:
            bpms = pd.to_numeric(df['bpm'], errors='coerce').dropna()
            bpms.hist(bins=15, color='orange', edgecolor='black')
            plt.title("Tempo (BPM) Distribution")
            plt.show()

    def plot_keys(self):
        df = self.get_df()
        if df is not None:
            df['key'].value_counts().plot(kind='pie', autopct='%1.1f%%')
            plt.title("Musical Key Distribution")
            plt.ylabel("")
            plt.show()

    def play_top_song(self):
        df = self.get_df()
        if df is not None:
            top_song = df.sort_values(by="points", ascending=False).iloc[0]
            query = urllib.parse.quote_plus(f"{top_song['title']} {top_song['artist']} official")
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")

if __name__ == "__main__":
    BeatStatsApp().mainloop()