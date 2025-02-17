import os
import argparse
import datetime
import pandas as pd
from time import sleep
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

handler = zoho_api.ZohoAuthHandler(CLIENT_ID, CLIENT_SECRET)
portals = zoho_api.ZohoDoc(handler, PORTAL, PROJECT_NAME, FILE_NAME)

parser_valid_args = {"--first", "--start"}
parser = argparse.ArgumentParser(
    description="This program is designed for automatically downloading, comparing, and analyzing data from a Zoho document, then sending the results to Telegram."
)
parser.add_argument("start", help="run the program")
parser.add_argument(
    "--first", help="use at first start", nargs="?", metavar="", const=True
)
parser.add_argument(
    "--interval",
    help="update interval in hours",
    nargs="?",
    type=int,
    const=12,
    metavar="12",
)
args = parser.parse_args()


def first():
    df = pd.read_excel(portals.download_document(), engine="calamine")
    last_mtime_csv = f'./csv/{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(last_mtime_csv, index=False)
    with open("./csv/last_document_flag.txt", "w") as flag_file:
        flag_file.write(last_mtime_csv)


def run(interval_hours: int = 12):
    interval_hours = interval_hours * 60 * 60
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
    sleep(interval_hours)


# Start
if args.start == "start" and args.first is not True and args.interval is None:
    sendMessage("Running with 12 hours interval")
    while True:
        run()

# First start
if args.start == "start" and args.first is True and args.interval is None:
    sendMessage("Running with 12 hours interval")
    first()
    while True:
        run()

# Start + interval / no first start
if args.start == "start" and args.interval is not None and args.first is not True:
    sendMessage(f"Running with {args.interval} hours interval")
    while True:
        run(args.interval)

# First start with interval
if args.start == "start" and args.interval is not None and args.first is True:
    sendMessage(f"Running with {args.interval} hours interval")
    first()
    while True:
        run(args.interval)
