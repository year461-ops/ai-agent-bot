# 新建一個 test_data.py 貼上以下內容並執行
from tools import get_stock_report

# 測試美股
print("--- 測試美股 TSM ---")
us_res = get_stock_report("TSM")
print(us_res)

# 測試台股
print("\n--- 測試台股 2330 ---")
tw_res = get_stock_report("2330")
print(tw_res)