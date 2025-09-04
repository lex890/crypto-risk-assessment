import random
import requests
from datetime import datetime
import time
import logging
from transformers import pipeline
from sklearn.ensemble import IsolationForest
import numpy as np
from . import keystore
from cerberus import Validator
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from .news_spider import CryptoNewsSpider
import math
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
np.random.seed(7122025)
sentiment_analyzer = None
DEFAULT_WEIGHTS = {
    "Realized Volatility": 0.25,
    "Liquidity and Order Book Depth": 0.25,
    "Exchange Listings and Reputation": 0.125,
    "Transaction Patterns and Anomalies": 0.125,
    "Developer and Team Transparency": 0.05,
    "Smart Contract Audit and Security Measures": 0.05,
    "Whitepaper and Roadmap Assessment": 0.04,
    "Regulatory Compliance and Legal Standing": 0.04,
    "Community and Social Media Presence": 0.03
}
crypto_schema = {
    '#': {'type': 'integer', 'required': True},
    'Name': {'type': 'string', 'required': True, 'empty': False},
    'Current Price': {'type': 'string', 'required': True, 'empty': False},
    '1h%': {'type': 'string', 'required': False, 'nullable': True},
    '24h%': {'type': 'string', 'required': True, 'empty': False,  'nullable': True},
    '7d%': {'type': 'string', 'required': False, 'nullable': True},
    'Market Cap': {'type': 'string', 'required': True, 'empty': False},
    'Logo': {'type': 'string', 'required': False, 'nullable': True},
    'Symbol': {'type': 'string', 'required': True, 'empty': False},
    'Description': {'type': 'string', 'required': False, 'nullable': True},
    'Creation Date': {'type': 'string', 'required': True, 'empty': False, 'nullable': True, 'regex': r'^\d{4}-\d{2}-\d{2}$'},
    'Website': {'type': 'string', 'required': False, 'nullable': True},
    'Source Code': {'type': 'string', 'required': False, 'nullable': True},
}
def calculate_total_score(scores):
    """
    Calculate total score using DEFAULT_WEIGHTS.
    Binary metrics get 10 points if 1, else 0.
    Total score is scaled so the sum < 100.
    """
    required_metrics = list(DEFAULT_WEIGHTS.keys())
    for metric in required_metrics:
        if metric not in scores:
            raise ValueError(f"Missing score for: {metric}")

    scale_factor = 100 / 10  # To scale weighted max of 10 up to ~100

    weighted_sum = 0
    for metric, weight in DEFAULT_WEIGHTS.items():
        value = scores[metric]

        # If this is one of the binary metrics, convert 1 → 10, 0 → 0
        if metric in [
            "Developer and Team Transparency",
            "Smart Contract Audit and Security Measures",
            "Whitepaper and Roadmap Assessment",
            "Regulatory Compliance and Legal Standing",
            "Community and Social Media Presence"
        ]:
            value = 10 if value == 1 else 0

        weighted_sum += value * weight

    total_score = weighted_sum * scale_factor
    total_score = min(total_score, 100)  # Clamp to < 100

    return int(total_score)

# Initialize Cerberus validator
validator = Validator(crypto_schema, allow_unknown=False)
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
COINGECKO_DEMO_API_KEYS = keystore.load_api_key('CoinGecko', 'CGKEY')
COINGECKO_BASE = 'https://api.coingecko.com/api/v3'
GITHUB_TOKEN = keystore.load_api_key('GitHub', 'GITHUB_TOKEN')
if isinstance(GITHUB_TOKEN, list):
    GITHUB_TOKEN = GITHUB_TOKEN[0]
GITHUB_TOKEN = GITHUB_TOKEN.strip()
NEWSAPI_KEYS = [
    "026ffd3bcbab4b5d896839af5f5d21ed",
    "74ba9d945b144ae7b77c1fb2db4f7afb",
    "753aa7b2266549d5a327cc06421b5641",
    "f828a52f2080498dacd9513ccf67d8bc",
    ]
for COINGECKO_DEMO_API_KEY in COINGECKO_DEMO_API_KEYS:
    if not COINGECKO_DEMO_API_KEY:
       raise ValueError("COINGECKO_DEMO_API_KEY is required in settings.cfg")

