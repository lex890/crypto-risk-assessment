descriptions = {
  '-SCORE1-': (
    "Trading Volume Consistency", 
    "Trading volume is stable and consistent over time, reflecting a healthy balance of buyer and seller activity in the market. This level of volume reliability typically indicates strong investor confidence and low likelihood of artificial manipulation. It supports the credibility of recent price movements and provides a solid foundation for technical analysis.",
    "Trading volume shows some irregularities, with occasional spikes or drops that may not be fully explained by market news or events. While overall participation appears fair, these inconsistencies could signal emerging volatility or speculative trading. Caution is advised when interpreting trends in such conditions, as they may not be entirely organic.",
    "Trading volume is highly erratic, with frequent unexplained surges or declines that could indicate wash trading, pump-and-dump activity, or other forms of market manipulation. Such instability undermines the reliability of price action and raises concerns about the asset's trading integrity. Extreme care should be taken before making trading decisions based on this data."
  ),

  '-SCORE2-': (
    "Liquidity & Order Book Depth",
    "The token has deep and active order books with minimal slippage, allowing for large trades to be executed efficiently. This suggests strong market participation and reduces the likelihood of price manipulation or artificial price swings.",
    "Liquidity is moderate, with occasional signs of thin order books or noticeable slippage during peak activity. While trading is possible, large trades may affect price, and caution is advised during volatile periods.",
    "Order books are consistently thin or illiquid, with large spreads and high slippage. This environment is vulnerable to manipulation, and trades can be significantly impacted by low volume. Such conditions are often seen in pump-and-dump schemes or low-trust tokens."
  ),

  '-SCORE3-': (
    "Token Age & Market History",
    "The token has a long and transparent trading history, with years of consistent performance across market cycles. Such longevity typically indicates resilience, maturity, and sustained investor interest.",
    "The token has a moderate trading history, possibly spanning several months. While there are no major red flags, its performance and legitimacy are still being established. Historical context is limited, so extra diligence is required.",
    "The token is newly launched with little to no trading history. This lack of historical data makes it difficult to assess reliability or long-term viability. New tokens are more prone to scams and speculative behavior."
  ),

  '-SCORE4-': (
    "Developer & Team Transparency",
    "The development team is fully doxxed, publicly active, and backed by credible professional profiles and past experience. Transparent communication and community interaction build trust and demonstrate accountability.",
    "Team information is partially available or inconsistently disclosed. While some members may be known, full transparency is lacking. This introduces a moderate level of risk and warrants further research.",
    "The team is anonymous or unverifiable, with no credible presence or history. Lack of accountability and transparency is a major red flag and often associated with fraudulent or short-lived projects."
  ),

  '-SCORE5-': (
    "Smart Contract Audit & Security",
    "The token’s smart contract has undergone one or more independent third-party audits, with no critical vulnerabilities found. This adds a significant layer of security and demonstrates a commitment to best practices.",
    "The smart contract may have had internal reviews or partial audits, but lacks comprehensive third-party verification. While not inherently insecure, the absence of a full audit is a concern that should be weighed.",
    "No known audits or publicly available code reviews exist. The contract may be unaudited or poorly written, making it susceptible to bugs, exploits, or intentional backdoors. Engaging with such tokens poses a high risk."
  ),

  '-SCORE6-': (
    "Exchange Listings & Reputation",
    "The token is listed on major and reputable exchanges with strict vetting processes, indicating a high level of legitimacy and broad market trust. These listings also improve liquidity and user access.",
    "The token is listed on mid-tier or niche exchanges. While this provides some accessibility, these platforms may have looser listing requirements, so extra scrutiny is recommended.",
    "The token is only available on obscure or decentralized exchanges with minimal oversight. Lack of reputable listings may suggest the project has not passed due diligence or is attempting to avoid regulatory scrutiny."
  ),

  '-SCORE7-': (
    "Community & Social Media Presence",
    "The project maintains an active, engaged, and growing community across major platforms. Discussions are organic, with balanced sentiment and developer participation. This signals healthy community trust and project momentum.",
    "Community activity exists but may appear inconsistent, overly promotional, or reliant on giveaways and hype. While engagement is visible, it may not reflect genuine interest or long-term support.",
    "Social media channels are inactive, filled with bots, or lacking genuine user interaction. Projects with fabricated or non-existent communities are often untrustworthy or abandoned."
  ),

  '-SCORE8-': (
    "Transaction Patterns & Anomalies",
    "On-chain activity appears healthy, with a wide distribution of wallets and regular, transparent transactions. This pattern reflects organic use and widespread participation.",
    "Some unusual transaction patterns are present, such as repeated transfers between a small number of wallets or unusual inactivity. These could be harmless but may also signal coordinated behavior or testing for manipulation.",
    "Transactions show clear signs of suspicious behavior: wallet clustering, circular transfers, or single-wallet dominance. These red flags are often seen in scams, wash trading, or exit strategies."
  ),

  '-SCORE9-': (
    "Whitepaper & Roadmap Execution",
    "The whitepaper is clear, detailed, and technically sound, with a roadmap that matches delivered progress. Regular updates and achievements reflect genuine commitment and execution.",
    "The whitepaper presents general ideas but lacks technical depth or realistic goals. Progress on the roadmap may be slow or unclear, raising questions about the project's capacity to deliver.",
    "The whitepaper is vague, filled with buzzwords, or not publicly available. No discernible progress on the roadmap exists. This is a major indicator of a low-effort or deceptive project."
  ),

  '-SCORE10-': (
    "Regulatory Compliance & Legal Standing",
    "The project adheres to relevant regulations, conducts proper KYC/AML procedures, and avoids jurisdictions known for fraudulent activity. This adds legitimacy and reduces legal risk.",
    "Regulatory compliance is unclear or inconsistently communicated. While no legal issues are known, a lack of transparency in this area warrants caution and further investigation.",
    "The token has been flagged by regulators or operates in clear violation of financial laws. Such exposure carries high legal risk and is commonly associated with scams or short-lived projects."
  ),
}

main_descriptions = {
    'Low Risk': (
        "This coin has been assessed as **Low Risk**, indicating a strong market position with high liquidity, "
        "consistent trading volume, and relatively low price volatility. It likely has robust community support, "
        "ongoing development activity, and positive sentiment across major platforms. Historical data suggests "
        "stable performance over time, making it a safer choice for conservative investors."
    ),
    'Low-Medium Risk': (
        "This coin is categorized as **Low-Medium Risk**, meaning it generally shows stability with occasional "
        "volatility spikes. It maintains decent trading activity, reasonable liquidity, and ongoing but possibly "
        "slower development progress. Market sentiment may vary, but overall confidence in the project remains steady."
    ),
    'Medium-High Risk': (
        "The coin is considered **Medium-High Risk**, indicating notable price swings, inconsistent trading volume, "
        "and possible concerns around project updates or development momentum. While it may have potential, "
        "market confidence is mixed and the asset may react strongly to news or external factors. Caution is advised."
    ),
    'High Risk': (
        "This coin falls under the **High Risk** category, showing signs of major volatility, low trading volume, "
        "or poor liquidity. It may lack sustained developer activity or community engagement, and could be highly "
        "sensitive to speculation or market rumors. Extreme caution is recommended, especially for risk-averse investors."
    )
}


def get_main_desc(score):
  int_score = int(score)
  if int_score > 80:
    key = 'Low Risk'
  elif int_score > 60:
    key = 'Low-Medium Risk'
  elif int_score > 40:
    key = 'Medium-High Risk'
  elif int_score > 1:
    key = 'High Risk'

  return main_descriptions[key]
