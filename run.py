import datetime
import pandas as pd
from zoho_api import zoho_api
from tables_comparsion import print_result
from tg_api import escape_markup, sendMessage

handler = zoho_api.ZohoAuthHandler(
    "1004.DCAJ27VKACCGNEPOYF04EVAR1JYJ6T", "87028a1c9efa37c677293dc02cfa54ac2fadb75669"
)
portals = zoho_api.ZohoDoc(
    handler, "678002754", "nScan dla PLAY", "Serwery_NQP_V1_08_18_2020.xlsx"
)
with open("./csv/last_document_flag.txt") as flag_file:
    beforelast_mtime_csv = f"{flag_file.read()}"
df = pd.read_excel(portals.download_document(), engine="calamine")
last_mtime_csv = f'./csv/{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
df.to_csv(last_mtime_csv, index=False)
comparsion_result = print_result(beforelast_mtime_csv, last_mtime_csv, "role")
with open("./csv/last_document_flag.txt", "w") as flag_file:
    flag_file.write(last_mtime_csv)
final_tg_msg = escape_markup(comparsion_result, "markdownv2")
sendMessage(final_tg_msg)
