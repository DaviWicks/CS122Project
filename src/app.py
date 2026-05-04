import os
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import threading
import time

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
        tk.Label(self, text="Analysis & Visualization", font=("Arial", 20, "bold")).pack(pady=20)
        
        info = tk.Label(self, text="Use the data loaded on the Home Page to generate charts.\n(Partner 2's implementation goes here.)", font=("Arial", 12))
        info.pack(pady=20)

        tk.Button(self, text="Back to Home", command=lambda: controller.show_frame(HomePage)).pack(pady=10)

if __name__ == "__main__":
    app = BeatStatsApp()
    app.mainloop()