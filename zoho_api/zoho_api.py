import os
import httpx
import json

import hashlib
import calendar
import time
from pathlib import Path
import datetime

ZOHO_OAUTH_API_BASE = "https://accounts.zoho.com/oauth/v2"
ZOHO_OAUTHV3_API_BASE = "https://accounts.zoho.com/oauth/v3"
ZOHO_SHEETS_API_BASE = "https://sheet.zoho.com/api/v2"
ZOHO_PROJECTS_API_BASE = "https://projectsapi.zoho.com"


class EmptyInput(Exception):
    """Thrown when an argument value is empty"""

    pass


class InvalidType(Exception):
    """Thrown when the wrong type/instance is used"""

    pass


class InvalidJsonResponse(Exception):
    """Thrown when an invalid/malformed JSON response is received"""

    pass


class UnexpectedResponse(Exception):
    """Thrown when the response received is missing a key we want"""

    pass


class HttpRequestError(Exception):
    """Thrown on the occurrence of an HttpX request error"""

    pass


class MissingData(Exception):
    """Thrown when a requirement is missing"""

    pass


class InvalidCacheTable(Exception):
    """Thrown when the specified cache table doesn't exist"""

    pass


class CorruptedCacheTable(Exception):
    """Thrown when a cache table contains malformed JSON data"""

    pass


# ----------


class ZohoDBCache:
    def __init__(self, hash):
        if not hash:
            raise MissingData("The cache hash is required")
        self.hash = hash
        self.cache_path = f"./.zoho_api/db_cache/{self.hash}"
        Path(f"{self.cache_path}").mkdir(parents=True, exist_ok=True)

    def __wait_till_released(self, table):
        while True:
            if Path(f"{self.cache_path}/{table}.lock").exists():
                time.sleep(1)
                continue
            else:
                break
        return True

    def __lock(self, table):
        open(f"{self.cache_path}/{table}.lock", "a").close()
        return True

    def __release(self, table):
        if Path(f"{self.cache_path}/{table}.lock").exists():
            os.remove(f"{self.cache_path}/{table}.lock")
        return True

    def __release_and_return(self, return_value, table):
        self.__release(table)
        return return_value

    def set(self, table, key, value):
        self.__wait_till_released(table)
        self.__lock(table)
        if not Path(f"{self.cache_path}/{table}.json").exists():
            with open(f"{self.cache_path}/{table}.json", "w") as f:
                data = {}
                data[key] = value
                f.write(json.dumps(data))
                return self.__release_and_return(True, table)
        with open(f"{self.cache_path}/{table}.json", "r") as f:
            try:
                data = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                self.__release(table)
                raise CorruptedCacheTable
            data[key] = value
            with open(f"{self.cache_path}/{table}.json", "w") as fw:
                fw.write(json.dumps(data))
                return self.__release_and_return(True, table)
        return self.__release_and_return(False, table)

    def get(self, table, key):
        if not Path(f"{self.cache_path}/{table}.json").exists():
            raise InvalidCacheTable
        with open(f"{self.cache_path}/{table}.json", "r") as f:
            try:
                data = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                raise CorruptedCacheTable
            if key in data:
                return data[key]
            else:
                return None

    def delete(self, table, key):
        if not Path(f"{self.cache_path}/{table}.json").exists():
            raise InvalidCacheTable
        self.__wait_till_released(table)
        self.__lock(table)
        with open(f"{self.cache_path}/{table}.json", "r") as f:
            try:
                data = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                self.__release(table)
                raise CorruptedCacheTable
            if key in data:
                del data[key]
            else:
                return self.__release_and_return(False, table)
            with open(f"{self.cache_path}/{table}.json", "w") as fw:
                fw.write(json.dumps(data))
                return self.__release_and_return(True, table)
        return self.__release_and_return(False, table)


