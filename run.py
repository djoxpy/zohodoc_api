import os
import datetime
import pandas as pd
from zoho_api import zoho_api
from tables_comparsion import print_result
from tg_api import escape_markup, sendMessage
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
PORTAL = os.getenv("PORTAL")
PROJECT_NAME = os.getenv("PROJECT_NAME")
FILE_NAME = os.getenv("FILE_NAME")

handler = zoho_api.ZohoAuthHandler(
    CLIENT_ID, CLIENT_SECRET
)
portals = zoho_api.ZohoDoc(
    handler, PORTAL, PROJECT_NAME, FILE_NAME
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
