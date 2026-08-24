from pathlib import Path
import os

import clickhouse_connect
from dotenv import load_dotenv


# syncagent/
# ├── .env
# └── tests/
#     └── test_database.py

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


if __name__ == "__main__":

    client = clickhouse_connect.get_client(
        host=os.environ["CLICKHOUSE_HOST"],
        user=os.environ["CLICKHOUSE_USER"],
        password=os.environ["CLICKHOUSE_PASSWORD"],
        secure=True,
    )

    schema_path = Path(__file__).parent / "schema.sql"

    with open(schema_path, "r", encoding="utf-8") as file:
        query = file.read()

    client.command(query)

    print("tracks table created successfully.")
