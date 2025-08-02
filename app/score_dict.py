descriptions = {
  '-VOLATILITY-': (
    "Realized Volatility",
    # Low Risk Assessment
    "The asset exhibits low volatility, with trading volume remaining stable and consistent over time. This steady activity reflects strong investor confidence and balanced participation from both buyers and sellers. The reliability of volume patterns suggests a low-risk environment with minimal signs of manipulation, providing a solid basis for technical analysis and informed decision-making.",
    # Medium Risk Assessment
    "The asset shows moderate volatility, with occasional fluctuations in trading volume that are not always aligned with market news or events. While general market activity appears legitimate, these irregularities may indicate emerging speculative interest or shifting investor sentiment. This presents a medium-risk scenario where caution is warranted when interpreting price movements.",
    # High Risk Assessment
    "The asset experiences high volatility, marked by unpredictable and extreme changes in trading volume. These abrupt surges or drops may signal wash trading, manipulation, or pump-and-dump schemes. Such erratic behavior undermines trust in market integrity and indicates a high-risk environment, where price action is unreliable and speculative activity dominates."
  ),

  '-LIQUIDITY-': (
    "Liquidity & Order Book Depth",
    # Low Risk Assessment
    "The token has deep and active order books with minimal slippage, allowing for large trades to be executed efficiently. This suggests strong market participation and reduces the likelihood of price manipulation or artificial price swings.",
    # Medium Risk Assessment
    "Liquidity is moderate, with occasional signs of thin order books or noticeable slippage during peak activity. While trading is possible, large trades may affect price, and caution is advised during volatile periods.",
    # High Risk Assessment
    "Order books are consistently thin or illiquid, with large spreads and high slippage. This environment is vulnerable to manipulation, and trades can be significantly impacted by low volume. Such conditions are often seen in pump-and-dump schemes or low-trust tokens."
  ),

  '-EXCHANGE-': (
    "Exchange Listings & Reputation",
    # Low Risk Assessment
    "The token is listed on major and reputable exchanges with strict vetting processes, indicating a high level of legitimacy and broad market trust. These listings also improve liquidity and user access.",
    # Medium Risk Assessment
    "The token is listed on mid-tier or niche exchanges. While this provides some accessibility, these platforms may have looser listing requirements, so extra scrutiny is recommended.",
    # High Risk Assessment
    "The token is only available on obscure or decentralized exchanges with minimal oversight. Lack of reputable listings may suggest the project has not passed due diligence or is attempting to avoid regulatory scrutiny."
  ),

  '-ANOMALY-': (
    "Transaction Patterns & Anomalies",
    # Low Risk Assessment
    "On-chain activity appears healthy, with a wide distribution of wallets and regular, transparent transactions. This pattern reflects organic use and widespread participation.",
    # Medium Risk Assessment
    "Some unusual transaction patterns are present, such as repeated transfers between a small number of wallets or unusual inactivity. These could be harmless but may also signal coordinated behavior or testing for manipulation.",
    # High Risk Assessment
    "Transactions show clear signs of suspicious behavior: wallet clustering, circular transfers, or single-wallet dominance. These red flags are often seen in scams, wash trading, or exit strategies."
  ),
  '-DEVELOPER-': (
    "Developer & Team Transparency",
    # Checked
    "The development team is fully doxxed, publicly active, and backed by credible professional profiles and past experience. Transparent communication and community interaction build trust and demonstrate accountability.",
    # Not Checked
    "Team information is partially available or inconsistently disclosed. While some members may be known, full transparency is lacking. This introduces a moderate level of risk and warrants further research.",
    
  ),

  '-COMMUNITY-': (
    "Community & Social Media Presence",
    # Checked
    "The project maintains an active, engaged, and growing community across major platforms. Discussions are organic, with balanced sentiment and developer participation. This signals healthy community trust and project momentum.",
    # Not Checked
    "Community activity exists but may appear inconsistent, overly promotional, or reliant on giveaways and hype. While engagement is visible, it may not reflect genuine interest or long-term support."
  ),

  '-WHITEPAPER-': (
    "Whitepaper & Roadmap Execution",
    # Checked
    "The whitepaper is clear, detailed, and technically sound, with a roadmap that matches delivered progress. Regular updates and achievements reflect genuine commitment and execution.",
    # Not Checked
    "The whitepaper presents general ideas but lacks technical depth or realistic goals. Progress on the roadmap may be slow or unclear, raising questions about the project's capacity to deliver."
  ),

  '-REGULATORY-': (
    "Regulatory Compliance & Legal Standing",
    # Checked
    "The project adheres to relevant regulations, conducts proper KYC/AML procedures, and avoids jurisdictions known for fraudulent activity. This adds legitimacy and reduces legal risk.",
    # Not Checked
    "Regulatory compliance is unclear or inconsistently communicated. While no legal issues are known, a lack of transparency in this area warrants caution and further investigation."
  ),

  '-CONTRACT-': (
    "Smart Contract Audit & Security",
    # Checked
    "The token's smart contract has undergone one or more independent third-party audits, with no critical vulnerabilities found. This adds a significant layer of security and demonstrates a commitment to best practices.",
    # Not Checked
    "The smart contract may have had internal reviews or partial audits, but lacks comprehensive third-party verification. While not inherently insecure, the absence of a full audit is a concern that should be weighed."
  ),




}

