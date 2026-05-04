# Beatport Music Trends Analysis

## Authors

* **Davis Nguyen** (Data Collection & Organization)
* **Gloria B Castro** (Analysis & Visualization)

---

## Project Description

This project analyzes electronic music trends using real-time and historical chart data from **BeatStats**, which aggregates Beatport Top 100 rankings. 

The application provides a professional-grade workflow to extract, process, and visualize the sonic characteristics and market performance of trending tracks. By automating the data collection process, the program allows users to identify patterns in track rankings, artists (including collaborations), genres, and musical metadata like BPM and Key.

The data is structured into local CSV files and used to analyze trends across genres, artists, record labels, and chart performance longevity.

---

## Key Features

* **Automated Selenium Scraper**: Bypasses anti-bot protections to perform a live "Top 100" scrape directly from the web.
* **Multi-threaded GUI**: A Tkinter-based interface that prevents application freezing during long data-gathering tasks.
* **Collaboration Analysis**: Multi-artist parsing to track collaboration trends and most frequent contributors.
* **Sonic Profiling**: Distribution analysis of BPM (tempo) and Musical Keys across the charts.
* **Market Share Tracking**: Analysis of record label dominance within the Top 100.
* **Chart Movement**: Real-time tracking of "Rising Tracks" and momentum.
* **Multimedia Integration**: Direct search and playback functionality for the most popular tracks via YouTube.

---

## Data Collection and Storage (Author #1)

Data is collected from publicly accessible BeatStats chart pages. 

While the program originally relied on manual HTML source parsing, it has been upgraded to include a **Selenium-driven automation engine** (`scraper.py`). This engine handles the complexities of dynamic web elements to extract:

* **Rank & Momentum**: Current position and rise/fall spots.
* **Artist & Title**: Full artist string parsing and track naming.
* **Metadata**: Record Label, Release Date, BPM, Key, and Track Length.
* **Performance Metrics**: Total Points and Days on Chart.

The cleaned dataset is automatically stored in a structured directory: `data/processed/beatstats_100_report.csv`.

---

## Data Analysis and Visualization (Author #2)

The dataset enables multiple forms of advanced musical and market analysis, including:

* **Genre/Label Distribution**: Identifying which genres and labels currently command the Top 100.
* **Artist Collaboration Trends**: Analyzing how many artists contribute to a single trending track.
* **Popularity vs. Longevity**: Using scatter plots to compare "Points" vs "Days on Chart."
* **Sonic Distribution**: Understanding the preferred BPM ranges and Keys for modern electronic music.

### Implemented Visualization Features

- **Top 10 Genres/Labels**: Interactive bar charts showing market dominance.
- **BPM Distribution**: Histogram displaying the most common tempo ranges.
- **Key Distribution**: Pie chart visualizing the frequency of specific musical keys.
- **Points vs Days**: Scatter plot analyzing the correlation between popularity and chart stay.
- **Rising Tracks Tool**: Identification and display of tracks with the highest positive movement.
- **YouTube Playback**: A feature that automatically searches for the #1 song's official music video.

---

## Interface (Tkinter)

The program uses a dual-page Tkinter GUI designed for ease of use during presentations:

### 1. Data Collection Page (HomePage)
* **Start Live Scrape**: Triggers the automated web scraper.
* **Load Existing CSV**: Quickly populates the table using historical data from `data/processed/`.
* **Sortable Table**: View all 100 tracks in a sortable treeview (click headers to sort).

### 2. Analysis Page (AnalysisPage)
* Provides a suite of buttons to launch Matplotlib windows for all data visualizations.
* Provides the "Play Top Song" feature for live demos.

---

## Installation

1. **Clone the repository**:
```bash
git clone [https://github.com/DaviWicks/CS122Project.git](https://github.com/DaviWicks/CS122Project.git)
cd CS122Project

1. Clone the repository:

```
git clone https://github.com/YOUR_USERNAME/CS122Project.git
cd CS122Project
```

2. Create and activate environment:

```
conda create -n cs122 python=3.10
conda activate cs122
```

3. Install dependencies:

```
pip install pandas beautifulsoup4 selenium matplotlib lxml
```

---

## Usage

1. Save the BeatStats Top 100 (All Genres) page source:

   * Open in browser
   * Right click → View Page Source
   * Save as:

     ```
     data/raw/all_genres_chart_source.html
     ```

2. Run the application:

```
python main.py
```

3. In the GUI:

   * Click **Load / Refresh Data**
   * Data will be parsed and CSV files generated automatically
   * Explore the dataset using the table

---

## Output Files

Generated files include:

```
data/raw/all_genres_chart.csv
data/processed/all_genres_chart_clean.csv
data/processed/all_genres_artist_counts.csv
data/processed/all_genres_genre_counts.csv
```

---

## Limitations

BeatStats uses anti-bot protection that prevents direct automated scraping using standard HTTP requests.

To address this, the program parses saved HTML source from publicly accessible chart pages. This ensures reliable data extraction while working within access constraints.

---

## Future Improvements

* Improve visualization integration directly in the GUI
* Automate periodic data updates
* Incorporate additional metadata sources if available
* Integrate real-time data instead of static HTML files
* Embed music playback directly in the application
* Add filtering by genre or artist
* Improve UI design with more advanced layouts
* Expand analysis to include historical trends

---

## Summary

This project transforms raw chart data into a structured dataset that enables meaningful analysis of electronic music trends, including popularity, collaboration patterns, and genre distribution.


