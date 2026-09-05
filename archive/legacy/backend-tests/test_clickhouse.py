import os
import clickhouse_connect
from dotenv import load_dotenv

load_dotenv()

host = os.environ["CLICKHOUSE_HOST"]
user = os.environ["CLICKHOUSE_USER"]
password = os.environ["CLICKHOUSE_PASSWORD"]

print("Testing ClickHouse...")
print("Host:", host)
print("User:", user)

client = clickhouse_connect.get_client(
    host=host,
    # port=8443,
    username=user,
    password=password,
    secure=True,
    # verify=True,
    connect_timeout=10,
    send_receive_timeout=30,
)

print("Connected!")

result = client.query("SELECT 1")

print("Query result:")
print(result.result_rows)

print("Databases:")

result = client.query("SHOW DATABASES")

for row in result.result_rows:
    print(row)
