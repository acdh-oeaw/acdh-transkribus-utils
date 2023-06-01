import requests


def get_title_from_iiif(iiif_url: str, label_key: str = "label") -> str:
    """ returns the manifests label"""
    r = requests.get(iiif_url)
    label = iiif_url
    if r.status_code == 200:
        label = r.json().get(label_key, iiif_url)
    return label
