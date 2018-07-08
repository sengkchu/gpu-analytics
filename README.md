# GPU Analytics

Data analytics dashboard for various GPUs. This app was created with Python and Dash, hosted at [heroku.com](https://gpuanalytics.herokuapp.com).

![application](https://raw.githubusercontent.com/sengkchu/gpu-analytics/master/app_preview.png)

Based on a web scrape of [PCPartPicker](https://pcpartpicker.com/) and [PassMark](https://www.videocardbenchmark.net/) into a SQLite database.

<center>
![schema](https://raw.githubusercontent.com/sengkchu/gpu-analytics/master/db_schema.png)
</center>

### Repo Contents:

+ `app.py` 	The application code, contains front-end layouts, logic for graphs, SQL queries to interface with the database.
+ `gpudata.db` SQLite database to act as the backend for the app. Designed to be small and compact (~5 MB) to fit into this repo. 
+ `gpu_scraper.py` Python code for web scraping PCPartPicker and PassMark.
+ `gpudata_scraper.ipynb` IPython notebook for the web scraper.
+ `gpudatabase_interface.ipynb` IPython notebook for SQL queries.
+ `Procfile` for hosting on heroku only.
+ `requirements.txt` python package requirements for this application.

### Running the App Locally (Windows):

+ Clone this repository.
+ Create virtual environment `python -m virtualenv venv`.
+ Start virtual environment `venv\Scripts\Activate`. 
+ Install packages `pip install -r requirements.txt`.
+ Start the application `python app.py`.
+ Enter http://localhost:5000/ in your web browser to use the application locally.

### Running the App Locally (macOS and Linux):

+ Clone this repository.
+ Create virtual environment `python3 -m virtualenv venv`.
+ Start virtual environment `source  venv/bin/activate`. 
+ Install packages `pip install -r requirements.txt`.
+ Start the application `python3 app.py`.
+ Enter http://localhost:5000/ in your web browser to use the application locally.
