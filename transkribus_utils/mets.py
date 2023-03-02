from acdh_xml_pyutils.xml import XMLReader


def get_title_from_mets(mets_url, title_xpaht=".//mods:title/text()"):
    doc = XMLReader(mets_url)
    nsmap = doc.nsmap
    nsmap['mets'] = "http://www.loc.gov/METS/"
    nsmap["mods"] = "http://www.loc.gov/mods/v3"
    tree = doc.tree
    mets_title = tree.xpath(title_xpaht, namespaces=nsmap)[0]
    return mets_title
