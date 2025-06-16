import requests
import json

API_KEY = "f828a52f2080498dacd9513ccf67d8bc"
crypto = ""
RESULTS = {}
def get_news(crypto):
    url = f"https://newsapi.org/v2/everything?q={crypto}&language=en&pageSize=5&sortBy=publishedAt&apiKey={API_KEY}"
    response = requests.get(url)
    data = response.json()  
    # Save only the articles (optionally include the keyword)
    RESULTS[crypto] = data.get("articles", [])
    # Save all results to a JSON file
    with open("crypto_news.json", "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, indent=2, ensure_ascii=False)
    print("News data saved to crypto_news.json")
    return []

def get_github_contributors(repo_url):
    # Example: https://github.com/ethereum/go-ethereum
    if "github.com" not in repo_url:
        return []

    parts = repo_url.rstrip("/").split("/")
    owner, repo = parts[-2], parts[-1]
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    
    response = requests.get(api_url)
    if response.status_code != 200:
        return []

    contributors = response.json()
    return [c["login"] for c in contributors[:5]]  # Top 5 contributors

# Example:
repo = "https://github.com/ethereum/go-ethereum"
top_devs = get_github_contributors(repo)
print("Top Contributors:", top_devs)