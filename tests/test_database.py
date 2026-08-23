from pathlib import Path
import os

import clickhouse_connect
from dotenv import load_dotenv


# syncagent/
# ├── .env
# └── tests/
#     └── test_database.py

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env.example"

load_dotenv(ENV_FILE)


if __name__ == "__main__":
    # print("HOST:", repr(os.getenv("CLICKHOUSE_HOST")))
    # print("USER:", repr(os.getenv("CLICKHOUSE_USER")))
    # print("PASSWORD EXISTS:", bool(os.getenv("CLICKHOUSE_PASSWORD")))

    client = clickhouse_connect.get_client(
        host=os.environ["CLICKHOUSE_HOST"],
        user=os.environ["CLICKHOUSE_USER"],
        password=os.environ["CLICKHOUSE_PASSWORD"],
        secure=True,
    )

    result = client.query("SELECT version()")

    print("Connected to ClickHouse!")
    print("Version:", result.result_rows)
