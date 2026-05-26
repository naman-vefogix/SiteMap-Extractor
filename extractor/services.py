import requests
import xml.etree.ElementTree as ET

def fetch_sitemap(url):

    response = requests.get(url)
    response.raise_for_status()

    return response.text

def parse_sitemap(url):

    xml_data = fetch_sitemap(url)

    root = ET.fromstring(xml_data)

    urls = []

    NAMESPACE = {
    "ns": "http://www.sitemaps.org/schemas/sitemap/0.9"
    }

    # CASE 1 → NORMAL URL SITEMAP
    url_tags = root.findall("ns:url", NAMESPACE)

    if url_tags:

        for url in url_tags:

            loc = url.find("ns:loc", NAMESPACE)

            if loc is not None:
                urls.append(loc.text)

        return urls

    # CASE 2 → SITEMAP INDEX
    sitemap_tags = root.findall("ns:sitemap", NAMESPACE)

    for sitemap in sitemap_tags:

        loc = sitemap.find("ns:loc", NAMESPACE)

        if loc is not None:

            child_sitemap_url = loc.text

            child_urls = parse_sitemap(
                child_sitemap_url
            )

            urls.extend(child_urls)

    return urls