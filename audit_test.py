import logging
import random
from datetime import datetime
from pprint import pprint
import app
# Import your modules
from app import score_handler as sch
from app import request_api as req

# Configure logging for clearer output
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# -------------------
# 1. SANITY TESTING
# -------------------
def sanity_test():
    logger.info("=== SANITY TEST START ===")
    
    test_symbols = ["BTC", "ETH", "ADA"]  # Known valid coins
    
    # Test API connectivity & schema compliance
    for symbol in test_symbols:
        coin_id = sch.get_coin_id(symbol)
        assert coin_id is not None, f"Failed to get CoinGecko ID for {symbol}"
        logger.info(f"{symbol} mapped to CoinGecko ID: {coin_id}")
        
        # Example: Test volume consistency score
        vol_score = sch.score_trading_volume_consistency(coin_id)
        assert vol_score is not None, f"Volume score is None for {symbol}"
        logger.info(f"Trading Volume Consistency ({symbol}): {vol_score}")
        
        # Example: Test volatility
        volat_score = sch.score_volatility(symbol)
        assert 0 <= volat_score <= 10, f"Volatility score out of range for {symbol}"
        logger.info(f"Volatility Score ({symbol}): {volat_score}")

    # Test CSV output creation from request_api
    cmc_key = "32603379-4a80-4718-8f12-9f2607da7e80"  # replace with your key
    headings, data, filepath = req.api_request(cmc_key, "1", "USD")
    assert headings is not None and data is not None, "CMC API request failed"
    logger.info(f"CMC CSV file created: {filepath}")

    logger.info("=== SANITY TEST PASSED ===\n")

# -------------------
# 2. AUDIT TESTING
# -------------------
def audit_test():
    logger.info("=== AUDIT TEST START ===")

    # Controlled synthetic test for volatility score
    synthetic_prices = [100, 102, 101, 103, 104, 102, 101]
    log_returns = sch.compute_log_returns(synthetic_prices)
    manual_vol = round(sch.compute_historical_volatility(log_returns) * 100, 2)

    logger.info(f"Manual volatility: {manual_vol}")
    # Expected score based on manual volatility
    expected_score = sch.score_volatility("BTC", days=7)  # Using real coin as reference
    logger.info(f"Expected score threshold check: {expected_score}")

    # Controlled anomaly detection test
    synthetic_data = [[random.uniform(1, 2), random.uniform(100, 200)] for _ in range(48)]
    anomaly_fraction = sch.estimated_outlier_fraction_mad([d[1] for d in synthetic_data])
    logger.info(f"Synthetic anomaly fraction: {anomaly_fraction:.4f}")

    # Weighted score calculation audit
    dummy_scores = {
        "Realized Volatility": 7,
        "Liquidity and Order Book Depth": 8,
        "Exchange Listings and Reputation": 9,
        "Transaction Patterns and Anomalies": 6,
        "Developer and Team Transparency": 1,
        "Smart Contract Audit and Security Measures": 0,
        "Whitepaper and Roadmap Assessment": 1,
        "Regulatory Compliance and Legal Standing": 0,
        "Community and Social Media Presence": 1
    }
    total_score = sch.calculate_total_score(dummy_scores)
    assert 0 <= total_score <= 100, "Total score out of range"
    logger.info(f"Weighted total score check: {total_score}")

    logger.info("=== AUDIT TEST PASSED ===\n")

# -------------------
# RUN TESTS
# -------------------
if __name__ == "__main__":
    sanity_test()
    audit_test()
    logger.info("All tests completed successfully.")
