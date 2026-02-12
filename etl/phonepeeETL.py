import os
import json
import psycopg2


class PhonePeETL:
    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
        self.cur = self.conn.cursor()
        print("Database connected")

    def close_db(self):
        self.conn.commit()
        self.cur.close()
        self.conn.close()
        print("Database connection closed")

    def load_aggregated_data(self, base_path, table_name, data_type):
        for state in os.listdir(base_path):
            for year in os.listdir(os.path.join(base_path, state)):
                year_path = os.path.join(base_path, state, year)

                for file in os.listdir(year_path):
                    if not file.endswith(".json"):
                        continue

                    quarter = int(file.replace(".json", ""))
                    with open(os.path.join(year_path, file), "r") as f:
                        data = json.load(f)

                    if not data.get("data"):
                        continue

                   
                    if data_type in ["transaction", "insurance"] and "transactionData" in data["data"]:
                        for item in data["data"]["transactionData"]:
                            name = item["name"]
                            count = item["paymentInstruments"][0]["count"]
                            amount = item["paymentInstruments"][0]["amount"]

                            self.cur.execute(f"""
                                INSERT INTO {table_name}
                                (state, year, quarter, transaction_type, transaction_count, transaction_amount)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (state, year, quarter, transaction_type) DO NOTHING;
                            """, (state, year, quarter, name, count, amount))

                    
                    elif data_type == "user" and data.get("data") and data["data"].get("usersByDevice"):
                        for item in data["data"]["usersByDevice"]:
                            self.cur.execute("""
                                INSERT INTO aggregated_user
                                (state, year, quarter, brand, user_count, percentage)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (state, year, quarter, brand) DO NOTHING;
                            """, (state, year, quarter, item["brand"], item["count"], item["percentage"]))

    def load_map_data(self, base_path, table_name, data_type):
        for state in os.listdir(base_path):
            for year in os.listdir(os.path.join(base_path, state)):
                year_path = os.path.join(base_path, state, year)

                for file in os.listdir(year_path):
                    if not file.endswith(".json"):
                        continue

                    quarter = int(file.replace(".json", ""))
                    with open(os.path.join(year_path, file), "r") as f:
                        data = json.load(f)

                    if not data.get("data"):
                        continue

                    if data_type in ["transaction", "insurance"] and "hoverDataList" in data["data"]:
                        for item in data["data"]["hoverDataList"]:
                            self.cur.execute(f"""
                                INSERT INTO {table_name}
                                (state, year, quarter, district, count, amount)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (state, year, quarter, district) DO NOTHING;
                            """, (state, year, quarter, item["name"], item["metric"][0]["count"], item["metric"][0]["amount"]))

                    elif data_type == "user" and "hoverData" in data["data"]:
                        for district, val in data["data"]["hoverData"].items():
                            self.cur.execute("""
                                INSERT INTO map_user
                                (state, year, quarter, district, registered_users, app_opens)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (state, year, quarter, district) DO NOTHING;
                            """, (state, year, quarter, district, val["registeredUsers"], val["appOpens"]))

    def load_top_data(self, base_path, table_name, data_type):
        for state in os.listdir(base_path):
            for year in os.listdir(os.path.join(base_path, state)):
                year_path = os.path.join(base_path, state, year)

                for file in os.listdir(year_path):
                    if not file.endswith(".json"):
                        continue

                    quarter = int(file.replace(".json", ""))
                    with open(os.path.join(year_path, file), "r") as f:
                        data = json.load(f)

                    if not data.get("data"):
                        continue

                    if data_type in ["transaction", "insurance"] and "districts" in data["data"]:
                        for item in data["data"]["districts"]:
                            self.cur.execute(f"""
                                INSERT INTO {table_name}
                                (state, year, quarter, district, count, amount)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (state, year, quarter, district) DO NOTHING;
                            """, (state, year, quarter, item["entityName"], item["metric"]["count"], item["metric"]["amount"]))

                    elif data_type == "user" and "pincodes" in data["data"]:
                        for item in data["data"]["pincodes"]:
                            self.cur.execute("""
                                INSERT INTO top_user
                                (state, year, quarter, pincode, registered_users)
                                VALUES (%s, %s, %s, %s, %s)
                                ON CONFLICT (state, year, quarter, pincode) DO NOTHING;
                            """, (state, year, quarter, item["name"], item["registeredUsers"]))



if __name__ == "__main__":
    db_config = {
        "host": "localhost",
        "database": "phonepe",
        "user": "postgres",
        "password": "root"
    }

    etl = PhonePeETL(db_config)

    aggregated_sets = [
        (r"C:\Users\ASUS\Desktop\Phonepe_project\data\aggregated\transaction\country\india\state", "aggregated_transaction", "transaction"),
        (r"C:\Users\ASUS\Desktop\Phonepe_project\data\aggregated\insurance\country\india\state", "aggregated_insurance", "insurance"),
        (r"C:\Users\ASUS\Desktop\Phonepe_project\data\aggregated\user\country\india\state", "aggregated_user", "user")
    ]

    map_sets = [
        (r"C:\Users\ASUS\Desktop\Phonepe_project\data\map\transaction\hover\country\india\state", "map_transaction", "transaction"),
        (r"C:\Users\ASUS\Desktop\Phonepe_project\data\map\insurance\hover\country\india\state", "map_insurance", "insurance"),
        (r"C:\Users\ASUS\Desktop\Phonepe_project\data\map\user\hover\country\india\state", "map_user", "user")
    ]

    top_sets = [
        (r"C:\Users\ASUS\Desktop\Phonepe_project\data\top\transaction\country\india\state", "top_transaction", "transaction"),
        (r"C:\Users\ASUS\Desktop\Phonepe_project\data\top\insurance\country\india\state", "top_insurance", "insurance"),
        (r"C:\Users\ASUS\Desktop\Phonepe_project\data\top\user\country\india\state", "top_user", "user")
    ]

    for p, t, d in aggregated_sets:
        etl.load_aggregated_data(p, t, d)

    for p, t, d in map_sets:
        etl.load_map_data(p, t, d)

    for p, t, d in top_sets:
        etl.load_top_data(p, t, d)

    etl.close_db()