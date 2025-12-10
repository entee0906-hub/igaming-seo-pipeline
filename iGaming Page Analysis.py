"""
iGaming Page Analysis
---------------------

Checks whether domains rank for iGaming-related keywords inside Google's top 20,
and evaluates domains based on authority (DR) and traffic thresholds.

Process:
1. Load LinkBuilder export with domain metrics.
2. Filter domains to only likely iGaming sites.
3. Query DataForSEO for top-20 ranking keywords per domain.
4. Check if any ranking keywords match iGaming-related terms.
5. Apply qualification criteria (DR, traffic, keyword relevance).
6. Output results and export CSV.

"""

# =========================================================
# =                        IMPORTS                        =
# =========================================================
import pandas as pd
import requests
import base64
import time


# =========================================================
# =                  CONFIGURATION                        =
# =========================================================
DFS_EMAIL = "admin@wldm.io"
DFS_API_KEY = "cb54e37f6a4874eb"
DFS_BASE_URL = "https://api.dataforseo.com/v3"

# Public CSV URL from LinkBuilder Google Sheet
LINKBUILDER_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1gBEIThc5Lg3ZdkRMe7NQE8o371AlYt6b37rko-rdpsA/export?format=csv"
)

IGAMING_TERMS = ["blackjack", "casino", "poker", "bet", "gambl", "slot"]


# =========================================================
# =                 AUTHENTICATION HEADERS                =
# =========================================================
def get_dfs_headers() -> dict:
    """
    Build DataForSEO HTTP Basic Authentication header.

    Returns
    -------
    dict
        Header containing encoded credentials and JSON content type.
    """
    credentials = f"{DFS_EMAIL}:{DFS_API_KEY}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json",
    }


# =========================================================
# =             DATAFORSEO KEYWORD FETCHING               =
# =========================================================
def get_page_keywords(domain: str) -> list:
    """
    Retrieve ranking keywords (top 20) for a domain from DataForSEO.

    Parameters
    ----------
    domain : str
        Domain name to check.

    Returns
    -------
    list
        List of keywords ranking inside the top 20 positions.
    """
    endpoint = f"{DFS_BASE_URL}/dataforseo_labs/google/ranked_keywords/live"
    payload = [
        {
            "target": domain,
            "location_code": 2840,
            "language_code": "en",
            "limit": 20,
        }
    ]

    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers=get_dfs_headers()
        )

        if response.status_code != 200:
            return []

        data = response.json()
        keywords = []

        tasks = data.get("tasks", [])
        if not tasks:
            return []

        results = tasks[0].get("result", [])
        for item in results:
            for kw_item in item.get("items", []):
                keyword = kw_item.get("keyword_data", {}).get("keyword")
                if keyword:
                    keywords.append(keyword)

        return keywords

    except Exception as exc:
        print(f"Error fetching keywords for {domain}: {exc}")
        return []


# =========================================================
# =                 DOMAIN FILTERING LOGIC                =
# =========================================================
def filter_igaming_domains(df: pd.DataFrame) -> list:
    """
    Filter domains to only those that appear related to iGaming.

    Parameters
    ----------
    df : pd.DataFrame
        LinkBuilder dataset.

    Returns
    -------
    list
        Clean list of iGaming-like domains.
    """
    mask = df["Domain"].str.contains(
        "casino|poker|bet|gambl|slot",
        case=False,
        na=False
    )
    return df[mask]["Domain"].tolist()


# =========================================================
# =                    MAIN ANALYSIS                      =
# =========================================================
def evaluate_domains(domains: list, df: pd.DataFrame) -> list:
    """
    Check each domain for ranking keywords and qualification criteria.

    Parameters
    ----------
    domains : list
        Domains to test (subset or full list).
    df : pd.DataFrame
        Original LinkBuilder dataset containing DR & traffic.

    Returns
    -------
    list
        List of processed result dictionaries.
    """
    results = []

    for domain in domains:
        print(f"Checking: {domain}")

        keywords = get_page_keywords(domain)

        has_igaming_kw = any(
            any(term in kw.lower() for term in IGAMING_TERMS)
            for kw in keywords
        )

        row = df[df["Domain"] == domain].iloc[0]
        dr = row["Domain Rating (DR)"]
        traffic = row["Traffic (Ah)"]

        qualifies = dr >= 20 and traffic >= 1500 and has_igaming_kw
        status = "QUALIFIED" if qualifies else "NOT_QUALIFIED"

        print(
            f"  DR: {dr}, Traffic: {traffic}, "
            f"iGaming in top 20: {has_igaming_kw} -> {status}"
        )

        if has_igaming_kw:
            matched = [
                kw for kw in keywords
                if any(t in kw.lower() for t in IGAMING_TERMS)
            ]
            print(f"  iGaming keywords: {matched[:2]}")

        results.append(
            {
                "Page_URL": f"https://{domain}",
                "Domain": domain,
                "DR": dr,
                "Traffic": traffic,
                "iGaming_In_Top20": has_igaming_kw,
                "Status": status,
            }
        )

        print()
        time.sleep(2)

    return results


# =========================================================
# =                     EXECUTION BLOCK                   =
# =========================================================
if __name__ == "__main__":
    print("Loading iGaming domains...")
    domains_df = pd.read_csv(LINKBUILDER_URL)

    igaming_domains = filter_igaming_domains(domains_df)
    print(f"Found {len(igaming_domains)} iGaming domains")

    test_domains = igaming_domains[:10]
    print(f"Testing {len(test_domains)} iGaming domains...\n")

    results = evaluate_domains(test_domains, domains_df)

    qualified = [r for r in results if r["Status"] == "QUALIFIED"]

    print(f"Domains tested: {len(results)}")
    print(f"Qualified pages: {len(qualified)}")
    print(f"Success rate: {len(qualified) / len(results) * 100:.0f}%")

    if qualified:
        print("\nQUALIFIED PAGES:")
        for entry in qualified:
            print(
                f"- {entry['Page_URL']} "
                f"(DR: {entry['DR']}, Traffic: {entry['Traffic']})"
            )

    # Save results
    pd.DataFrame(results).to_csv("qualified_igaming_pages.csv", index=False)
    print("\nResults saved to: qualified_igaming_pages.csv")
