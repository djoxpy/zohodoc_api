import httpx
import re

TOKEN = "7770779855:AAFZZVHZGU0hNYroh5Qdo12Ena1gfFpZ1P8"
TG_API = "https://api.telegram.org"
PARSE_MODE = "markdownv2"


def escape_markup(text: str, mode: str) -> str:
    if mode == "markdown":
        return re.sub(r"([_*\[`])", r"\\\1", text)

    elif mode == "markdownv2":
        return re.sub(r"([\[\]()~>#+\-=|{}.!])", r"\\\1", text)

    elif mode == "html":
        return re.sub(r"<(\s|[^a-z\/])", r"&lt;\1", text)

    return text


def fetch_bot_data():
    req = httpx.get(f"{TG_API}/bot{TOKEN}/getMe")
    print(req.json())
    return req


def getUpdates():
    req = httpx.post(f"{TG_API}/bot{TOKEN}/getUpdates")
    print(req.json())
    return req


def sendMessage(text):
    req = httpx.post(
        f"{TG_API}/bot{TOKEN}/sendMessage",
        json={"chat_id": "-4718639012", "text": text, "parse_mode": PARSE_MODE},
    )

    return req
