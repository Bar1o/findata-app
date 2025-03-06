# run from backend
# PYTHONPATH=. python -m services.paper_data.external_use
from .paper_data_db import PaperDataDBManager

db_manager = PaperDataDBManager()

# assets_data = db_manager.check_assets_table()
# print(assets_data.columns)
# print(assets_data[["ticker", "name", "figi"]])

print(db_manager.get_uid_by_ticker("SBER"))
print(db_manager.get_ticker_by_uid("40d89385-a03a-4659-bf4e-d3ecba011782"))