class ZohoAuthHandler:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        if not self.client_id or not self.client_secret:
            raise MissingData("Missing the Zoho authentication credentials")
        self.hash = hashlib.md5(
            (str(self.client_id) + ":" + str(self.client_secret)).encode("utf-8")
        ).hexdigest()
        self.cache_path = f"./.zoho_api/auth_cache/{self.hash}"
        Path(f"{self.cache_path}").mkdir(parents=True, exist_ok=True)

    def __fetch_token(self):

        request_code_params = {
            "client_id": self.client_id,
            "scope": "ZohoProjects.portals.READ,ZohoProjects.projects.READ,ZohoProjects.documents.READ,ZohoPC.files.READ",
            # "scope":"ZohoProjects.portals.ALL,ZohoProjects.projects.ALL,ZohoProjects.activities.ALL,ZohoProjects.feeds.ALL,ZohoProjects.status.ALL,ZohoProjects.milestones.ALL,ZohoProjects.tasklists.ALL,ZohoProjects.tasks.ALL,ZohoProjects.timesheets.ALL,ZohoProjects.bugs.ALL,ZohoProjects.events.ALL,ZohoProjects.forums.ALL,ZohoProjects.clients.ALL,ZohoProjects.users.ALL,ZohoProjects.documents.READ,ZohoProjects.search.READ,ZohoProjects.tags.ALL,ZohoProjects.calendar.ALL,ZohoProjects.integrations.ALL,ZohoProjects.projectgroups.ALL,ZohoProjects.entity_properties.ALL,ZohoPC.files.ALL,WorkDrive.workspace.ALL,WorkDrive.files.ALL,WorkDrive.team.ALL",
            "grant_type": "device_request",
            "access_type": "offline",
        }

        try:
            response = httpx.post(
                f"{ZOHO_OAUTHV3_API_BASE}/device/code", data=request_code_params
            )
        except httpx.RequestError as e:
            raise HttpRequestError(f"Failed to request device code: {e}")

        try:
            code_data = response.json()
        except ValueError as e:
            raise InvalidJsonResponse(f"Failed to parse the device code response: {e}")

        print(
            f"Please visit this URL and enter the code: {code_data['verification_url']}"
        )
        print(f"User Code: {code_data['user_code']}")

        input("Press Enter after you have authorized the device...")

        request_token_params = [
            f"code={code_data['device_code']}",
            f"client_id={self.client_id}",
            f"client_secret={self.client_secret}",
            "grant_type=device_token",
        ]
        ts = calendar.timegm(time.gmtime())
        try:
            tokenreq = httpx.post(
                f"{ZOHO_OAUTHV3_API_BASE}/device/token?"
                + "&".join(request_token_params)
            )
        except httpx.RequestError as e:
            raise HttpRequestError(f"Failed to request an access token: {e}")
        try:
            tokenres = json.loads(tokenreq.text)
        except json.decoder.JSONDecodeError as e:
            raise InvalidJsonResponse(
                f"Failed to parse the token generation response: {e}"
            )
        if not "access_token" in tokenres:
            raise UnexpectedResponse("Failed to obtain an access token")
        tokenres["created_at"] = ts
        with open(f"{self.cache_path}/token.json", "w") as f:
            f.write(json.dumps(tokenres))
        return tokenres["access_token"]

    def __refresh_token(self, refresh_token):
        req_params = "&".join(
            [
                f"client_id={self.client_id}",
                f"client_secret={self.client_secret}",
                "grant_type=refresh_token",
                f"refresh_token={refresh_token}",
            ]
        )
        ts = calendar.timegm(time.gmtime())
        try:
            req = httpx.post(f"{ZOHO_OAUTH_API_BASE}/token?{req_params}")
        except httpx.RequestError as e:
            raise HttpRequestError(f"Failed to request an access token renewal: {e}")
        try:
            res = json.loads(req.text)
        except json.decoder.JSONDecodeError as e:
            raise InvalidJsonResponse(
                f"Failed to parse the token renewal response: {e}"
            )
        if not "access_token" in res:
            raise UnexpectedResponse("Failed to refresh the access token")
        with open(f"{self.cache_path}/token.json", "r") as f:
            data = json.loads(f.read())
            data["access_token"] = res["access_token"]
            data["created_at"] = ts
            data["expires_in"] = res["expires_in"]
            with open(f"{self.cache_path}/token.json", "w") as fw:
                fw.write(json.dumps(data))
        return res["access_token"]

    def token(self):
        if not Path(f"{self.cache_path}/token.json").exists():
            with open(f"{self.cache_path}/token.json", "w") as f:
                f.write("{}")
        with open(f"{self.cache_path}/token.json", "r") as f:
            data = json.loads(f.read())
            if (
                not "access_token" in data
                or not "refresh_token" in data
                or not "expires_in" in data
                or not "created_at" in data
            ):
                return self.__fetch_token()
            if (int(data["created_at"]) + int(data["expires_in"])) <= calendar.timegm(
                time.gmtime()
            ):
                return self.__refresh_token(data["refresh_token"])
            return data["access_token"]


class ZohoDoc:
    def __init__(
        self,
        AuthHandler,
        portal: str,
        project_name: str,
        file_name: str,
        max_threads=24,
    ):
        if not isinstance(AuthHandler, ZohoAuthHandler):
            raise InvalidType("Invalid ZohoAuthHandler instance passed")
        if not isinstance(portal, str):
            raise InvalidJsonResponse("Invalid workbooks list passed")
        if len(portal) <= 0:
            raise EmptyInput("Couldn't find any workbook names to use")
        self.AuthHandler = AuthHandler
        self.portal = portal
        self.project_name = project_name
        self.file_name = file_name
        self.max_threads = int(max_threads)
        self.hash = hashlib.md5(str(self.portal).encode("utf-8")).hexdigest()
        self.cache = ZohoDBCache(self.hash)

    def __fetch_project_id(self):
        try:
            req = httpx.get(
                f"{ZOHO_PROJECTS_API_BASE}/restapi/portal/{self.portal}/projects/",
                headers={
                    "Authorization": f"Zoho-oauthtoken {self.AuthHandler.token()}"
                },
            )
        except httpx.RequestError as e:
            raise HttpRequestError(f"Failed to fetch the project ID: {e}")
        res = json.loads(req.text)

        for project in res["projects"]:
            if project["name"] == self.project_name:
                return project["id"]

    def __fetch_project_docs(self):
        projectId = self.__fetch_project_id()
        try:
            req = httpx.get(
                f"{ZOHO_PROJECTS_API_BASE}/restapi/portal/{self.portal}/projects/{projectId}/documents/",
                headers={
                    "Authorization": f"Zoho-oauthtoken {self.AuthHandler.token()}"
                },
            )
        except httpx.RequestError as e:
            raise HttpRequestError(f"Failed to fetch the project ID: {e}")
        res = json.loads(req.text)
        return res

    def __get_document_link(self):
        documents_list = dict(self.__fetch_project_docs())
        for dicts in documents_list["dataobj"]:
            res_name = dicts.get("res_name")
            if res_name == self.file_name:
                docs_download_url = dicts.get("docs_download_url")
                return docs_download_url

    def download_document(self):
        url = self.__get_document_link()
        req = httpx.get(
            url,
            headers={"Authorization": f"Zoho-oauthtoken {self.AuthHandler.token()}"},
        )

        with open(
            f'./downloads_xlsx/{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}_{self.file_name}.xlsx',
            "wb",
        ) as xlsx:
            xlsx.write(req.content)

        return xlsx.name