main_descriptions = {
    'Low Risk': (
        "This coin has been assessed as Low Risk, indicating a strong market position with high liquidity, "
        "consistent trading volume, and relatively low price volatility. It likely has robust community support, "
        "ongoing development activity, and positive sentiment across major platforms. Historical data suggests "
        "stable performance over time, making it a safer choice for conservative investors."
    ),
    'Low-Medium Risk': (
        "This coin is categorized as Low-Medium Risk, meaning it generally shows stability with occasional "
        "volatility spikes. It maintains decent trading activity, reasonable liquidity, and ongoing but possibly "
        "slower development progress. Market sentiment may vary, but overall confidence in the project remains steady."
    ),
    'Medium-High Risk': (
        "The coin is considered Medium-High Risk, indicating notable price swings, inconsistent trading volume, "
        "and possible concerns around project updates or development momentum. While it may have potential, "
        "market confidence is mixed and the asset may react strongly to news or external factors. Caution is advised."
    ),
    'High Risk': (
        "This coin falls under the High Risk category, showing signs of major volatility, low trading volume, "
        "or poor liquidity. It may lack sustained developer activity or community engagement, and could be highly "
        "sensitive to speculation or market rumors. Extreme caution is recommended, especially for risk-averse investors."
    ),
    'No Rating': (
        "No risk rating is available for this coin due to insufficient data or anomalies in the scoring process. "
        "Please try again later or review the coin's fundamentals manually."
    )
}

def get_main_desc(score):
    int_score = int(score)
    if int_score >= 80:
        key = 'Low Risk'
    elif int_score >= 60:
        key = 'Low-Medium Risk'
    elif int_score >= 40:
        key = 'Medium-High Risk'
    else:
        key = 'High Risk'

    return main_descriptions[key]

def get_category_desc(category, score):
    if category not in descriptions:
        return "Unknown Category", "No description available."

    category_info = descriptions[category]
    int_score = int(score)

    if category in ['-DEVELOPER-', '-COMMUNITY-', '-WHITEPAPER-', '-REGULATORY-', '-CONTRACT-']:
        # Binary category — score 1 means True, 0 means False
        if int_score == 1:
            desc_index = 1  # True description
        else:
            desc_index = 2  # False description
    else:
        # Risk-based category with 3 risk levels
        if int_score >= 8:
            desc_index = 1  # Low Risk
        elif int_score >= 4:
            desc_index = 2  # Medium Risk
        elif int_score >= 1:
            desc_index = 3  # High Risk
        else:
            desc_index = 3  # Default to High Risk if invalid score

    return category_info[0], category_info[desc_index]  # title, description
