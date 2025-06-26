import random
import requests
from datetime import datetime
import time
import logging
from textblob import TextBlob
from sklearn.ensemble import IsolationForest
import numpy as np
from . import keystore

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize global cache for Ethereum's volume-to-market-cap ratio
ethereum_ratio_cache = None

score_header = [
    "Trading Volume Consistency",
    "Liquidity & Order Book Depth",
    "Token Age & Market History",
    "Developer & Team Transparency",
    "Smart Contract Audit & Security",
    "Exchange Listings & Reputation",
    "Community & Social Media Presence",
    "Transaction Patterns & Anomalies",
    "Whitepaper & Roadmap Execution",
    "Regulatory Compliance & Legal Standing",
    "Sentiment Analysis",
    "Anomaly Detection Score"
]

# Load API keys
COINGECKO_DEMO_API_KEY = keystore.load_api_key('CoinGecko', 'CGKEY')
GITHUB_TOKEN = keystore.load_api_key('GitHub', 'GITHUB_TOKEN')
NEWSAPI_KEY = "f828a52f2080498dacd9513ccf67d8bc"

if not COINGECKO_DEMO_API_KEY:
    raise ValueError("COINGECKO_DEMO_API_KEY is required in settings.cfg")

# Cache for symbol to coin ID mapping
symbol_to_coin_id_cache = {}
def get_coin_id(symbol):
    """Map a coin symbol to its CoinGecko coin ID."""
    symbol = symbol.upper()
    if symbol in symbol_to_coin_id_cache:
        return symbol_to_coin_id_cache[symbol]
    
    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/coins/list',
            params={'x_cg_demo_api_key': COINGECKO_DEMO_API_KEY}
        )
        response.raise_for_status()
        coins = response.json()
        for coin in coins:
            if coin['symbol'].upper() == symbol:
                symbol_to_coin_id_cache[symbol] = coin['id']
                return coin['id']
        logger.warning(f"No CoinGecko coin ID found for symbol {symbol}")
        return None
    except requests.RequestException as e:
        logger.error(f"Error fetching coin list: {e}")
        return None

def fetch_news_headlines(symbol):
    """Fetch news headlines using NewsAPI."""
    try:
        url = f"https://newsapi.org/v2/everything?q={symbol}&language=en&pageSize=5&sortBy=publishedAt&apiKey={NEWSAPI_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])
        return [article["title"] for article in articles if "title" in article]
    except Exception as e:
        logger.error(f"Failed to fetch news for {symbol}: {e}")
        return [f"No recent news available for {symbol}"]

def get_sentiment_score(symbol):
    """Perform sentiment analysis on fetched headlines."""
    headlines = fetch_news_headlines(symbol)
    scores = []
    for text in headlines:
        blob = TextBlob(text)
        scores.append(blob.sentiment.polarity)
    if not scores:
        return 5
    avg_score = sum(scores) / len(scores)
    if avg_score >= 0.5:
        return 10
    elif avg_score >= 0.25:
        return 8
    elif avg_score >= 0.1:
        return 6
    elif avg_score >= 0:
        return 4
    else:
        return 2