# Cache for symbol to coin ID mapping
# ======= MISC =======
symbol_to_coin_id_cache = {}
preferred_ids = {
"BTC": "bitcoin",
"ETH": "ethereum",
"XRP": "ripple",
"USDT": "tether",
"BNB": "binancecoin",
"SOL": "solana",
"USDC": "usd-coin",
"STETH": "staked-ether",
"DOGE": "dogecoin",
"TRX": "tron",
"ADA": "cardano",
"WSTETH": "wrapped-steth",
"WBTC": "wrapped-bitcoin",
"HYPE": "hyperliquid",
"LINK": "chainlink",
"XLM": "stellar",
"SUI": "sui",
"WBETH": "wrapped-beacon-eth",
"WEETH": "wrapped-eeth",
"BCH": "bitcoin-cash",
"HBAR": "hedera-hashgraph",
"AVAX": "avalanche-2",
"USDE": "ethena-usde",
"WETH": "weth",
"LTC": "litecoin",
"TON": "the-open-network",
"LEO": "leo-token",
"SHIB": "shiba-inu",
"USDS": "usds",
"BSC-USD": "binance-bridged-usdt-bnb-smart-chain",
"UNI": "uniswap",
"WBT": "whitebit",
"CBBTC": "coinbase-wrapped-btc",
"DOT": "polkadot",
"CRO": "crypto-com-chain",
"BGB": "bitget-token",
"PEPE": "pepe",
"SUSDE": "ethena-staked-usde",
"XMR": "monero",
"ENA": "ethena",
"AAVE": "aave",
"DAI": "dai",
"TAO": "bittensor",
"MNT": "mantle",
"ETC": "ethereum-classic",
"NEAR": "near",
"ONDO": "ondo-finance",
"APT": "aptos",
"PI": "pi-network",
"ICP": "internet-computer",
"OKB": "okb",
"JITOSOL": "jito-staked-sol",
"KAS": "kaspa",
"PENGU": "pudgy-penguins",
"ARB": "arbitrum",
"ALGO": "algorand",
"BUIDL": "blackrock-usd-institutional-digital-liquidity-fund",
"POL": "polygon-ecosystem-token",
"USD1": "usd1-wlfi",
"ATOM": "cosmos",
"VET": "vechain",
"BONK": "bonk",
"RENDER": "render-token",
"GT": "gatechain-token",
"WLD": "worldcoin-wld",
"FTN": "fasttoken",
"RETH": "rocket-pool-eth",
"SEI": "sei-network",
"IP": "story-2",
"TRUMP": "official-trump",
"SUSDS": "susds",
"RSETH": "kelp-dao-restaked-eth",
"BNSOL": "binance-staked-sol",
"SKY": "sky",
"FET": "fetch-ai",
"JLP": "jupiter-perpetuals-liquidity-provider-token",
"FIL": "filecoin",
"SPX": "spx6900",
"QNT": "quant-network",
"FLR": "flare-networks",
"JUP": "jupiter-exchange-solana",
"LBTC": "lombard-staked-btc",
"OSETH": "stakewise-v3-oseth",
"XDC": "xdce-crowd-sale",
"METH": "mantle-staked-ether",
"LSETH": "liquid-staked-ethereum",
"USDTB": "usdtb",
"KCS": "kucoin-shares",
"HASH": "hash-2",
"INJ": "injective-protocol",
"OP": "optimism",
"CRV": "curve-dao-token",
"USDT0": "usdt0",
"EZETH": "renzo-restaked-eth",
"NEXO": "nexo",
"STX": "blockstack",
"TIA": "celestia",
"FDUSD": "first-digital-usd",
"USDF": "falcon-finance",
"VIRTUAL": "virtual",
"PENDLE": "pendle",
"CLBTC": "clbtc",
"KAIA": "kaia",
"CGETH.HASHKEY": "cgeth-hashkey-cloud",
"THETA": "theta-token",
"EETH": "ether-fi-staked-eth",
"A": "vaulta",
"MSOL": "msol",
"IOTA": "iota",
"RAY": "raydium",
"GALA": "gala",
"JASMY": "jasmycoin",
"SAND": "the-sandbox",
"CMETH": "mantle-restaked-eth",
"OUSG": "ousg",
"MORPHO": "morpho",
"BTT": "bittorrent",
"JTO": "jito-governance-token",
"USDY": "ondo-us-dollar-yield",
"USDX": "usdx-money-usdx",
"FLOKI": "floki-inu",
"CFX": "conflux-network",
"IMX": "immutable-x",
"FARTCOIN": "fartcoin",
"ENS": "ethereum-name-service",
"LDO": "lido-dao",
"PYUSD": "paypal-usd",
"GRT": "the-graph",
"WIF": "dogwifhat",
"CAKE": "pancakeswap",
"XTZ": "tezos",
"PAXG": "pax-gold",
"AERO": "aerodrome-finance",
"PUMP": "pump-fun",
"FORM": "binaryx-new",
"BSV": "bitcoin-sv",
"DEEP": "deepbook-protocol",
"CORE": "core-dao",
"RSR": "reserve-rights",
"STRK": "starknet-token",
"ETHFI": "ether-fi-ethfi",
"AR": "arweave",
"DYDX": "dydx-chain",
"COMP": "compound",
"USDD": "usdd",
"RUNE": "thorchain",
"XCN": "onyxcoin",
"TUSD": "trueusd",
"APE": "apecoin-ape",
"ZBCN": "zebec-network",
"NFT": "apenft",
"SUPER": "superverse",
"NEO": "neo",
"CVX": "convex-finance",
"EGLD": "multiversx-egld",
"EIGEN": "eigenlayer",
"AIOZ": "aioz-network",
"W": "wormhole",
"XEC": "ecash",
"ZK": "zksync",
"KAVA": "kava",
"CHZ": "chiliz",
"SUN": "sun-token",
"AXS": "axie-infinity",
"1INCH": "1inch",
"BEAM": "onbeam",
"RON": "ronin",
"ATH": "aethir",
"MOVE": "movement",
"AXL": "axelar",
"GNO": "gnosis-gno",
"WEMIX": "wemix",
"PYTH": "pyth-network",
"M": "memecore",
"BRETT": "based-brett",
"WAL": "walrus-xyz",
"AB": "newton",
"BUILD": "buildon",
"MOG": "mog-coin",
"HNT": "helium",
"SYRUP": "maple-finance"
}
def estimated_outlier_fraction_mad(data, threshold=3.5):
    """
    Estimate fraction of outliers using MAD method.
    threshold: how many scaled MAD units to call something an outlier.
    """
    data = np.array(data)
    median = np.median(data)
    mad = np.median(np.abs(data - median))
    if mad == 0:
        return 0.0  # No variation
    modified_z_scores = 0.6745 * (data - median) / mad
    outliers = np.abs(modified_z_scores) > threshold
    return np.mean(outliers)
