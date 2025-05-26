from urllib.parse import urlparse

def remove_duplicate_links(links):
    unique_links = {}
    for link in links:
        href = link.get("href", "").split("#")[0]  # Remove fragment identifiers
        if href and href not in unique_links:
            unique_links[href] = link
    return list(unique_links.values())

def extract_links(links):
    return [link["href"] for link in links if "href" in link]


def classify_url(url: str) -> str:
    parsed_url = urlparse(url)

    # Check if the path is empty or just a slash
    if parsed_url.path in ["", "/"]:
        return "Website"
    return "Web Page"
