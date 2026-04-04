import re
from urllib.parse import urlparse

SUSPICIOUS_WORDS = [
    "login",
    "signin",
    "secure",
    "account",
    "verify",
    "update",
    "confirm",
    "banking",
    "password",
    "credential",
    "authenticate",
    "authorize",
    "ebayisapi",
    "webscr",
    "cmd",
    "signin",
    "wallet",
    "transfer",
    "phishing",
    "hack",
    "steal",
    "fake",
    "scam",
]

OBFUSCATION_CHARS = set("@01!|")


def extract_features(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    domain = parsed.netloc
    path = parsed.path
    full_url = url

    url_length = len(full_url)

    domain_parts = domain.split(".")
    tld = domain_parts[-1] if domain_parts else ""
    tld_length = len(tld)

    subdomains = [p for p in domain_parts if p not in ("www", "") and p != tld]
    no_of_subdomain = len(subdomains)

    domain_without_tld = (
        ".".join(domain_parts[:-1]) if len(domain_parts) > 1 else domain
    )
    domain_length = len(domain_without_tld)

    is_domain_ip = (
        1 if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain.split(":")[0]) else 0
    )

    no_of_letters = sum(1 for c in full_url if c.isalpha())
    letter_ratio = round(no_of_letters / url_length, 3) if url_length > 0 else 0.0

    no_of_digits = sum(1 for c in full_url if c.isdigit())
    digit_ratio = round(no_of_digits / url_length, 3) if url_length > 0 else 0.0

    no_of_equals = full_url.count("=")
    no_of_qmark = full_url.count("?")
    no_of_ampersand = full_url.count("&")

    special_char_pattern = r"[^a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%]"
    special_chars = re.findall(special_char_pattern, full_url)
    no_of_other_special_chars = len(special_chars)
    special_char_ratio = (
        round(no_of_other_special_chars / url_length, 3) if url_length > 0 else 0.0
    )

    obfuscated_chars = sum(1 for c in domain if c in OBFUSCATION_CHARS)
    has_obfuscation = 1 if obfuscated_chars > 0 else 0
    no_of_obfuscated_char = obfuscated_chars
    obfuscation_ratio = (
        round(obfuscated_chars / len(domain), 3) if len(domain) > 0 else 0.0
    )

    is_https = 1 if url.startswith("https") else 0

    url_lower = full_url.lower()
    bank = 1 if any(w in url_lower for w in ["bank", "banca", "banque"]) else 0
    pay = 1 if "pay" in url_lower else 0
    crypto = (
        1 if any(w in url_lower for w in ["crypto", "coin", "bitcoin", "wallet"]) else 0
    )
    suspicious_words = sum(1 for w in SUSPICIOUS_WORDS if w in url_lower)

    path_parts = [p for p in path.split("/") if p]
    url_depth = len(path_parts)

    tokens = re.split(r"[-._~:/?#\[\]@!$&'()*+,;=]+", full_url)
    tokens = [t for t in tokens if t]
    avg_token_length = (
        round(sum(len(t) for t in tokens) / len(tokens), 3) if tokens else 0.0
    )

    return {
        "URLLength": url_length,
        "DomainLength": domain_length,
        "IsDomainIP": is_domain_ip,
        "TLDLength": tld_length,
        "NoOfSubDomain": no_of_subdomain,
        "NoOfLettersInURL": no_of_letters,
        "LetterRatioInURL": letter_ratio,
        "NoOfDigitsInURL": no_of_digits,
        "DigitRatioInURL": digit_ratio,
        "NoOfEqualsInURL": no_of_equals,
        "NoOfQMarkInURL": no_of_qmark,
        "NoOfAmpersandInURL": no_of_ampersand,
        "NoOfOtherSpecialCharsInURL": no_of_other_special_chars,
        "SpecialCharRatioInURL": special_char_ratio,
        "HasObfuscation": has_obfuscation,
        "NoOfObfuscatedChar": no_of_obfuscated_char,
        "ObfuscationRatio": obfuscation_ratio,
        "IsHTTPS": is_https,
        "Bank": bank,
        "Pay": pay,
        "Crypto": crypto,
        "SuspiciousWords": suspicious_words,
        "URLDepth": url_depth,
        "AvgTokenLength": avg_token_length,
    }
