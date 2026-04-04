import re
from urllib.parse import urlparse


def validate_url(url):
    if not url or not isinstance(url, str):
        return None, "URL is required"

    url = url.strip()

    if not url.startswith(("http://", "https://")):
        return None, "URL must start with http:// or https://"

    parsed = urlparse(url)

    if not parsed.netloc:
        return None, "Invalid URL format"

    domain = parsed.netloc.split(":")[0]

    ip_pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
    domain_pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$"

    if not re.match(ip_pattern, domain) and not re.match(domain_pattern, domain):
        return None, "Invalid URL format"

    if not domain.startswith("www.") and not re.match(ip_pattern, domain):
        domain = "www." + domain

    scheme = parsed.scheme
    standardized_url = f"{scheme}://{domain}"

    if parsed.path and parsed.path != "/":
        standardized_url += parsed.path

    if parsed.query:
        standardized_url += f"?{parsed.query}"

    if parsed.fragment:
        standardized_url += f"#{parsed.fragment}"

    return standardized_url, None


def extract_domain(url):
    parsed = urlparse(url)
    return parsed.netloc.split(":")[0]
