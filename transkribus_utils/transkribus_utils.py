import os
import requests
import lxml.etree as ET
import re

base_url = "https://transkribus.eu/TrpServer/rest"
nsmap = {"page": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}
crowd_base_url = (
    "https://transkribus.eu/r/read/sandbox/application/?colId={}&docId={}&pageId={}"
)


class ACDHTranskribusUtils:
    def login(self, user, pw):
        """log in function
        :param user: Your TRANSKRIBUS user name, e.g. my.mail@whatever.com
        :param pw: Your TRANSKRIBUS password
        :param base_url: The base URL of the TRANSKRIBUS API
        :return: The Session ID in case of a successful log in attempt
        """
        res = requests.post(
            f"{self.base_url}/auth/login", data={"user": user, "pw": pw}
        )
        if res.status_code == 200:
            tree = ET.fromstring(res.content)
            sessionid = tree.xpath("/trpUserLogin/sessionId/text()")
            cookies = dict(JSESSIONID=sessionid[0])
            return cookies
        else:
            return False

    def ft_search(self, **kwargs):
        """ Helper function to interact with TRANSKRIBUS fulltext search endpoint
            :param kwargs: kwargs will be forwarded to TRANSKRIBUS API endpoint e.g. 'query' holds the\
            search string
            :return: The default TRANSKRIBUS response as JSON
        """
        url = f"{self.base_url}/search/fulltext"
        if kwargs:
            querystring = kwargs
        else:
            return False
        querystring["type"] = "LinesLc"
        print(querystring)
        response = requests.request(
            "GET", url, cookies=self.login_cookie, params=querystring
        )
        if response.ok:
            return response.json()
        else:
            return response.ok

    def list_collections(self):
        """Helper function to list all collections
        :return: A dict with listing the collections
        """
        url = f"{self.base_url}/collections/list"
        response = requests.get(url, cookies=self.login_cookie)
        return response.json()

    def list_docs(self, col_id):
        """Helper function to list all documents in a given collection
        :param col_id: Collection ID
        :return: A dict with listing the collections
        """
        url = f"{self.base_url}/collections/{col_id}/list"
        print(url)
        response = requests.get(url, cookies=self.login_cookie)
        return response.json()

    def get_doc_md(self, doc_id, col_id):
        """Helper function to interact with TRANSKRIBUS document metadata endpoint
        :param col_id: The ID of a TRANSKRIBUS Collection
        :param doc_id: The ID of TRANSKRIBUS Document
        :param page_id: The page number of the Document
        :return: A dict with basic metadata of a transkribus Document
        """
        url = f"{self.base_url}/collections/{col_id}/{doc_id}/metadata"
        response = requests.get(url, cookies=self.login_cookie)
        return response.json()

    def get_doc_overview_md(self, doc_id, col_id):
        """Helper function to interact with TRANSKRIBUS document endpoint
        :param col_id: The ID of a TRANSKRIBUS Collection
        :param doc_id: The ID of TRANSKRIBUS Document
        :return: A dict with basic metadata of a transkribus Document
        """
        url = f"{self.base_url}/collections/{col_id}/{doc_id}/fulldoc"
        response = requests.get(url, cookies=self.login_cookie)
        if response.ok:
            result = {}
            result["trp_return"] = response.json()
            page_list = result["trp_return"]["pageList"]["pages"]
            result["pages"] = [
                {
                    "page_id": x["pageId"],
                    "doc_id": x["docId"],
                    "page_nr": x["pageNr"],
                    "thumb": x["thumbUrl"],
                }
                for x in page_list
            ]
            return result
        else:
            return response.ok

    def get_fulldoc_md(self, doc_id, col_id, page_id="1"):
        """Helper function to interact with TRANSKRIBUS document endpoint
        :param col_id: The ID of a TRANSKRIBUS Collection
        :param doc_id: The ID of TRANSKRIBUS Document
        :param page_id: The page number of the Document
        :return: A dict with basic metadata of a transkribus Document
        """
        url = f"{self.base_url}/collections/{col_id}/{doc_id}/{page_id}"
        response = requests.get(url, cookies=self.login_cookie)
        if response.ok:
            doc_xml = ET.fromstring(response.text.encode("utf8"))
            result = {
                "doc_id": doc_id,
                "base_url": self.base_url,
                "col_id": col_id,
                "page_id": page_id,
                "session_id": self.login_cookie["JSESSIONID"],
            }
            result["doc_url"] = url
            result["doc_xml"] = doc_xml
            result["transcript_url"] = doc_xml.xpath(
                "//tsList/transcripts[1]/url/text()"
            )[0]
            result["thumb_url"] = doc_xml.xpath("./thumbUrl/text()")[0]
            result["img_url"] = doc_xml.xpath("./url/text()")[0]
            result["img_url"] = doc_xml.xpath("./url/text()")[0]
            result["extra_info"] = self.get_doc_md(
                doc_id, base_url=self.base_url, col_id=col_id
            )
            return result
        else:
            return response.ok

    def get_transcript(self, fulldoc_md):
        """Helper function to fetch the (latest) fulltext of a TRANSKRIBUS page
        :param fulldoc_md: A dict returned by login.get_fulldoc_md
        :return: The fulldoc_md dict with additional keys 'page_xml' and 'transcript'
        """
        nsmap = {
            "page": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
        }
        md = fulldoc_md
        url = md["transcript_url"]
        response = requests.get(url, cookies=self.login_cookie)
        if response.ok:
            page = ET.fromstring(response.text.encode("utf8"))
            md["page_xml"] = page
            md["transcript"] = page.xpath(
                ".//page:TextLine//page:Unicode/text()", namespaces=nsmap
            )
            return md
        else:
            return response.ok

    def list_documents(self, col_id):
        """Helper function to interact with TRANSKRIBUS collection endpoint to list all documents
        :param col_id: The ID of a TRANSKRIBUS Collection
        :return: A dict with the default TRANSKRIBUS API return
        """
        url = f"{self.base_url}/collections/{col_id}/list"
        response = requests.get(url, cookies=self.login_cookie)
        if response.ok:
            return response.json()
        else:
            return response.ok

    def get_mets(self, doc_id, col_id):
        """Get METS file from Document
        :param col_id: The ID of a TRANSKRIBUS Collection
        :param doc_id: The ID of TRANSKRIBUS Document
        :return: A dict with an lxml object of the mets file and the doc_id
        """
        url = f"{self.base_url}/collections/{col_id}/{doc_id}/mets"
        response = requests.get(url, cookies=self.login_cookie)
        if response.ok:
            result = {
                "doc_xml": ET.fromstring(response.text.encode("utf8")),
                "doc_id": doc_id,
            }
        else:
            result = {"doc_xml": None, "doc_id": doc_id}
        return result

    def save_mets_to_file(self, doc_id, col_id, file_path="."):
        """Saves the METS file of a Document
        :param col_id: The ID of a TRANSKRIBUS Collection
        :param doc_id: The ID of TRANSKRIBUS Document
        :return: The full filename
        """
        mets_dict = self.get_mets(doc_id, col_id)
        file_name = os.path.join(file_path, f"{mets_dict['doc_id']}_mets.xml")
        if os.path.isdir(file_path):
            with open(file_name, "wb") as f:
                f.write(ET.tostring(mets_dict["doc_xml"]))
            return file_name
        else:
            print(f"{file_path} does not exist")
            return None

    def get_image_names(self, doc_id, col_id):
        """Get images names for Document
        :param col_id: The ID of a TRANSKRIBUS Collection
        :param doc_id: The ID of TRANSKRIBUS Document
        :return: a list of images names
        """
        url = f"{self.base_url}/collections/{col_id}/{doc_id}/imageNames"
        response = requests.get(url, cookies=self.login_cookie)
        if response.ok:
            result = response.text.split("\n")
        else:
            result = []
        return result

    def save_image_names_to_file(self, doc_id, col_id, file_path="."):
        """Saves the METS file of a Document
        :param col_id: The ID of a TRANSKRIBUS Collection
        :param doc_id: The ID of TRANSKRIBUS Document
        :return: The full filename
        """
        file_list = self.get_image_names(doc_id, col_id)
        file_name = os.path.join(file_path, f"{doc_id}_image_name.xml")
        root = ET.Element("list")
        counter = 1
        for x in file_list:
            item = ET.Element("item")
            item.attrib["n"] = f"{counter}"
            item.text = x
            root.append(item)
            counter += 1
        if os.path.isdir(file_path):
            with open(file_name, "wb") as f:
                f.write(ET.tostring(root))
            return file_name
        else:
            print(f"{file_path} does not exist")
            return None

    def collection_to_mets(self, col_id, file_path=".", filter_by_doc_ids=[]):
        """Saves METS files of all Documents from a TRANSKRIBUS Collection
        :param col_id: The ID of a TRANSKRIBUS Collection
        :param doc_id: The ID of TRANSKRIBUS Document
        :param filter_by_doc_ids: Only process documents with the passed in IDs
        :return: The full filename
        """
        mpr_docs = self.list_docs(col_id)
        col_dir = os.path.join(file_path, f"{col_id}")
        try:
            os.makedirs(col_dir)
        except FileExistsError:
            pass
        doc_ids = [x["docId"] for x in mpr_docs]
        if filter_by_doc_ids:
            filter_as_int = [int(x) for x in filter_by_doc_ids]
            doc_ids = [x for x in doc_ids if int(x) in filter_as_int]
        print(f"{len(doc_ids)} to download")
        counter = 1
        for doc_id in doc_ids:
            save_mets = self.save_mets_to_file(doc_id, col_id, file_path=col_dir)
            file_list = self.save_image_names_to_file(doc_id, col_id, file_path=col_dir)
            print(f"saving: {save_mets}")
            print(f"saving: {file_list}")
            print(f"{counter}/{len(doc_ids)}")
            counter += 1

        return doc_ids

    def search_for_document(self, title, col_id):
        """Searches for a document with given title in a collection
        :param col_id: The ID of a TRANSKRIBUS Collection
        :param title: Title of the document
        """
        res = requests.get(
            f"{self.base_url}/collections/findDocuments",
            cookies=self.login_cookie,
            params={"collId": col_id, "title": title},
        )
        return res.json()

    def search_for_collection(self, title):
        """Searches for a collection by title
        :param title: Title of the TRANSKRIBUS Collection
        """
        res = requests.get(
            f"{self.base_url}/collections/listByName",
            cookies=self.login_cookie,
            params={"name": title},
            headers={"Accept": "application/json"},
        )
        return res.json()

    def create_collection(self, title):
        """Creates a new collection and returns the collectionId
        :param title: Title of the TRANSKRIBUS Collection
        """
        res = requests.post(
            f"{self.base_url}/collections/createCollection",
            cookies=self.login_cookie,
            params={"collName": title},
        )
        if res.status_code == 200:
            return res.content.decode("utf8")
        else:
            print("error: ", res.status_code, res.content)
            return False

    def get_or_create_collection(self, title):
        """Get or create TRANSKRIBUS collection ID
        :param title: Title of the TRANSKRIBUS Collection
        """
        col = self.search_for_collection(title=title)
        if len(col) == 0:
            col = self.create_collection(title=title)
            return col
        else:
            print(col)
            return col[0]["colId"]

    def upload_mets_file_from_url(self, mets_url, col_id):
        """Takes an URL to a METS file and posts that URL to Transkribus
        :param mets_url: URL of the METS file
        :param col_id: Transkribus CollectionID
        """
        res = requests.post(
            f"{self.base_url}/collections/{col_id}/createDocFromMetsUrl",
            cookies=self.login_cookie,
            params={"fileName": mets_url},
        )
        if res.status_code == 200:
            return True
        else:
            print("Error: ", res.status_code, res.content)
            return False

    def upload_mets_files_from_goobi(
        self, file_titles, check_name=True, col_regex=None, col_id=None
    ):
        """Uploads all file_ids from Goobi via METS in Transkribus
        :param file_titles: Array with file titles to upload
        :param col_id: The ID of a TRANSKRIBUS Collection
        :param check_name (boolean): If set to True checks first if file exist and omits upload if file already exists
        :param col_regex: regex to be used to create collection from file name
        """
        if col_regex is None and col_id is None:
            raise AttributeError("You need to specify either col_regex or col_id")
        pattern = False
        if col_id is None:
            pattern = re.compile(col_regex)
        for f in file_titles:
            if pattern:
                col_name = pattern.match(f)
                col_id = self.get_or_create_collection(col_name.group())
            if check_name:
                s1 = self.search_for_document(f, col_id)
                if len(s1) == 0:
                    self.upload_mets_file_from_url(
                        self.goobi_base_url.format(f), col_id=col_id
                    )

    def __init__(
        self,
        user=None,
        password=None,
        transkribus_base_url=base_url,
        goobi_base_url=None,
    ) -> None:
        if user is None:
            user = os.environ.get("TRANSKRIBUS_USER", None)
            if user is None:
                raise AttributeError(
                    "Transkribus username needs to be set in environments or in init"
                )
        if password is None:
            password = os.environ.get("TRANSKRIBUS_PASSWORD", None)
            if password is None:
                raise AttributeError(
                    "Transkribus password needs to be set in environments or in init"
                )
        if transkribus_base_url is None:
            transkribus_base_url = os.environ.get("TRANSKRIBUS_BASE_URL", None)
            if transkribus_base_url is None:
                raise AttributeError(
                    "Transkribus Base Url needs to be set in environment or init"
                )
        if goobi_base_url is None:
            goobi_base_url = os.environ.get("GOOBI_BASE_URL", None)
            if goobi_base_url is None:
                print("WARNING: Goobi url not set")
        self.base_url = transkribus_base_url
        self.login_cookie = self.login(user, password)
        if goobi_base_url is not None:
            self.goobi_base_url = goobi_base_url + "?id={}"
        else:
            self.goobi_base_url = None