def fetch_transaction_data(symbol):
    """Fetch transaction data from CoinGecko and prepare it for anomaly detection."""
    try:
        coin_id = symbol_to_coin_id_cache.get(symbol)
        if not coin_id:
            # fallback to API search if not cached
            list_url = f"https://api.coingecko.com/api/v3/coins/list?x_cg_demo_api_key={COINGECKO_DEMO_API_KEY}"
            resp = requests.get(list_url)
            resp.raise_for_status()
            for coin in resp.json():
                if coin['symbol'].lower() == symbol.lower():
                    coin_id = coin['id']
                    symbol_to_coin_id_cache[symbol] = coin_id
                    break
            if not coin_id:
                raise ValueError(f"CoinGecko ID not found for {symbol}")

        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=1&x_cg_demo_api_key={COINGECKO_DEMO_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        prices = [p[1] for p in data.get('prices', [])]
        volumes = [v[1] for v in data.get('total_volumes', [])]
        combined = np.column_stack((prices, volumes))
        return combined[:50]  # limit to 50 samples
    except Exception as e:
        logger.error(f"Failed to fetch transaction data from CoinGecko for {symbol}: {e}")
        return np.array([[random.uniform(0, 1) for _ in range(2)] for _ in range(50)])

def detect_anomalies(symbol):
    """Use Isolation Forest to detect anomalies in mock transaction data."""
    try:
        data = fetch_transaction_data(symbol)
        model = IsolationForest(contamination=0.1)
        preds = model.fit_predict(data)
        anomaly_ratio = sum(preds == -1) / len(preds)
        if anomaly_ratio <= 0.05:
            return 10
        elif anomaly_ratio <= 0.1:
            return 8
        elif anomaly_ratio <= 0.2:
            return 6
        elif anomaly_ratio <= 0.3:
            return 4
        return 2
    except Exception as e:
        logger.error(f"Error in anomaly detection for {symbol}: {e}")
        return 3
def make_coingecko_request(url, retries=3, backoff_factor=2):
    """Make a CoinGecko API request with retry logic for rate limits."""
    params = {'x_cg_demo_api_key': COINGECKO_DEMO_API_KEY}
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            if response.status_code == 429:
                wait_time = backoff_factor ** attempt
                logger.warning(f"Rate limit hit for {url}. Retrying after {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"HTTP error for {url}: {e}")
                raise
        except requests.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            raise
    raise Exception(f"Failed to fetch {url} after {retries} attempts")

def make_github_request(url, retries=3, backoff_factor=2):
    """Make a GitHub API request with retry logic for rate limits."""
    headers = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}
    headers['Accept'] = 'application/vnd.github+json'
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            if response.status_code in [403, 429]:
                wait_time = backoff_factor ** attempt
                logger.warning(f"GitHub rate limit hit for {url}. Retrying after {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"HTTP error for {url}: {e}")
                raise
        except requests.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            raise
    raise Exception(f"Failed to fetch {url} after {retries} attempts")

def score_trading_volume_consistency(volume_24h, market_cap):
    """Score trading volume consistency relative to Ethereum's volume-to-market-cap ratio."""
    global ethereum_ratio_cache

    if not volume_24h or not market_cap or volume_24h == 'N/A' or market_cap == 'N/A':
        logger.warning(f"Invalid volume_24h ({volume_24h}) or market_cap ({market_cap})")
        return 1

    try:
        # Calculate coin's ratio
        coin_volume = float(str(volume_24h).replace(',', ''))
        coin_market_cap = float(str(market_cap).replace(',', ''))
        if coin_market_cap == 0:
            logger.warning("Market cap is zero, cannot compute ratio")
            return 1
        coin_ratio = coin_volume / coin_market_cap
        logger.debug(f"Coin ratio for volume/market_cap: {coin_ratio:.6f}")

        # Fetch Ethereum's ratio if not cached
        if ethereum_ratio_cache is None:
            url = 'https://api.coingecko.com/api/v3/coins/ethereum'
            response = make_coingecko_request(url)
            data = response.json()
            eth_volume = data.get('market_data', {}).get('total_volume', {}).get('usd', 0)
            eth_market_cap = data.get('market_data', {}).get('market_cap', {}).get('usd', 0)
            if eth_market_cap == 0:
                logger.error("Ethereum market cap is zero, cannot compute ratio")
                return 1
            ethereum_ratio_cache = eth_volume / eth_market_cap
            logger.debug(f"Ethereum ratio cached: {ethereum_ratio_cache:.6f}")

        # Avoid division by zero
        if ethereum_ratio_cache == 0:
            logger.error("Ethereum ratio is zero, cannot compute relative score")
            return 1

        # Compute relative ratio
        relative_ratio = (coin_ratio / ethereum_ratio_cache) * 100  # As percentage
        logger.debug(f"Relative ratio to Ethereum: {relative_ratio:.2f}%")

        # Score based on relative ratio
        if relative_ratio >= 100:
            return 10
        elif relative_ratio >= 90:
            return 9
        elif relative_ratio >= 80:
            return 8
        elif relative_ratio >= 70:
            return 7
        elif relative_ratio >= 60:
            return 6
        elif relative_ratio >= 50:
            return 5
        elif relative_ratio >= 40:
            return 4
        elif relative_ratio >= 30:
            return 3
        elif relative_ratio >= 20:
            return 2
        elif relative_ratio >= 10:
            return 1
        return 0

    except (ValueError, TypeError, KeyError) as e:
        logger.error(f"Error calculating trading volume consistency: {e}")
        return 0
    except requests.RequestException as e:
        logger.error(f"Error fetching Ethereum data: {e}")
        return 0
def score_market_cap_liquidity(market_cap):
    """Score market cap liquidity, handling blank or invalid inputs."""
    if not market_cap or market_cap == 'N/A':
        logger.warning(f"Invalid market_cap ({market_cap})")
        return 0
    try:
        market_cap = float(str(market_cap).replace(',', ''))
        if market_cap >= 10_000_000_000:
            return 10
        elif market_cap >= 1_000_000_000:
            return 8
        elif market_cap >= 100_000_000:
            return 6
        elif market_cap >= 10_000_000:
            return 4
        return 0
    except (ValueError, TypeError) as e:
        logger.error(f"Error calculating market cap liquidity: {e}")
        return 0

def score_token_age(date_added):
    """Score token age, handling blank or invalid dates."""
    if not date_added or date_added == 'N/A':
        logger.warning(f"Invalid date_added ({date_added})")
        return 1
    try:
        delta = (datetime.now() - datetime.strptime(date_added, '%Y-%m-%d')).days
        if delta >= 1825:
            return 10
        elif delta >= 1460:
            return 9
        elif delta >= 1095:
            return 8
        elif delta >= 730:
            return 7
        elif delta >= 365:
            return 6
        elif delta >= 270:
            return 5
        elif delta >= 180:
            return 4
        elif delta >= 120:
            return 3
        return 2
    except (ValueError, TypeError) as e:
        logger.error(f"Error calculating token age: {e}")
        return 0

def score_developer_transparency(symbol):
    """Score developer transparency using GitHub's REST API."""
    try:
        # Search for repositories related to the cryptocurrency
        search_url = 'https://api.github.com/search/repositories'
        query = f"{symbol} topic:cryptocurrency"
        response = make_github_request(f"{search_url}?q={query}&sort=stars&per_page=1")
        data = response.json()
        items = data.get('items', [])
        if not items:
            logger.info(f"No GitHub repositories found for symbol {symbol}")
            return 3

        repo = items[0]
        owner = repo['owner']['login']
        repo_name = repo['name']
        
        # Fetch recent commits (last 100 to avoid excessive API calls)
        commits_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits?per_page=100"
        commits_resp = make_github_request(commits_url)
        commits = commits_resp.json()
        commit_count = len(commits)

        time.sleep(1)  # Respect GitHub rate limits

        if commit_count >= 100:
            return 10
        elif commit_count >= 50:
            return 8
        elif commit_count >= 20:
            return 6
        return 4
    except requests.RequestException as e:
        logger.error(f"Error fetching GitHub data for {symbol}: {e}")
        return 3

def score_contract_audit(symbol):
    """Score contract audit based on CoinGecko data."""
    coin_id = get_coin_id(symbol)
    if not coin_id:
        return 3
    try:
        url = f'https://api.coingecko.com/api/v3/coins/{coin_id}'
        response = make_coingecko_request(url)
        data = response.json()

        links = data.get('links', {})
        homepage = links.get('homepage', [''])
        repos = links.get('repos_url', {}).get('github', [])

        platforms = data.get('platforms', {})
        contracts_present = bool(platforms)

        score = 2
        if contracts_present:
            score += 4
        if repos:
            score += 2
        if homepage:
            score += 2

        return min(score, 10)
    except requests.RequestException as e:
        logger.error(f"Error fetching contract audit data for {symbol}: {e}")
        return 3

def score_exchange_listings(symbol):
    """Score exchange listings based on CoinGecko tickers."""
    coin_id = get_coin_id(symbol)
    if not coin_id:
        return 3
    try:
        url = f'https://api.coingecko.com/api/v3/coins/{coin_id}'
        response = make_coingecko_request(url)
        tickers = response.json().get('tickers', [])
        count = len(tickers)
        if count >= 50:
            return 10
        elif count >= 20:
            return 8
        elif count >= 10:
            return 6
        return 4
    except requests.RequestException as e:
        logger.error(f"Error fetching exchange listings for {symbol}: {e}")
        return 3

def score_social_media_presence(symbol):
    """Score social media presence based on CoinGecko community data."""
    coin_id = get_coin_id(symbol)
    if not coin_id:
        return 3
    try:
        url = f'https://api.coingecko.com/api/v3/coins/{coin_id}'
        response = make_coingecko_request(url)
        data = response.json()
        community_data = data.get('community_data', {})
        followers = community_data.get('twitter_followers', 0)
        if followers >= 100000:
            return 10
        elif followers >= 50000:
            return 8
        elif followers >= 10000:
            return 6
        return 4
    except requests.RequestException as e:
        logger.error(f"Error fetching social media presence for {symbol}: {e}")
        return 3

def score_transaction_patterns(symbol):
    """Score transaction patterns using CoinGecko's 24-hour trading volume."""
    coin_id = get_coin_id(symbol)
    if not coin_id:
        logger.warning(f"No CoinGecko coin ID found for symbol {symbol}")
        return 3

    try:
        # Fetch coin's 24-hour trading volume
        url = f'https://api.coingecko.com/api/v3/coins/{coin_id}'
        response = make_coingecko_request(url)
        data = response.json()
        volume_24h = data.get('market_data', {}).get('total_volume', {}).get('usd', 0)
        logger.debug(f"24-hour trading volume for {symbol}: ${volume_24h:,.2f}")

        # Score based on trading volume
        if volume_24h >= 100_000_000:  # $100M
            return 10
        elif volume_24h >= 10_000_000:  # $10M
            return 8
        elif volume_24h >= 1_000_000:   # $1M
            return 6
        elif volume_24h >= 100_000:    # $100K
            return 4
        return 2

    except (ValueError, TypeError, KeyError) as e:
        logger.error(f"Error calculating transaction patterns for {symbol}: {e}")
        return 3
    except requests.RequestException as e:
        logger.error(f"Error fetching CoinGecko data for {symbol}: {e}")
        return 3

def score_whitepaper_roadmap(symbol):
    """Score whitepaper and roadmap based on CoinGecko data."""
    coin_id = get_coin_id(symbol)
    if not coin_id:
        return 3
    try:
        url = f'https://api.coingecko.com/api/v3/coins/{coin_id}'
        response = make_coingecko_request(url)
        data = response.json()
        description = data.get('description', {}).get('en', '')
        links = data.get('links', {})

        whitepaper = links.get('homepage', [''])
        roadmap = links.get('repos_url', {}).get('github', [])

        score = 2
        if whitepaper:
            score += 3
        if roadmap:
            score += 3
        if len(description) > 300:
            score += 2

        return min(score, 10)
    except requests.RequestException as e:
        logger.error(f"Error fetching whitepaper/roadmap for {symbol}: {e}")
        return 3

def score_regulatory_compliance(symbol):
    """Score regulatory compliance based on CoinGecko categories and platforms."""
    coin_id = get_coin_id(symbol)
    if not coin_id:
        return 3
    try:
        url = f'https://api.coingecko.com/api/v3/coins/{coin_id}'
        response = make_coingecko_request(url)
        data = response.json()
        tags = data.get('categories', [])
        platforms = data.get('platforms', {})

        score = 2
        if any('stablecoin' in tag.lower() for tag in tags):
            score += 2
        if any(tag for tag in tags if 'compliant' in tag.lower() or 'regulated' in tag.lower()):
            score += 4
        if any(platform in platforms for platform in ['ethereum', 'binance-smart-chain', 'bitcoin']):
            score += 2

        return min(score, 10)
    except requests.RequestException as e:
        logger.error(f"Error fetching regulatory compliance for {symbol}: {e}")
        return 3

def evaluate_cryptos(cryptos, currency_choice):
    results = []
    for coin in cryptos:
        rank_number = str(coin.get('#'))
        crypto_name = coin.get('Name')
        logger.info(f'Retrieved: {crypto_name}')
        current_price = coin.get('Current Price')
        volume_1h = coin.get('1h%')
        volume_24h = coin.get('24h%')
        volume_7d = coin.get('7d%')
        market_cap = coin.get('Market Cap')
        logo_link = coin.get('Logo')
        symbol = coin.get('Symbol')
        description = coin.get('Description')
        creation_date = coin.get('Creation Date')
        website = coin.get('Website')
        source_code = coin.get('Source Code')
        score_social = 10 if crypto_name == 'Bitcoin' else get_sentiment_score(symbol)
        score_txn = 10 if crypto_name == 'Bitcoin' else detect_anomalies(symbol)
        score_volume = 10 if crypto_name == 'Bitcoin' else score_trading_volume_consistency(volume_24h, market_cap)
        score_liquidity = 10 if crypto_name == 'Bitcoin' else score_market_cap_liquidity(market_cap)
        score_age = 10 if crypto_name == 'Bitcoin' else score_token_age(creation_date)
        score_dev = 10 if crypto_name == 'Bitcoin' else score_developer_transparency(symbol)
        score_audit = 10 if crypto_name == 'Bitcoin' else score_contract_audit(symbol)
        score_exchange = 10 if crypto_name == 'Bitcoin' else score_exchange_listings(symbol)
        score_whitepaper = 10 if crypto_name == 'Bitcoin' else score_whitepaper_roadmap(symbol)
        score_regulation = 10 if crypto_name == 'Bitcoin' else score_regulatory_compliance(symbol)
        if score_exchange <= 7 and crypto_name =='Ethereum':
            score_exchange = score_exchange + 3
        if score_social <= 7 and crypto_name == 'Ethereum':
            score_social = score_social + 3
        if crypto_name == 'Ethereum' and score_whitepaper <= 7:
            score_whitepaper = score_whitepaper + 3
        if crypto_name == 'Ethereum' and score_regulation <= 7:
            score_regulation = score_regulation + 3
        if crypto_name == 'Ethereum' and score_dev <= 7:
            score_dev = score_dev + 3 
        if crypto_name == 'Ethereum' and score_txn <= 7:
            score_txn = score_txn + 3
        score_volume = int((score_liquidity + score_exchange + score_audit)/3)
        scores = {
            '#': rank_number,
            'Name': crypto_name,
            'Current Price': current_price,
            '1h%': volume_1h,
            '24h%': volume_24h,
            '7d%': volume_7d,
            'Market Cap': market_cap,
            'Logo': logo_link,
            'Symbol': symbol,
            'Description': description,
            'Creation Date': creation_date,
            'Website': website,
            'Source Code': source_code,
            'Trading Volume Consistency': score_volume,
            'Liquidity and Order Book Depth': score_liquidity,
            'Token Age and Market History': score_age,
            'Developer and Team Transparency': score_dev,
            'Smart Contract Audit and Security Measures': score_audit,
            'Exchange Listings and Reputation': score_exchange,
            'Community and Social Media Presence': score_social,
            'Transaction Patterns and Anomalies': score_txn,
            'Whitepaper and Roadmap Assessment': score_whitepaper,
            'Regulatory Compliance and Legal Standing': score_regulation
        }
        scores['Total Score'] = sum([v for k, v in scores.items() if isinstance(v, int)])
        results.append(scores)
        time.sleep(2)
    return results