# Beatport Music Trends Analysis

## Authors

* Davis Nguyen (Data Collection & Organization)
* Gloria B Castro (Analysis & Visualization)

---

## Project Description

This project analyzes electronic music trends using publicly available chart data from BeatStats, which aggregates Beatport Top 100 rankings.

The program extracts chart data such as:

* track rankings
* artists (including multiple artists per track)
* genres
* chart movement (rising tracks)
* popularity (points)
* chart longevity (days)

The data is structured into CSV files and used to analyze trends across genres, artists, and chart performance.

---

## Key Features

* Multi-artist parsing and collaboration analysis
* Genre-based trend analysis across all Top 100 tracks
* Chart movement tracking (rising tracks)
* Track popularity and longevity analysis
* Interactive Tkinter GUI for loading and viewing data
* Sortable data table for user interaction

---

## Data Collection and Storage (Author #1)

Data is collected from publicly accessible BeatStats chart pages.

Due to anti-bot protections that block automated requests, the program parses saved HTML source files from the chart pages using BeautifulSoup. The extracted data includes:

* rank
* rise amount (chart movement)
* artist names
* track title
* genre
* points
* days on chart
* Beatport track link

The cleaned dataset is stored locally in CSV format for further analysis.

---

## Data Analysis and Visualization (Author #2)

The dataset enables multiple forms of analysis, including:

* Most common genres in the Top 100
* Most frequent artists and collaborations
* Tracks with the highest popularity (points)
* Tracks with the longest chart duration (days)
* Rising tracks based on chart movement
* Number of artists per track (collaboration trends)

Visualizations include:

* Bar charts (top artists, genres)
* Histograms (points, days)
* Scatter plots (rank vs days)
* Trend analysis of rising tracks

### Implemented Features

The application includes interactive analysis tools:

- Top 10 genres displayed as a bar chart
- Top 10 artists displayed as a bar chart
- Scatter plot of points vs days on chart
- Scatter plot of rank vs points
- Average points by genre visualization
- Identification of top rising tracks (popup display)
- Ability to open the most popular song in a web browser (YouTube)

These features allow users to explore music trends and identify popular and emerging tracks.

---

## Interface (Tkinter)

The program uses a Tkinter-based GUI with two main pages:

### 1. Data Collection Page

* Load saved chart data
* Automatically generate and update CSV files
* View chart data in a sortable table
* Inspect key metrics and summaries

### 2. Analysis Page

* Provides guidance for visualizations and analysis
* Designed for data exploration and presentation

---

## Installation

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
pip install pandas beautifulsoup4 lxml matplotlib
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