def get_coin_id(symbol):
    """Map a coin symbol to its CoinGecko coin ID."""
    symbol = symbol.upper()
    if symbol in preferred_ids:
        return preferred_ids[symbol]
    else:
        if symbol in symbol_to_coin_id_cache:
            return symbol_to_coin_id_cache[symbol]
        
        try:
            response = requests.get(
                f'{COINGECKO_BASE}/coins/list',
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
                continue
            else:
                logger.error(f"HTTP error for {url}: {e}")
                raise
        except requests.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            raise
    raise Exception(f"Failed to fetch {url} after {retries} attempts")

# ======= COMMUNITY AND SOCIAL MEDIA PRESENCE =======
def fetch_news_headlines(symbol):
    """Fetch news headlines using NewsAPI with multiple API keys and rate limit handling."""
    for api_key in NEWSAPI_KEYS:
        try:
            url = f"https://newsapi.org/v2/everything?q={symbol}&language=en&pageSize=5&sortBy=publishedAt&apiKey={api_key}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])
            return [article["title"] for article in articles if "title" in article]
        except requests.HTTPError as e:
            if response.status_code == 429:
                logger.warning(f"NewsAPI rate limit reached for key {api_key}. Trying next key...")
                time.sleep(2 ** NEWSAPI_KEYS.index(api_key))  # Exponential backoff
                continue
            else:
                logger.error(f"HTTP error for {symbol} with key {api_key}: {e}")
                return [f"No recent news available for {symbol}"]
        except Exception as e:
            logger.error(f"Failed to fetch news for {symbol} with key {api_key}: {e}")
            return [f"No recent news available for {symbol}"]
    logger.error(f"All NewsAPI keys exhausted for {symbol}")
    return [f"No recent news available for {symbol}"]

def get_sentiment_score(symbol):
    """Perform sentiment analysis on fetched headlines using DistilBERT (lazy load)."""
    global sentiment_analyzer

    # Lazy load the model on first use
    if sentiment_analyzer is None:
        logger.info("Loading sentiment analysis model for the first time...")
        from transformers import pipeline
        sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )

    headlines = fetch_news_headlines(symbol)
    scores = []
    for text in headlines:
        if "No recent news available" in text:
            continue
        result = sentiment_analyzer(text)[0]
        polarity = result["score"] if result["label"] == "POSITIVE" else -result["score"]
        scores.append(polarity)

    if not scores:
        return 0

    avg_score = sum(scores) / len(scores)
    return 1 if avg_score > 0.25 else 0
