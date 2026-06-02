import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}

# client ip & country for db 
def get_ip_location(ip_address):
    try:
        url = f"https://api.ip2location.io/?ip={ip_address}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            location_info= {
                "IP": data.get("ip"),
                "Country Code": data.get("country_code"),
                "Country Name": data.get("country_name")
            }
            return {"status":True,"country":location_info['Country Name']}
        else:
            return {"status":False}
    except:
        return {"status": False}

def get_user_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # Get the first IP in the list
    else:
        ip = request.META.get('REMOTE_ADDR')  # Default IP address
    result=get_ip_location(ip)
    if result["status"]:
        country=result["country"]
        ip=f'{ip}-{country}'
    return ip


def normalize_domain(url: str) -> str:
    """
    Always store/lookup by bare domain regardless of what user passed.

    examples:
        https://vefogix.com
        https://vefogix.com/sitemap.xml
        https://vefogix.com/robots.txt

    all will become:
        https://vefogix.com
    """
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def fetch_sitemap(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )
    response.raise_for_status()
    return response.content


def get_tag_name(tag):
    return tag.split("}")[-1]


def extract_sitemaps_from_robots(robots_url: str) -> list[str]:
    """
    Read robots.txt and extract all Sitemap: URLs.
    """

    response = requests.get(
        robots_url,
        headers=HEADERS,
        timeout=10
    )
    response.raise_for_status()
    sitemaps = []
    for line in response.text.splitlines():
        line = line.strip()
        if line.lower().startswith("sitemap:"):
            sitemap_url = line.split(":", 1)[1].strip()
            if sitemap_url:
                sitemaps.append(sitemap_url)
    return sitemaps


def resolve_sitemap_urls(user_input: str) -> list[str]:
    """
    floww:
    1. https://vefogix.com
       -> robots.txt first
       -> fallback sitemap.xml
    2. https://vefogix.com/robots.txt
       -> extract Sitemap entries
    3. https://vefogix.com/sitemap.xml
       -> use directly
    4. https://www.lockeremporium.com/xmlsitemap.php 
       -> use directly  
    """

    url = user_input.strip().rstrip("/")

    # User supplied directllyyyy robots.txt
    if url.endswith("/robots.txt"):
        sitemaps = extract_sitemaps_from_robots(url)
        if not sitemaps:
            raise Exception(
                "No Sitemap entries found in robots.txt"
            )
        return sitemaps

    # User supplied directly sitemap.xml
    if url.endswith(".xml"):
        return [url]
    
    # User supplied directly sitemap.xml
    if url.endswith("xmlsitemap.php"):
        return [url]

    # User supplied domain
    robots_url = f"{url}/robots.txt"
    try:
        sitemaps = extract_sitemaps_from_robots(robots_url)
        if sitemaps:
            print(f"[INFO] Found {len(sitemaps)} sitemap(s) in robots.txt")
            return sitemaps
    except Exception as e:
        print(f"[INFO] robots.txt failed: {e}")

    # Fallback
    fallback = f"{url}/sitemap.xml"
    print(f"[INFO] Falling back to {fallback}")
    return [fallback]


def parse_sitemap(url,visited=None,urls=None,max_urls=None):
    if visited is None:
        visited = set()

    if urls is None:
        urls = []

    if url in visited:
        return urls

    if max_urls is not None and len(urls) >= max_urls:
        return urls

    visited.add(url)

    xml_data = fetch_sitemap(url)

    try:
        root = ET.fromstring(xml_data)

    except ET.ParseError:
        # Plain text sitemap support
        text = xml_data.decode("utf-8",errors="ignore")

        for line in text.split():
            if max_urls is not None and len(urls) >= max_urls:
                return urls
            line = line.strip()
            if line.startswith(("http://", "https://")):
                urls.append(line)

        return urls

    for child in root:

        if max_urls is not None and len(urls) >= max_urls:
            return urls
        tag_name = get_tag_name(child.tag)

        # Sitemap index or xmlsitemap.php
        if tag_name == "sitemap" or tag_name == "xmlsitemap.php":
            for item in child:
                if get_tag_name(item.tag) == "loc":
                    child_sitemap = item.text.strip()
                    try:
                        parse_sitemap(child_sitemap,visited=visited,urls=urls,max_urls=max_urls)
                    except Exception as e:
                        print(f"FAILED: {child_sitemap} -> {e}")
                        continue
        
        # URL sitemap
        elif tag_name == "url":
            for item in child:
                if get_tag_name(item.tag) == "loc":
                    urls.append(item.text.strip())
                    if (max_urls is not None and len(urls) >= max_urls):
                        return urls

    return urls