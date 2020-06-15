import os
import json
import requests
import lxml.etree as ET

base_url = "https://transkribus.eu/TrpServer/rest"
nsmap = {
    "page": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
}
crowd_base_url = "https://transkribus.eu/r/read/sandbox/application/?colId={}&docId={}&pageId={}"


def trp_login(user, pw, base_url=base_url):
    """ log in function
        :param user: Your TRANSKRIBUS user name, e.g. my.mail@whatever.com
        :param pw: Your TRANSKRIBUS password
        :param base_url: The base URL of the TRANSKRIBUS API
        :return: The Session ID in case of a successful log in attempt
    """
    url = "{}/auth/login".format(base_url)
    payload = "user={}&pw={}".format(user, pw)
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        }
    response = requests.request("POST", url, data=payload, headers=headers)
    if response.ok:
        session_id = response.text.split('<sessionId>')[1].split('</sessionId>')[0]
        return session_id
    else:
        response.ok


def trp_ft_search(user, pw, base_url=base_url, **kwargs):
    """ Helper function to interact with TRANSKRIBUS fulltext search endpoint
        :param user: Your TRANSKRIBUS user name, e.g. my.mail@whatever.com
        :param pw: Your TRANSKRIBUS password
        :param base_url: The base URL of the TRANSKRIBUS API
        :param kwargs: kwargs will be forwarded to TRANSKRIBUS API endpoint e.g. 'query' holds the\
        search string
        :return: The default TRANSKRIBUS response as JSON
    """
    url = f"{base_url}/search/fulltext"
    if kwargs:
        querystring = kwargs
    else:
        return False
    querystring['type'] = "LinesLc"
    print(querystring)
    session_id = trp_login(user, pw, base_url=base_url)
    headers = {
        'cookie': "JSESSIONID={}".format(session_id),
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.ok:
        return response.json()
    else:
        return response.ok


def trp_list_collections(user, pw, base_url=base_url):
    """ Helper function to list all collections
        :param base_url: The base URL of the TRANSKRIBUS API
        :param user: Your TRANSKRIBUS user name, e.g. my.mail@whatever.com
        :param pw: Your TRANSKRIBUS password
        :return: A dict with listing the collections
    """
    url = f"{base_url}/collections/list"
    session_id = trp_login(user, pw, base_url=base_url)
    headers = {
        'cookie': "JSESSIONID={}".format(session_id),
    }
    response = requests.request("GET", url, headers=headers)
    return response.json()


def trp_list_docs(col_id, user, pw, base_url=base_url):
    """ Helper function to list all documents in a given collection
        :param col_id: Collection ID
        :param base_url: The base URL of the TRANSKRIBUS API
        :param user: Your TRANSKRIBUS user name, e.g. my.mail@whatever.com
        :param pw: Your TRANSKRIBUS password
        :return: A dict with listing the collections
    """
    url = f"{base_url}/collections/{col_id}/list"
    print(url)
    session_id = trp_login(user, pw, base_url=base_url)
    headers = {
        'cookie': "JSESSIONID={}".format(session_id),
    }
    response = requests.request("GET", url, headers=headers)
    return response.json()


def trp_get_doc_md(doc_id, col_id, user, pw, base_url=base_url):
    """ Helper function to interact with TRANSKRIBUS document metadata endpoint
        :param user: Your TRANSKRIBUS user name, e.g. my.mail@whatever.com
        :param pw: Your TRANSKRIBUS password
        :param base_url: The base URL of the TRANSKRIBUS API
        :param col_id: The ID of a TRANSKRIBUS Collection
        :param doc_id: The ID of TRANSKRIBUS Document
        :param page_id: The page number of the Document
        :return: A dict with basic metadata of a transkribus Document
    """
    url = f"{base_url}/collections/{col_id}/{doc_id}/metadata"
    session_id = trp_login(user, pw, base_url=base_url)
    headers = {
        'cookie': "JSESSIONID={}".format(session_id),
    }
    response = requests.request("GET", url, headers=headers)
    return response.json()


def trp_get_doc_overview_md(doc_id, col_id, user, pw, base_url=base_url):
    """ Helper function to interact with TRANSKRIBUS document endpoint
        :param user: Your TRANSKRIBUS user name, e.g. my.mail@whatever.com
        :param pw: Your TRANSKRIBUS password
        :param base_url: The base URL of the TRANSKRIBUS API
        :param col_id: The ID of a TRANSKRIBUS Collection
        :param doc_id: The ID of TRANSKRIBUS Document
        :return: A dict with basic metadata of a transkribus Document
    """
    url = f"{base_url}/collections/{col_id}/{doc_id}/fulldoc"
    session_id = trp_login(user, pw, base_url=base_url)
    headers = {
        'cookie': "JSESSIONID={}".format(session_id),
    }
    response = requests.request("GET", url, headers=headers)
    if response.ok:
        result = {}
        result["trp_return"] = response.json()
        page_list = result["trp_return"]["pageList"]["pages"]
        result["pages"] = [
            {
                "page_id": x['pageId'],
                "doc_id": x['docId'],
                "page_nr": x['pageNr'],
                "thumb": x['thumbUrl']
            } for x in page_list
        ]
        return result
    else:
        return response.ok


def trp_get_fulldoc_md(doc_id, col_id, user, pw, base_url=base_url, page_id="1"):
    """ Helper function to interact with TRANSKRIBUS document endpoint
        :param user: Your TRANSKRIBUS user name, e.g. my.mail@whatever.com
        :param pw: Your TRANSKRIBUS password
        :param base_url: The base URL of the TRANSKRIBUS API
        :param col_id: The ID of a TRANSKRIBUS Collection
        :param doc_id: The ID of TRANSKRIBUS Document
        :param page_id: The page number of the Document
        :return: A dict with basic metadata of a transkribus Document
    """
    url = f"{base_url}/collections/{col_id}/{doc_id}/{page_id}"
    session_id = trp_login(user, pw, base_url=base_url)
    headers = {
        'cookie': "JSESSIONID={}".format(session_id),
    }
    response = requests.request("GET", url, headers=headers)
    if response.ok:
        doc_xml = ET.fromstring(response.text.encode('utf8'))
        result = {
            "doc_id": doc_id,
            "base_url": base_url,
            "col_id": col_id,
            "page_id": page_id,
            "session_id": session_id
        }
        result["doc_url"] = url
        result["doc_xml"] = doc_xml
        result["transcript_url"] = doc_xml.xpath('//tsList/transcripts[1]/url/text()')[0]
        result["thumb_url"] = doc_xml.xpath('./thumbUrl/text()')[0]
        result["img_url"] = doc_xml.xpath('./url/text()')[0]
        result["img_url"] = doc_xml.xpath('./url/text()')[0]
        result["extra_info"] = trp_get_doc_md(
            doc_id, base_url=base_url, col_id=col_id, user=user, pw=pw
        )
        return result
    else:
        return response.ok


def get_transcript(fulldoc_md):
    """ Helper function to fetch the (latest) fulltext of a TRANSKRIBUS page
        :param fulldoc_md: A dict returned by trp_login.trp_get_fulldoc_md
        :return: The fulldoc_md dict with additional keys 'page_xml' and 'transcript'
    """
    nsmap = {
        "page": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
    }
    md = fulldoc_md
    url = md['transcript_url']
    headers = {
        'cookie': "JSESSIONID={}".format(md['session_id']),
    }
    response = requests.request("GET", url, headers=headers)
    if response.ok:
        page = ET.fromstring(response.text.encode('utf8'))
        md['page_xml'] = page
        md['transcript'] = page.xpath(
            './/page:TextLine//page:Unicode/text()', namespaces=nsmap
        )
        return md
    else:
        return response.ok


def list_documents(col_id, user, pw, base_url=base_url):
    """ Helper function to interact with TRANSKRIBUS collection endpoint to list all documents
        :param user: Your TRANSKRIBUS user name, e.g. my.mail@whatever.com
        :param pw: Your TRANSKRIBUS password
        :param base_url: The base URL of the TRANSKRIBUS API
        :param col_id: The ID of a TRANSKRIBUS Collection
        :return: A dict with the default TRANSKRIBUS API return
    """
    url = f"{base_url}/collections/{col_id}/list"
    session_id = trp_login(user, pw, base_url=base_url)
    headers = {
        'cookie': "JSESSIONID={}".format(session_id),
    }
    response = requests.request("GET", url, headers=headers)
    if response.ok:
        return response.json()
    else:
        return response.ok


def trp_get_mets(doc_id, col_id, user, pw, base_url=base_url):
    """ Get METS file from Document
        :param user: Your TRANSKRIBUS user name, e.g. my.mail@whatever.com
        :param pw: Your TRANSKRIBUS password
        :param base_url: The base URL of the TRANSKRIBUS API
        :param col_id: The ID of a TRANSKRIBUS Collection
        :param doc_id: The ID of TRANSKRIBUS Document
        :return: A dict with an lxml object of the mets file and the doc_id
    """
    url = f"{base_url}/collections/{col_id}/{doc_id}/mets"
    session_id = trp_login(user, pw, base_url=base_url)
    headers = {
        'cookie': "JSESSIONID={}".format(session_id),
    }
    response = requests.request("GET", url, headers=headers)
    if response.ok:
        result = {
            "doc_xml": ET.fromstring(response.text.encode('utf8')),
            "doc_id": doc_id
        }
    else:
        result = {
            "doc_xml": None,
            "doc_id": doc_id
        }
    return result


def trp_save_mets_to_file(doc_id, col_id, user, pw, file_path=".", base_url=base_url):
    """ Saves the METS file of a Document
        :param user: Your TRANSKRIBUS user name, e.g. my.mail@whatever.com
        :param pw: Your TRANSKRIBUS password
        :param base_url: The base URL of the TRANSKRIBUS API
        :param col_id: The ID of a TRANSKRIBUS Collection
        :param doc_id: The ID of TRANSKRIBUS Document
        :return: The full filename
    """
    mets_dict = trp_get_mets(doc_id, col_id, user, pw, base_url=base_url)
    file_name = os.path.join(file_path, f"{mets_dict['doc_id']}_mets.xml")
    if os.path.isdir(file_path):
        with open(file_name, 'wb') as f:
            f.write(ET.tostring(mets_dict["doc_xml"]))
        return file_name
    else:
        print(f"{file_path} does not exist")
        return None


def trp_collection_to_mets(col_id, user, pw, file_path=".", base_url=base_url):
    """ Saves METS files of all Documents from a TRANSKRIBUS Collection
        :param user: Your TRANSKRIBUS user name, e.g. my.mail@whatever.com
        :param pw: Your TRANSKRIBUS password
        :param base_url: The base URL of the TRANSKRIBUS API
        :param col_id: The ID of a TRANSKRIBUS Collection
        :param doc_id: The ID of TRANSKRIBUS Document
        :return: The full filename
    """
    mpr_docs = trp_list_docs(col_id, user, pw)
    col_dir = os.path.join(file_path, f"{col_id}")
    try:
        os.makedirs(col_dir)
    except FileExistsError:
        pass
    doc_ids = [x['docId'] for x in mpr_docs]
    print(f"{len(doc_ids)} to download")
    counter = 1
    for doc_id in doc_ids:
        save_mets = trp_save_mets_to_file(
            doc_id, col_id, user, pw, file_path=col_dir, base_url=base_url
        )
        print(f"saving: {save_mets}")
        print(f"{counter}/{len(doc_ids)}")
        counter += 1

    return doc_ids
