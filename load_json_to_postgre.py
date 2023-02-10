import pandas as pd
from sqlalchemy import create_engine, String, Integer
import os
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import ARRAY

load_dotenv()

# Create SQLALchemy database engine
db_url = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
    os.environ.get("DATABASE_USERNAME"),
    os.environ.get("DATABASE_PASSWORD"),
    os.environ.get("DATABASE_HOST"),
    os.environ.get("DATABASE_PORT"),
    os.environ.get("DATABASE_NAME"),
)
engine = create_engine(db_url, echo=False)

# Read data from json file
DATA_PATH = "data/random_data.json"
df = pd.read_json(DATA_PATH, lines=True, dtype=True)

# Specify metadata types (important)
types = {
    "id": Integer,
    "title": String,
    "link": String,
    "authors": String,
    "references": ARRAY(Integer),
    "year": Integer,
}

# Executed only once after the first migration to load data to PostgreSQL
df.to_sql(name="article", if_exists="fail", index=False, dtype=types, con=engine)
