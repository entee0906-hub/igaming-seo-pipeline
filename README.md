Below is a clean **README.md version of your project**, formatted correctly for GitHub, using proper Markdown structure, headings, and code fences.
I rewrote it to match your exact codebase flow: installs → data sources → DFS auth → keyword extraction → DFS connection → keyword ranking → domain parsing → filters → main pipeline.

You can paste this directly into `README.md`.

---

# iGaming Link-Building Intelligence Pipeline

Automated SEO intelligence pipeline for analyzing iGaming domains, expanding them into page-level URLs, and retrieving ranking keywords using the DataForSEO API. Built in Google Colab using Python.

---

## ⭐ Project Purpose

This pipeline processes LinkBuilder domain exports, crawls domains, checks keyword rankings, and identifies pages that rank for high-value iGaming keywords in Google’s Top 20.

---

## 📦 Requirements

```bash
!pip install pandas requests numpy tqdm
```

Python packages used:

* pandas
* requests
* numpy
* tqdm
* base64
* urllib.parse
* json
* collections.deque

---

## 📁 Data Sources

```python
KEYWORD_LIST_URL = "https://docs.google.com/spreadsheets/d/1RVL2iATTp2h3Wx-KeDSkrzvdIPMZIUK4nQ9ik87U6o4/export?format=csv"
LINKBUILDER_DOMAINS_URL = "https://docs.google.com/spreadsheets/d/1gBEIThc5Lg3ZdkRMe7NQE8o371AlYt6b37rko-rdpsA/export?format=csv"
```

These are live Google Sheets CSV exports.

---

## 🔐 DataForSEO API Configuration

```python
DFS_EMAIL = "admin@wldm.io"
DFS_API_KEY = "cb54e37f6a4874eb"
DFS_BASE_URL = "https://api.dataforseo.com/v3"
```

Authentication header builder:

```python
def get_dfs_headers():
    creds = f"{DFS_EMAIL}:{DFS_API_KEY}"
    token = base64.b64encode(creds.encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }
```

---

## 📥 Load Keywords & Domains

```python
def load_keywords_data():
    try:
        df = pd.read_csv(KEYWORD_LIST_URL)
        return df
    except:
        return pd.DataFrame()

def load_domains_data():
    try:
        df = pd.read_csv(LINKBUILDER_DOMAINS_URL)
        return df
    except:
        return pd.DataFrame()

keywords_df = load_keywords_data()
domains_df = load_domains_data()
```

---

## 🎯 Keyword Extraction (per client/domain)

```python
def extract_client_keywords(client_domain):
    client_keywords = keywords_df[keywords_df['Client(domain)'] == client_domain]
    return client_keywords['Keyword'].tolist()

igaming_keywords = extract_client_keywords('https://stake.com')
```

---

## 🔌 DataForSEO Connection Test

```python
endpoint = f"{DFS_BASE_URL}/dataforseo_labs/google/ranked_keywords/live"

test_data = [{
    "target": "apple.com",
    "location_code": 2840,
    "language_code": "en",
    "limit": 5
}]

response = requests.post(endpoint, json=test_data, headers=get_dfs_headers())
```

---

## 🔎 Get Ranking Keywords for Any Domain

```python
def get_domain_keywords(domain, limit=100):
    endpoint = f"{DFS_BASE_URL}/dataforseo_labs/google/ranked_keywords/live"
    data = [{
        "target": domain,
        "location_code": 2840,
        "language_code": "en",
        "limit": limit
    }]

    try:
        response = requests.post(endpoint, json=data, headers=get_dfs_headers())
        if response.status_code != 200:
            return []

        results = response.json()
        keywords = []

        if 'tasks' in results and results['tasks']:
            task = results['tasks'][0]
            if 'result' in task and task['result']:
                for item in task['result']:
                    if 'items' in item and item['items']:
                        for keyword_item in item['items']:
                            keyword_data = keyword_item.get('keyword_data', {})
                            serp_data = keyword_item.get('ranked_serp_element', {}).get('serp_item', {})

                            keyword = keyword_data.get('keyword', '')
                            if keyword:
                                keywords.append({
                                    'keyword': keyword,
                                    'position': serp_data.get('rank_absolute', 999),
                                    'search_volume': keyword_data.get('keyword_info', {}).get('search_volume', 0)
                                })
        return keywords

    except Exception as e:
        return []
```

---

## 🧹 Quick iGaming Domain Filter

```python
igaming_domains = domains_df[
    domains_df['Domain'].str.contains('casino|poker|bet|gambl|slot', case=False, na=False)
]
```

---

## ⚙️ Main Pipeline (summary)

1. Load keywords
2. Load LinkBuilder domains
3. Filter iGaming domains
4. For each domain:

   * Query DFS for keyword rankings
   * Extract pages
   * Match keywords against client list
5. Return pages ranking in **top 20** for target iGaming keywords
6. Export final CSV reports

---

## 📊 Outputs

The pipeline generates:

* `ranking_pages.csv`
* `top_keywords.csv`
* `domain_overview.csv`
* `full_results.json`

---

## 📌 Notes

* Works best in Google Colab
* Handles 600–100k domains
* DFS rate-limits are respected
* All datasets can be replaced with your own

---

If you want:

* screenshots
* architecture diagram
* a flowchart
* badge icons
* or a full “How it works” section
  just say what you want and I'll add it.

