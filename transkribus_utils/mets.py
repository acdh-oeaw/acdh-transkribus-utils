from acdh_xml_pyutils.xml import XMLReader

GOOBI_IIIF_PATTERN = "https://viewer.acdh.oeaw.ac.at/viewer/api/v1/records/{}/files/images/{}/full/full/0/default.jpg"  # noqa


def get_title_from_mets(mets_url, title_xpaht=".//mods:title/text()"):
    doc = XMLReader(mets_url)
    nsmap = doc.nsmap
    nsmap['mets'] = "http://www.loc.gov/METS/"
    nsmap["mods"] = "http://www.loc.gov/mods/v3"
    tree = doc.tree
    mets_title = tree.xpath(title_xpaht, namespaces=nsmap)[0]
    return mets_title


def replace_img_urls_in_mets(mets_url, replacement_pattern=GOOBI_IIIF_PATTERN):
    doc = XMLReader(mets_url)
    nsmap = doc.nsmap
    nsmap['mets'] = "http://www.loc.gov/METS/"
    nsmap["mods"] = "http://www.loc.gov/mods/v3"
    nsmap["xlink"] = "http://www.w3.org/1999/xlink"
    new_uris = []
    for x in doc.tree.xpath(".//mets:fileGrp[@USE='PRESENTATION']//mets:FLocat/@xlink:href", namespaces=nsmap):
        collection_id, image_id = x.split('/')[-2:]
        new_uri = replacement_pattern.format(collection_id, image_id)
        new_uris.append(new_uri)
    for i, x in enumerate(doc.tree.xpath(".//mets:fileGrp[@USE='DEFAULT']//mets:FLocat", namespaces=nsmap)):
        x.attrib["{http://www.w3.org/1999/xlink}href"] = new_uris[i]
    return doc.return_string()
