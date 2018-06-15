import sqlite3
from config import DB

def run_query(q):
    with sqlite3.connect(DB) as conn:
        return pd.read_sql(q,conn)

def run_command(c):
    with sqlite3.connect(DB) as conn:
        conn.execute('PRAGMA foreign_keys = ON;')
        conn.isolation_level = None
        conn.execute(c)
        
def run_inserts(c, values):
    with sqlite3.connect(DB) as conn:
        conn.execute('PRAGMA foreign_keys = ON;')
        conn.isolation_level = None
        conn.execute(c, values) 
        
def show_tables():
    q = '''
    SELECT
        name,
        type
    FROM sqlite_master
    WHERE type IN ("table","view");
    '''
    return run_query(q)
	
	
#Create the reviews table
c1 = """
CREATE TABLE reviews(
    review_id INTEGER PRIMARY KEY,
    anime_id INTEGER,
    username TEXT,
    review_date TEXT, 
    episodes_seen TEXT,
    overall_rating INT,
    story_rating INT,
    animation_rating INT,
    sound_rating  INT,
    character_rating INT,
    helpful_counts INT,
    enjoyment_rating INT,
    review_body TEXT,
    FOREIGN KEY(anime_id) REFERENCES animes(anime_id)  
); 
"""

run_command(c1)