def score_news_coverage(symbol, crypto_name):
    """Score news coverage based on article count from scraped news."""
    try:
        # Configure Scrapy settings
        settings = get_project_settings()
        settings.set('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        settings.set('ROBOTSTXT_OBEY', True)
        settings.set('DOWNLOAD_DELAY', 2.0)

        # Initialize spider and process
        process = CrawlerProcess(settings)
        results = []

        def collect_results(item, response, spider):
            results.append(item)

        process.crawl(CryptoNewsSpider, symbol=symbol, crypto_name=crypto_name, callback=collect_results)
        process.start()

        article_count = len(results)
        logger.info(f"Found {article_count} news articles for {crypto_name} ({symbol})")

        if article_count >= 10:
            return 10
        elif article_count >= 5:
            return 8
        elif article_count >= 2:
            return 6
        elif article_count >= 1:
            return 4
        return 5
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
        return 5

# === Fetch historical volume data ===
def get_historical_volume(coin_id, currency='usd', days=30):
    url = f'{COINGECKO_BASE}/coins/{coin_id}/market_chart'
    params = {
        'vs_currency': currency,
        'days': days,
        'interval': 'daily',
        'x_cg_demo_api_key': COINGECKO_DEMO_API_KEY  # Use the API key from score_handler.py
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        volumes = data.get("total_volumes", [])
        print(f"\nVolume data for '{coin_id}' over the last {days} days:")
        volume_values = []
        for timestamp, volume in volumes:
            date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
            volume_values.append(volume)

        return volume_values

    except requests.RequestException as e:
        logger.error(f"Error fetching volume data for {coin_id}: {e}")
        return []

# === Universal Exponential Decay Function ===
def exp_decay_score(x, a):
    """Returns score from 1 to 10, decreasing exponentially with input x."""
    return round(max(1, min(10 * math.exp(-a * x), 10)), 2)

# === Universal Inverse Growth Function (for positive metrics like high volume) ===
def inverse_exp_growth(x, a=1e-9):
    """Returns score from 1 to 10, increasing with x (e.g., high trading volume is good)."""
    return round(min(10, 10 * (1 - math.exp(-a * x))), 2)

# === Sub-metric 1: Volume Stability Score (VSI) ===
def score_volume_stability(volumes):
    mean_vol = sum(volumes) / len(volumes)
    stdev_vol = math.sqrt(sum((v - mean_vol) ** 2 for v in volumes) / (len(volumes) - 1))
    cv = stdev_vol / mean_vol if mean_vol != 0 else float('inf')
    return exp_decay_score(cv, a=0.5)

# === Sub-metric 2: Volume Spike Score (VSI2) ===
def score_volume_spikes(volumes, max_spikes=5):
    mean_vol = sum(volumes) / len(volumes)
    spike_count = sum(1 for v in volumes if v > 2 * mean_vol)

    # Normalize spike count to a 0–1 scale
    x = spike_count / max(len(volumes), 1)

    # Optional: exaggerate spike frequency if it's above max_spikes
    if spike_count > max_spikes:
        x += (spike_count - max_spikes) * 0.05

    return exp_decay_score(x, a=6)

# === Sub-metric 3: Mean Volume Score (VSI3) ===
def score_mean_volume(mean_vol):
    return inverse_exp_growth(mean_vol, a=1e-9)

# === Master function ===
def score_trading_volume_consistency(coin_id):
    volumes = get_historical_volume(coin_id, days=7)

    if len(volumes) < 2:
        logger.info("Not enough data to compute volume metrics.")
        return None

    mean_vol = statistics.mean(volumes)
    stdev_vol = statistics.stdev(volumes)
    cv = stdev_vol / mean_vol if mean_vol != 0 else float('inf')

    vsi_score = score_volume_stability(volumes)
    vsi2_score = score_volume_spikes(volumes)
    vsi3_score = score_mean_volume(mean_vol)

    logger.info("\n=== Trading Volume Consistency Scores ===")
    logger.info(f"Mean Volume: {mean_vol:,.2f}")
    logger.info(f"Standard Deviation: {stdev_vol:,.2f}")
    logger.info(f"Coefficient of Variation (CV): {cv:.4f}")
    logger.info(f"VSI  (Stability Score)........: {vsi_score} / 10")
    logger.info(f"VSI2 (Spike Score)............: {vsi2_score} / 10")
    final_score = round((vsi_score + vsi2_score) / 2, 2)
    logger.info(f"[RESULT] Final Trading Volume Score: {final_score}/10")
    return {
        'vsi': vsi_score,
        'vsi2': vsi2_score,
        'final_score': final_score
    }
# ======= TRANSACTION PATTERNS AND ANOMALIES =======
def fetch_transaction_data(symbol,days):
    """Fetch transaction data from CoinGecko and prepare it for anomaly detection."""
    try:
        coin_id = symbol_to_coin_id_cache.get(symbol)
        if not coin_id:
            # fallback to API search if not cached
            list_url = f"{COINGECKO_BASE}/coins/list?x_cg_demo_api_key={COINGECKO_DEMO_API_KEY}"
            resp = requests.get(list_url)
            resp.raise_for_status()
            for coin in resp.json():
                if coin['symbol'].lower() == symbol.lower():
                    coin_id = coin['id']
                    symbol_to_coin_id_cache[symbol] = coin_id
                    break
            if not coin_id:
                raise ValueError(f"CoinGecko ID not found for {symbol}")

        url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart?vs_currency=usd&days={days}&x_cg_demo_api_key={COINGECKO_DEMO_API_KEY}"
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
    """Use Isolation Forest to detect anomalies in 30 days of price data."""
    try:
        data = fetch_transaction_data(symbol, days=30)
        model = IsolationForest(
            n_estimators=100,
            max_samples='auto',
            contamination= max(0.01, min(0.1, estimated_outlier_fraction_mad(data))),
            random_state=5
        )
        preds = model.fit_predict(data)
        anomaly_ratio = sum(preds == -1) / len(preds)
        logger.info(f"Anomaly ratio for {symbol}: {anomaly_ratio:.4f}")

        if anomaly_ratio <= 0.02:
            return 10
        elif anomaly_ratio <= 0.04:
            return 9
        elif anomaly_ratio <= 0.06:
            return 8
        elif anomaly_ratio <= 0.08:
            return 7
        elif anomaly_ratio <= 0.1:
            return 6
        elif anomaly_ratio <= 0.12:
            return 5
        elif anomaly_ratio <= 0.14:
            return 4
        elif anomaly_ratio <= 0.16:
            return 3
        elif anomaly_ratio <= 0.18:
            return 2
        return 1

    except Exception as e:
        logger.error(f"Error in anomaly detection for {symbol}: {e}")
        return 5  # Default score on error
# ======= VOLATILITY =======
def fetch_prices(symbol, days):
    """
    Fetch historical daily closing prices from CoinGecko
    """
    coin_id = get_coin_id(symbol)
    url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': days,
        'interval': 'daily'  # 1 price per day
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        prices = [p[1] for p in response.json().get("prices", [])]
        print(f"Retrieved {len(prices)} price points for {coin_id}.")
        return prices
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return []
def compute_log_returns(prices):
    """
    Compute daily log returns from a list of prices
    """
    prices = np.array(prices)
    log_returns = np.log(prices[1:] / prices[:-1])
    return log_returns
def compute_historical_volatility(log_returns):
    """
    Compute historical volatility (standard deviation of log returns)
    """
    return round(np.std(log_returns), 6)
def score_volatility(symbol, days=30):
    """Market Volatility of a Coin."""
    
    try:
        #list of closing prices in the last 30 days
        prices = fetch_prices(symbol, days)
        if len(prices) > 2:
            log_returns = compute_log_returns(prices)
            volatility  = (compute_historical_volatility(log_returns)) * 100
            
            # Updated scoring: lower volatility = higher score, based on real output
            if volatility <= 1.5:
                return 10
            elif volatility <= 2:
                return 9
            elif volatility <= 2.5:
                return 8
            elif volatility <= 3:
                return 7
            elif volatility <= 4:
                return 6
            elif volatility <= 5:
                return 5
            elif volatility <= 6:
                return 4
            elif volatility <= 7:
                return 3
            elif volatility <= 8:
                return 2
            elif volatility <= 10:
                return 1
            elif volatility > 10:
                return 1
        else:
            print("Not enough data to compute.")
            return 5
    except (ValueError, TypeError) as e:
        logger.error(f"Error calculating token volatility: {e}")
        return 5

# ======= LIQUIDITY & ORDER BOOK DEPTH =======    
def spread_metric_score(value, bands):
    """bands is a tuple of thresholds in ascending order""" 
    if value <= bands[0]:
        return 10
    elif value <= bands[1]:
        return 8
    elif value <= bands[2]:
        return 6
    elif value <= bands[3]:
        return 4
    else:
        return 2    
def score_market_cap_liquidity(symbol, current_price, volume_24h):
    """Score market cap liquidity, handling blank or invalid inputs."""
    coin_id = get_coin_id(symbol)
    if not coin_id:
        logger.error(f"No CoinGecko coin ID found for symbol {symbol}")
        return 5  # Return default score if coin ID is not found

    try:
        url = f"{COINGECKO_BASE}/coins/{coin_id}"
        response = make_coingecko_request(url)  # Use retry logic for API calls
        data = response.json()

        # Use API's current price and 24h change for consistency
        api_current_price = data.get('market_data', {}).get('current_price', {}).get('usd')
        api_volume_24h_pct = data.get('market_data', {}).get('price_change_percentage_24h', 0) / 100

        # Parse input current_price if provided, else use API
        if isinstance(current_price, str):
            current_price = current_price.replace('$', '').replace(',', '').strip()
            current_price = float(current_price)
        elif isinstance(current_price, (int, float)):
            pass  # Already good
        else:
            logger.warning(f"Invalid current_price type for {symbol}: {type(current_price)}. Using API value.")
            current_price = api_current_price if api_current_price else 0.0

        # If no valid current_price, default
        if current_price == 0.0:
            logger.error(f"No valid current_price for {symbol}")
            return 5

        # Parse input volume_24h (24h % change) if provided, else use API
        if isinstance(volume_24h, str):
            volume_24h = volume_24h.replace('%', '').strip()
            volume_24h = float(volume_24h) / 100 if volume_24h else api_volume_24h_pct
        elif isinstance(volume_24h, (int, float)):
            volume_24h /= 100 if abs(volume_24h) > 1 else volume_24h  # Assume if >1 it's not decimal
        else:
            logger.warning(f"Invalid volume_24h type for {symbol}: {type(volume_24h)}. Using API value.")
            volume_24h = api_volume_24h_pct

        # Check if 'tickers' key exists and is non-empty
        if 'tickers' not in data or not data['tickers']:
            logger.warning(f"No tickers found for {symbol} (coin_id: {coin_id})")
            return 5  # Return default score if no tickers are available

        prices = []
        exchanges = []
        logger.debug(f"Tickers data: {data['tickers']}")
        for ticker in data['tickers']:
            if ticker.get('trust_score') in {'green', 'yellow'}:
                usd_price = ticker.get('converted_last', {}).get('usd')
                exchange = ticker.get('market', {}).get('name')
                if usd_price and exchange:
                    prices.append(float(usd_price))  # Use normalized USD price
                    exchanges.append(exchange)

        if not prices or len(prices) < 3:  # Require at least 3 valid prices for meaningful calculation
            logger.warning(f"Insufficient valid tickers ({len(prices)}) for {symbol}")
            return 5  # Return default score if no/few valid tickers

        proxy_bid = min(prices)
        proxy_ask = max(prices)
        mid_price = (proxy_bid + proxy_ask) / 2

        # Calculate prev_price using volume_24h as a percentage change
        prev_price = current_price / (1 + volume_24h) if volume_24h != 0 else current_price

        # Determine Q based on price movement
        Q = 1 if current_price > prev_price else -1 if current_price < prev_price else 0

        # Calculate m_after based on Q
        if Q == 1:
            m_after = (proxy_ask + mid_price) / 2
        elif Q == -1:
            m_after = (proxy_bid + mid_price) / 2
        else:
            m_after = mid_price

        # Log intermediate values for debugging
        logger.debug(f"{symbol} - proxy_bid: {proxy_bid}, proxy_ask: {proxy_ask}, mid_price: {mid_price}, "
                     f"current_price: {current_price}, prev_price: {prev_price}, Q: {Q}, m_after: {m_after}")

        # Calculate spreads in basis points
        spread_bps = ((proxy_ask - proxy_bid) / mid_price) * 10_000 if mid_price != 0 else float('inf')
        effect_bps = (2 * Q * ((current_price - mid_price) / mid_price)) * 10_000 if mid_price != 0 else float('inf')
        impact_bps = Q * ((m_after - mid_price) / mid_price) * 10_000 if mid_price != 0 else float('inf')

        # Handle inf by setting to high value (e.g., 1000 bps) for low score
        if spread_bps == float('inf'):
            spread_bps = 1000
        if effect_bps == float('inf'):
            effect_bps = 1000
        if impact_bps == float('inf'):
            impact_bps = 1000

        # Score each metric (adjust bands if needed for crypto; these seem reasonable)
        score_qs = spread_metric_score(spread_bps, (5, 15, 30, 60))
        score_es = spread_metric_score(abs(effect_bps), (7, 20, 40, 80))
        score_pi = spread_metric_score(abs(impact_bps), (3, 8, 15, 30))

        liquidity_score = round((score_qs + score_es + score_pi) / 3, 1)
        logger.info(f"Liquidity Score for {symbol} (1-10): {liquidity_score}")
        return liquidity_score

    except requests.RequestException as e:
        logger.error(f"Error fetching tickers for {symbol}: {e}")
        return 5  # Return default score on API failure
    except (ValueError, TypeError, ZeroDivisionError) as e:
        logger.error(f"Error processing liquidity data for {symbol}: {e}")
        logger.debug(f"Data snapshot: current_price={current_price}, volume_24h={volume_24h}, prices={prices}")
        return 5  # Return default score on data processing errors
# ======= DEVELOPER AND TEAM TRANSPARENCY =======
def make_github_request(url, retries=3, backoff_factor=2):
    """Make a GitHub API request with retry logic for rate limits."""
    headers = {'Authorization': f'Bearer {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}
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
                continue
            else:
                logger.error(f"HTTP error for {url}: {e}")
                raise
        except requests.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            raise
    raise Exception(f"Failed to fetch {url} after {retries} attempts")
def score_developer_transparency(symbol,backoff_factor = 2):
    """
    Scores developer transparency:
    - First checks if CoinGecko lists a GitHub repository for the coin.
    - If yes, queries GitHub API for activity.
    - If no GitHub link → returns 0.
    """
    try:
        # Step 1: Get CoinGecko ID
        coin_id = get_coin_id(symbol)
        if not coin_id:
            logger.warning(f"No CoinGecko ID found for {symbol}")
            return 0

        # Step 2: Fetch coin details from CoinGecko
        for COINGECKO_DEMO_API_KEY in COINGECKO_DEMO_API_KEYS:
            url = f"{COINGECKO_BASE}/coins/{coin_id}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 429:
                wait_time = backoff_factor ** COINGECKO_DEMO_API_KEYS.index(COINGECKO_DEMO_API_KEY)
                logger.warning(f'Rate limit reached, trying again in {wait_time} seconds')
                time.sleep(wait_time)
                continue
            elif resp.status_code != 200:
                logger.warning(f"Failed to fetch CoinGecko details for {symbol}: {resp.status_code}")
                return 0

        data = resp.json()
        links = data.get('links', {})
        logger.debug(f"CoinGecko links for {symbol}: {links}")
        
        github_links = links.get('repos_url', {}).get('github', [])
        logger.debug(f"GitHub links for {symbol}: {github_links}")
        
        # Step 3: Check if GitHub repo link exists
        if not github_links:
            logger.info(f"No GitHub link found for {symbol} on CoinGecko")
            return 0

        # Use the first GitHub link
        github_url = github_links[0]
        parts = github_url.rstrip("/").split("/")
        if len(parts) < 2:
            logger.warning(f"Invalid GitHub URL format for {symbol}: {github_url}")
            return 0

        owner, repo = parts[-2], parts[-1]

        # Step 4: Query GitHub API for repository details
        headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
        gh_url = f"https://api.github.com/repos/{owner}/{repo}"
        gh_resp = requests.get(gh_url, headers=headers, timeout=10)

        if gh_resp.status_code == 401:
            logger.error("GitHub API Unauthorized — check your token.")
            return 0
        elif gh_resp.status_code != 200:
            logger.warning(f"GitHub API error for {symbol}: {gh_resp.status_code}")
            return 0

        repo_data = gh_resp.json()

        # Example scoring: 1 if there's been a push in the last 90 days
        from datetime import datetime, timezone
        last_push = datetime.strptime(repo_data.get("pushed_at", ""), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        days_since_push = (datetime.now(timezone.utc) - last_push).days

        return 1 if days_since_push <= 90 else 0

    except Exception as e:
        logger.error(f"Error scoring developer transparency for {symbol}: {e}")
        return 0

# ======= SMART CONTRACT AUDIT AND SECURITY MEASURES =======
def score_contract_audit(symbol):
    """Score contract audit based on CoinGecko data."""
    coin_id = get_coin_id(symbol)
    if not coin_id:
        return 0
    try:
        url = f'{COINGECKO_BASE}/coins/{coin_id}'
        response = make_coingecko_request(url)
        data = response.json()

        links = data.get('links', {})
        homepage = links.get('homepage', [''])
        repos = links.get('repos_url', {}).get('github', [])

        platforms = data.get('platforms', {})
        contracts_present = bool(platforms)

        score = 1
        if contracts_present:
            score += 3
        if repos:
            score += 3
        if homepage:
            score += 3
        if score >=5:
            return 1
        return 0
    except requests.RequestException as e:
        logger.error(f"Error fetching contract audit data for {symbol}: {e}")
        return 0

# ======= EXCHANGE LISTINGS AND REPUTATION =======
def score_exchange_listings(symbol):
    """
    Score exchange listings based on the number of unique, trusted exchanges
    the coin is listed on.
    """
    coin_id = get_coin_id(symbol)
    if not coin_id:
        return 1

    try:
        url = f'{COINGECKO_BASE}/coins/{coin_id}/tickers'
        response = make_coingecko_request(url)
        tickers = response.json().get('tickers', [])
        
        # Filter only tickers with trust_score of 'green' or 'yellow'
        trusted_tickers = [
            t for t in tickers 
            if t.get('trust_score') in ['green', 'yellow']
            and 'market' in t and t['market'].get('name')
        ]

        # Get unique exchange names from trusted tickers
        unique_exchanges = {t['market']['name'] for t in trusted_tickers}
        count = len(unique_exchanges)

        # Scoring logic based on trusted exchange diversity
        if count >= 50:
            return 10
        elif count >= 40:
            return 9
        elif count >= 30:
            return 8
        elif count >= 25:
            return 7
        elif count >= 20:
            return 6
        elif count >= 15:
            return 5
        elif count >= 10:
            return 4
        elif count >= 5:
            return 3
        elif count >= 2:
            return 2
        return 5

    except requests.RequestException as e:
        logger.error(f"Error fetching exchange listings for {symbol}: {e}")
        return 5

# ======= WHITEPAPER AND ROADMAP ASSESSMENT =======
def score_whitepaper_roadmap(symbol):
    """Score whitepaper and roadmap based on CoinGecko data."""
    coin_id = get_coin_id(symbol)
    if not coin_id:
        return 0
    try:
        url = f'{COINGECKO_BASE}/coins/{coin_id}'
        response = make_coingecko_request(url)
        data = response.json()
        description = data.get('description', {}).get('en', '')
        links = data.get('links', {})

        whitepaper = links.get('homepage', [''])
        roadmap = links.get('repos_url', {}).get('github', [])

        score = 1
        if whitepaper:
            score += 2
        if roadmap:
            score += 2
        if len(description) > 300:
            score += 3
        if len(description) > 400:
            score += 1
        if len(description) > 500:
            score += 1
        if score >= 5:
            return 1
        return 0
    except requests.RequestException as e:
        logger.error(f"Error fetching whitepaper/roadmap for {symbol}: {e}")
        return 0

# ======= REGULATORY COMPLIANCE AND LEGAL STANDING =======
def score_regulatory_compliance(symbol):
    """Score regulatory compliance based on CoinGecko categories and platforms."""
    coin_id = get_coin_id(symbol)
    if not coin_id:
        return 0
    try:
        url = f'{COINGECKO_BASE}/coins/{coin_id}'
        response = make_coingecko_request(url)
        data = response.json()
        tags = data.get('categories', [])
        platforms = data.get('platforms', {})

        score = 1
        if any('stablecoin' in tag.lower() for tag in tags):
            score += 2
        if any(tag for tag in tags if 'compliant' in tag.lower() or 'regulated' in tag.lower()):
            score += 4
        if any(platform in platforms for platform in ['ethereum', 'binance-smart-chain', 'bitcoin']):
            score += 3
        if score >=5:
            return 1
        return 0
    except requests.RequestException as e:
        logger.error(f"Error fetching regulatory compliance for {symbol}: {e}")
        return 0

def evaluate_cryptos(cryptos, currency_choice, progress_callback=None):
    print('this is inside evaluate_cryptos: ', cryptos)
    """
    Evaluate cryptocurrencies based on various scoring metrics with input validation.
    
    Args:
        cryptos: List of dictionaries containing cryptocurrency data.
        currency_choice: The currency to use for pricing (e.g., 'usd').
    
    Returns:
        List of dictionaries with scores and original data.
    """
    results = []
    
    # Validate each crypto entry
    for idx, coin in enumerate(cryptos):
        if not validator.validate(coin):
            logger.error(f"Validation failed for coin {coin.get('Name', 'Unknown')}: {validator.errors}")
            continue  # Skip invalid entries
            # Alternatively, raise an exception: raise ValueError(f"Validation failed: {validator.errors}")

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
        
        score_exchange =  score_exchange_listings(symbol)        
        score_txn =  detect_anomalies(symbol)
        score_vol =  score_volatility(symbol)
        score_liquidity =  score_market_cap_liquidity(symbol, current_price, volume_24h)

        # 1 == True
        score_dev = score_developer_transparency(symbol)
        score_audit =  score_contract_audit(symbol)
        score_whitepaper = score_whitepaper_roadmap(symbol)
        score_regulation = score_regulatory_compliance(symbol)
        score_social = get_sentiment_score(symbol)        
        # Compile scores into result dictionary
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
            # 1-10 Scoring Values
            'Realized Volatility': int(score_vol),
            'Liquidity and Order Book Depth': int(score_liquidity),
            'Exchange Listings and Reputation': int(score_exchange),
            'Transaction Patterns and Anomalies': int(score_txn),
            # Binary Scoring Values
            'Developer and Team Transparency': score_dev,
            'Community and Social Media Presence': score_social,
            'Whitepaper and Roadmap Assessment': score_whitepaper,
            'Regulatory Compliance and Legal Standing': score_regulation,
            'Smart Contract Audit and Security Measures': score_audit  
        }                        
        scores["Total Score"] = calculate_total_score(scores)
        results.append(scores)
        if progress_callback:
            progress = 50 + int((idx / 9) * 48)
            progress_callback(progress, f"Evaluating cryptocurrency score for {crypto_name}")
        time.sleep(4)  # Respect API rate limits
    print('results', results)
    return results