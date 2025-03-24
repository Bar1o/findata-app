api_tickers = ["SBER", "VTBR", "MGNT", "SMLT", "SVCB", "OKEY", "CBOM", "TATN", "ASTR"]  # 10
missing_tickers = ["YDEX", "OZON", "LENT", "GAZP", "HEAD", "PIKK", "X5", "LSRG", "MSTT", "ROSN", "LKOH", "NVTK", "T"]

sectors = ["tech", "retail", "banks", "oil", "build"]
all_tickers = api_tickers + missing_tickers

tech = ["YDEX", "HEAD", "VKCO", "ASTR"]
retail = ["MGNT", "OZON", "LENT", "X5", "OKEY"]
banks = ["SBER", "T", "SVCB", "VTBR", "CBOM"]
build = ["SMLT", "PIKK", "LSRG", "MSTT"]
oil = ["GAZP", "ROSN", "LKOH", "NVTK", "TATN"]
