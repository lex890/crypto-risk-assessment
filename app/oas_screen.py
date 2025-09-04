import FreeSimpleGUI as sg
from .score_dict  import get_main_desc
from .plot_graphs import pie_charts
from .score_dict  import get_category_desc, get_descriptive_info

HEADLINE_FONT = ("Segoe UI", 24, "bold")
BACK_FONT     = ("Segoe UI", 18, "bold")
BODY_FONT     = ("Calibri", 12, "bold")
MAIN_DESC     = ("Segoe UI", 15)
CATEGORY_FONT = ("Calibri",   14, "bold")
DESC_FONT     = ("Calibri", 10)
BODY_FONT_COLOR = '#8e8e8e'

rv_bg  = '#ef476f'
ol_bg  = '#ffd166'
el_bg  = '#06d6a0'
am_bg  = '#118ab2'
bi_bg  = '#2e4e5a'
bnk_bg = "#ffffff"
# generate OAS
def generate_oas_window(current_row, oas_table, vol_table, current_coin):
    # Donut Graph OAS
    score = [
        [  
            sg.Canvas(
                key="-MAINSCORE-WINDOW-", 
                size=(75, 75), 
                tooltip='Overall Assessment Score',
                background_color='#F0F0F0')
        ]
    ]
    
    relative_vol  = current_row[13]
    orderbook_liq = current_row[14]
    exchange_lis  = current_row[15]
    anomaly_pat   = current_row[16]
    binary_sc     = current_row[17:22]
    box_pad = ((20, 15), 0)
    percent_pad = ((5, 0), 0)
    category_bar_size = (5, 6)
    rv_box = [
        [
            sg.Text('', size=category_bar_size, background_color=rv_bg, border_width=0, relief='solid', pad=box_pad),
            sg.Column([
                    [
                        sg.Text('REALIZED VOLATILITY', font=CATEGORY_FONT, text_color=rv_bg, pad=((0, 0), 0), size=(14, 2)),
                    ],
                    [
                        sg.Text(f'{round((float(relative_vol)*10)*0.20, 1)}%', font=CATEGORY_FONT, pad=percent_pad)
                    ]
                ],
                pad=(0, 0)
            )
        ]
    ]

    ol_box = [
        [
            sg.Text('', size=category_bar_size, background_color=ol_bg, border_width=0, relief='solid', pad=box_pad),
            sg.Column([
                    [
                        sg.Text('LIQUIDITY AND ORDER BOOK DEPTH', font=CATEGORY_FONT, text_color=ol_bg, pad=((0, 0), 0), size=(14, 2)),
                    ],
                    [
                        sg.Text(f'{round((float(orderbook_liq)*10)*0.20, 1)}%', font=CATEGORY_FONT, pad=percent_pad)
                    ]
                ],
                pad=(0, 0)
            )
        ]
    ]

    el_box = [
        [
            sg.Text('', size=category_bar_size, background_color=el_bg, border_width=0, relief='solid', pad=box_pad),
            sg.Column([
                    [
                        sg.Text('EXCHANGE LISTINGS AND REPUTATION', font=CATEGORY_FONT, text_color=el_bg, pad=((0, 0), 0), size=(14, 2)),
                    ],
                    [
                        sg.Text(f'{round((float(exchange_lis)*10)*0.20, 1)}%', font=CATEGORY_FONT, pad=percent_pad)
                    ]
                ],
                pad=(0, 0)
            )
        ]
    ]

    am_box = [
        [
            sg.Text('', size=category_bar_size, background_color=am_bg, border_width=0, relief='solid', pad=box_pad),
            sg.Column([
                    [
                        sg.Text('TRANSACTION PATTERNS & ANOMALY', font=CATEGORY_FONT, text_color=am_bg, pad=((0, 0), 0), size=(14, 2)),
                    ],
                    [
                        sg.Text(f'{round((float(anomaly_pat)*10)*0.20, 1)}%', font=CATEGORY_FONT, pad=percent_pad)
                    ]
                ],
                pad=(0, 0)
            )
        ]
    ]

    bn_box = [
        [
            sg.Text('', size=category_bar_size, background_color=bi_bg, border_width=0, relief='solid', pad=box_pad),
            sg.Column([
                    [
                        sg.Text('BINARY METRICS', font=CATEGORY_FONT, text_color=bi_bg, pad=((0, 0), 0), size=(7, 2)),
                    ],
                    [
                        sg.Text(f'{round(sum(map(float, binary_sc)) * 4, 1)}%', font=CATEGORY_FONT, pad=percent_pad)
                    ]
                ],
                pad=(0, 0)
            )
        ]
    ]

    assessment_guide_box = [
        [
            sg.Column(rv_box, pad=((0, 0), (0, 0)))
        ],
        [
            sg.Column(ol_box, pad=((0, 0), (0, 0)))
        ],
        [
            sg.Column(el_box, pad=((0, 0), (0, 0)))
        ],
        [
            sg.Column(am_box, pad=((0, 0), (0, 0)))
        ],
        [
            sg.Column(bn_box, pad=((0, 0), (0, 0)))
        ]
    ]
    descriptive_guide_pad  = ((0, 0), (0, 0))
    descriptive_guide_size = (65, 5)
    bar_size = (1, 6)
    bnk_pad = ((0, 0), 0)
    descriptive_guide_box  = [
        [
            # volatility desc
            sg.Text('', size=bar_size, background_color=bnk_bg, border_width=0, relief='solid', pad=bnk_pad),
            sg.Text(get_category_desc('-VOLATILITY-', relative_vol)[1], pad=descriptive_guide_pad, font=DESC_FONT, size=descriptive_guide_size)
        ],
        [
            # liquidity desc
            sg.Text('', size=bar_size, background_color=bnk_bg, border_width=0, relief='solid', pad=bnk_pad),
            sg.Text(get_category_desc('-LIQUIDITY-', orderbook_liq)[1], pad=descriptive_guide_pad, font=DESC_FONT, size=descriptive_guide_size)
        ],
        [
            # exchange desc
            sg.Text('', size=bar_size, background_color=bnk_bg, border_width=0, relief='solid', pad=bnk_pad),
            sg.Text(get_category_desc('-EXCHANGE-', exchange_lis)[1], pad=descriptive_guide_pad, font=DESC_FONT, size=descriptive_guide_size)
        ],
        [
            # anomaly 
            sg.Text('', size=bar_size, background_color=bnk_bg, border_width=0, relief='solid', pad=bnk_pad),
            sg.Text(get_category_desc('-ANOMALY-', anomaly_pat)[1], pad=descriptive_guide_pad, font=DESC_FONT, size=descriptive_guide_size)
        ],
        [
            # binary scores
            sg.Text('', size=bar_size, background_color=bnk_bg, border_width=0, relief='solid', pad=bnk_pad),
            sg.Text(get_descriptive_info(binary_sc), pad=descriptive_guide_pad, font=DESC_FONT, size=descriptive_guide_size)
        ]
    ]


    header_pad = ((50, 0), (50, 0))
    goback_pad = ((0, 20), (50, 0))
    ext_btn_pad = ((0, 70), (50, 0))
    sub_txt_pad = ((50, 0), (5, 0))
    hrz_sep_pad = ((50, 50), (10, 0))
    oas_guide_pad = ((50, 0), (0, 0))

    oas_header = [
        [
            sg.Text('Overall Assessment Score Dashboard', font=HEADLINE_FONT, pad=header_pad), 
            sg.Push(),
            sg.Text('Go Back', font=BACK_FONT, pad=goback_pad, enable_events=True,key='-WEXIT-'),  
            sg.Image('app/assets/images/right-arrow.png', pad=ext_btn_pad, enable_events=True, key='-EXIT-')
        ],
        [
            sg.Text('Get a clear overview of your Overall Assessment Score (OAS) along with actionable insights for improvement.', font=BODY_FONT, text_color=BODY_FONT_COLOR, pad=sub_txt_pad), 
            sg.Push()
        ],
        [sg.HorizontalSeparator(pad=hrz_sep_pad)],
    ]

    analysis_font = ('Segoe UI', 24, 'bold')
    analysis_clr = '#2e4e5a'
    oas_analysis = [
        [sg.Text(f'Score Summary for {current_coin}', pad=((0, 0), (40, 10)), font=analysis_font, text_color=analysis_clr)],
        [
            sg.Column(score, pad=((0, 0), (0, 0))),
            sg.Text(get_main_desc(pie_charts[0][2]), size=(40, 10), font=MAIN_DESC,pad=((0, 120), (0, 0))),
            
        ],
        [
            sg.Column(assessment_guide_box, pad=oas_guide_pad),
            sg.Column(descriptive_guide_box, pad=((0, 0), (0, 0)), vertical_alignment='top'),
            
        ]
    ]

    oas_tables = [
        [ sg.Column(oas_table, pad=((0, 0), (0, 0))) ],
        [ sg.Column(vol_table, pad=((0, 0), (0, 0))) ]
    ]

    oas_body = [
        [oas_header],  # This is fine because oas_header is a list of rows.
        [
            sg.Push(),
            sg.Column(oas_analysis, pad=((0, 0), (0, 0))),  # Left side
            sg.Column(oas_tables, pad=((0, 0), (0, 0))),    # Right side
            sg.Push()
        ]
    ]

    return [
        oas_body
    ]