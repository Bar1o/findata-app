# run from backend
# PYTHONPATH=. python -m services.paper_data.external_use
from .paper_data_db import PaperDataDBManager

db_manager = PaperDataDBManager()

assets_data = db_manager.check_assets_table()
print(assets_data)
