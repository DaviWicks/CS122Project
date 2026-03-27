# Project Title

Beatport Music Trends Analysis

## Authors

* Davis Nguyen (Author #1)
* Partner Name (Author #2)

## Project Description

This project analyzes electronic music trends using publicly available chart data from Beatport. The program will collect data such as track rankings, artists, genres, and BPM from Beatport charts. The data will be stored locally and organized for easy access and updates. Using this data, the project will identify trends such as popular genres, recurring artists, and tempo patterns. Finally, the program will generate visualizations to help users better understand how electronic music trends evolve over time.

## Project Outline / Plan

* Collect Beatport chart data (Top 100 or genre-specific charts)
* Clean and store the data in CSV format
* Build a user interface to explore the data
* Analyze trends such as artist frequency and BPM distribution
* Generate visualizations (graphs and charts)
* Test and refine the program
* Prepare final submission and presentation

## Interface Plan

The interface will allow users to explore Beatport chart data through an interactive system. A main page will allow users to select a genre or chart type. A second page will display detailed statistics and visualizations. The interface will include at least four widgets such as:

* Buttons to load or refresh chart data
* Dropdown menu to select genre or chart
* Search bar for artist or track name
* Button to generate visualizations

## Data Collection and Storage Plan (Author #1)

Data will be collected from publicly accessible Beatport charts using Python tools such as `requests` and `BeautifulSoup`. The program will extract relevant information including track titles, artist names, rankings, genres, and BPM where available. The collected data will be cleaned and stored locally in CSV files to ensure it can be reused without repeatedly accessing the website. The storage structure will allow for easy updates and organization by chart type or genre. My role will focus on gathering the data efficiently and maintaining a clean, structured dataset.

## Data Analysis and Visualization Plan (Author #2)

The second author will analyze the collected data using Python libraries such as `pandas` and `numpy`. The analysis will focus on identifying trends such as the most frequent artists, dominant genres, and BPM distributions. Visualizations such as bar charts, line graphs, and histograms will be created using `matplotlib`. These visuals will help users interpret patterns in the data. This portion of the project will focus on transforming raw data into meaningful insights.

## Future Improvements

* Expand analysis across multiple genres
* Track trends over time (weekly/monthly charts)
* Add more advanced visualizations
* Improve user interface design
* Automate data updates

## Installation

1. Clone the repository
2. Install required Python libraries
3. Run the main program file

## License

This project is licensed under the MIT License.
