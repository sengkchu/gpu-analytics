# GPU Analytics

Data analytics dashboard for various GPUs. This app was created with Python and Dash, hosted on my website at https://gpuanalytics.codingdisciple.com/.

For a static version of this app hosted on heroku.com [click here](https://gpuanalytics.herokuapp.com). 

![application](https://raw.githubusercontent.com/sengkchu/gpu-analytics/master/app_preview.png)

Based on a web scrape of [PCPartPicker](https://pcpartpicker.com/) and [PassMark](https://www.videocardbenchmark.net/) into a SQLite database.

<p align="center">
  <img src="https://raw.githubusercontent.com/sengkchu/gpu-analytics/master/db_schema.png", alt='Schema'>
</p>

### Repo Contents:

+ server_files: Files used in conjunction with apache2 and wsgi to serve the app on a VPS. This folder is not required to run the application locally.
    + appdata
        + `gpu_scraper.py` Python script for scraping data on a VPS.
        + `gpudata.db` Empty database file.
        + `worker.py` Python script to run `gpu_scraper.py` every day at 00:10 Pacific time. 
    + var/www/FlaskApp
        + `FlaskApp.wsgi` WSGI file to serve the application on a VPS.
        + FlaskApp 
            + `__init__.py` The application code.
	+ `FlaskApp.conf` Configuration file for the application.
    
+ `app.py` 	The application code, contains front-end layouts, logic for graphs, SQL queries to interface with the database.
+ `gpudata.db` SQLite database to act as the backend for the app. Designed to be small and compact (~5 MB) to fit into this repo. 
+ `gpu_scraper.py` Python code for web scraping PCPartPicker and PassMark locally
+ `gpudata_scraper.ipynb` IPython notebook for the web scraper.
+ `gpudatabase_interface.ipynb` IPython notebook for testing out SQL queries, SQL tables are created here.
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

### Running the App on a VPS (Ubuntu/Digital Ocean/Cloudflare):
Check my website for a tutorial coming soon! https://codingdisciple.com/.
