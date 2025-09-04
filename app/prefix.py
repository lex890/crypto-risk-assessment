# Define UI element keys that will respond to hover effects
KEY_PREFIXES = ('-rank', '-icon', '-name', '-symbol', '-oas',
                '-price', '-hour', '-day', '-week', '-mcap',
                '-KEYSTORE-', '-CRYPTO-NAME-TOGGLE-', '-DEMOMODE-',
                '-CRYPTO-LOGO-TOGGLE-', '-CRYPTO-LINKER-', 
                '-SAVEKEY-', 'Clear', 'Confirm', '-HYPERLINK-','-CATEGORY0-', '-CATEGORY1-', '-CATEGORY2-', '-HEADERICON-',
                 '-CATEGORY3-', '-CATEGORY4-', '-CATEGORY5-', '-CATEGORY6-', '-CATEGORY7-', '-CATEGORY8-', '-VOLATILITY-', '-VOLATILITY1-', '-LIQUIDITY-', '-LIQUIDITY1-','-EXCHANGE-', '-EXCHANGE1-', '-ANOMALY-', '-ANOMALY1-',  '-V-WIMG-', '-V-WMSG-', '-L-WIMG-', '-L-WMSG-', '-E-WIMG-', '-E-WMSG-', '-A-WIMG-', '-A-WMSG-', '-RV-IMAGE-', '-OL-IMAGE-', '-EL-IMAGE-', '-AP-IMAGE-', '-DT-CHECK-', '-CP-CHECK-', '-WA-CHECK-', '-RC-CHECK-', '-SC-CHECK-', '-ALPHA-', '-NUMBER-', '-PRICE-', '-DT-EXPAND-')
TABLE_PREFIXES = ('-rank', '-icon', '-name', '-symbol', '-oas',
                '-price', '-hour', '-day', '-week', '-mcap')
ASSESSMENT_PREFIXES = ('-CATEGORY0-', '-CATEGORY1-', '-CATEGORY2-',
                 '-CATEGORY3-', '-CATEGORY4-', '-CATEGORY5-', '-CATEGORY6-', '-CATEGORY7-', '-CATEGORY8-', '-VOLATILITY-', '-VOLATILITY1-', '-LIQUIDITY-', '-LIQUIDITY1-','-EXCHANGE-', '-EXCHANGE1-', '-ANOMALY-', '-ANOMALY1-', '-V-WIMG-', '-V-WMSG-', '-L-WIMG-', '-L-WMSG-', '-E-WIMG-', '-E-WMSG-', '-A-WIMG-', '-A-WMSG-', '-RV-IMAGE-', '-OL-IMAGE-', '-EL-IMAGE-', '-AP-IMAGE-', '-DT-CHECK-', '-CP-CHECK-', '-WA-CHECK-', '-RC-CHECK-', '-SC-CHECK-', '-DT-EXPAND-')
KEY_ACCESS = {
    '-VOLATILITY-' : '-VOLATILITY-',
    '-CATEGORY0-'  : '-VOLATILITY-',
    '-V-WIMG-'     : '-VOLATILITY-',
    '-V-WMSG-'     : '-VOLATILITY-',
    '-RV-IMAGE-'   : '-VOLATILITY-',
    '-VOLATILITY1-': '-VOLATILITY-',

    '-LIQUIDITY-'  : '-LIQUIDITY-',
    '-CATEGORY1-'  : '-LIQUIDITY-',
    '-L-WIMG-'     : '-LIQUIDITY-',
    '-L-WMSG-'     : '-LIQUIDITY-',
    '-OL-IMAGE-'   : '-LIQUIDITY-',
    '-LIQUIDITY-1' : '-LIQUIDITY-',

    '-EXCHANGE-'   : '-EXCHANGE-',
    '-CATEGORY2-'  : '-EXCHANGE-',
    '-E-WIMG-'     : '-EXCHANGE-',
    '-E-WMSG-'     : '-EXCHANGE-',
    '-EL-IMAGE-'   : '-EXCHANGE-',
    '-EXCHANGE1-'  : '-EXCHANGE-',

    '-ANOMALY-'    : '-ANOMALY-',
    '-CATEGORY3-'  : '-ANOMALY-',
    '-A-WIMG-'     : '-ANOMALY-',
    '-A-WMSG-'     : '-ANOMALY-',
    '-AP-IMAGE-'   : '-ANOMALY-',
    '-ANOMALY1-'   : '-ANOMALY-',   
}

BINARY_ACCESS = {
    '-DT-CHECK-'  : '-DEVELOPER-',
    '-CATEGORY4-' : '-DEVELOPER-',

    '-CP-CHECK-'  : '-COMMUNITY-',
    '-CATEGORY5-' : '-COMMUNITY-',

    '-WA-CHECK-'  : '-WHITEPAPER-',
    '-CATEGORY6-' : '-WHITEPAPER-',

    '-RC-CHECK-'  : '-REGULATORY-',
    '-CATEGORY7-' : '-REGULATORY-',

    '-SC-CHECK-'  : '-CONTRACT-',
    '-CATEGORY8-' : '-CONTRACT-',  
}