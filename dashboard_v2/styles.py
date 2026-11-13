import streamlit as st


def apply_custom_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {
            --ink: #0B1F3A;
            --navy: #16365F;
            --blue: #2F6FD0;
            --teal: #0E9F8E;
            --amber: #F4A62A;
            --red: #D9473F;
            --tint: #EEF3F8;
            --line: #DCE5EF;
            --muted: #5B6B7E;
            --card-shadow: 0 1px 2px rgba(11, 31, 58, 0.05), 0 14px 30px -18px rgba(11, 31, 58, 0.28);
        }

        html, body, .stApp, .stMarkdown, button, input, textarea, select {
            font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
        }

        #MainMenu, footer {
            visibility: hidden;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

        .stApp {
            color: var(--ink);
            background:
                radial-gradient(900px 480px at 8% -8%, rgba(47, 111, 208, 0.13), transparent 62%),
                radial-gradient(760px 440px at 98% 0%, rgba(14, 159, 142, 0.11), transparent 58%),
                linear-gradient(180deg, #F7FAFD 0%, #EAF0F7 100%);
        }

        .block-container {
            padding-top: 1.6rem;
            padding-bottom: 3rem;
            max-width: 1280px;
        }

        .stApp h2, .stApp h3 {
            color: var(--ink);
            font-weight: 700;
            letter-spacing: -0.015em;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0B1F3A 0%, #0F2A4D 60%, #133764 100%);
            border-right: none;
            box-shadow: 12px 0 32px -18px rgba(11, 31, 58, 0.6);
        }

        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #E6EEF8 !important;
        }

        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] textarea,
        section[data-testid="stSidebar"] div[data-baseweb="select"] * {
            color: var(--ink) !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSliderThumbValue"] {
            color: #FFFFFF !important;
        }

        .top-header {
            position: relative;
            overflow: hidden;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.9rem;
            padding: 1.55rem 1.85rem;
            margin-bottom: 1.3rem;
            border-radius: 20px;
            color: #FFFFFF;
            background: linear-gradient(120deg, #0B1F3A 0%, #16365F 55%, #245BA8 100%);
            box-shadow: 0 22px 44px -22px rgba(11, 31, 58, 0.65);
        }

        .top-header::before {
            content: "";
            position: absolute;
            right: -70px;
            top: -110px;
            width: 300px;
            height: 300px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0) 66%);
            pointer-events: none;
        }

        .top-header::after {
            content: "";
            position: absolute;
            left: 38%;
            bottom: -130px;
            width: 260px;
            height: 260px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(14, 159, 142, 0.35), rgba(14, 159, 142, 0) 66%);
            pointer-events: none;
        }

        .top-header > * {
            position: relative;
            z-index: 2;
        }

        .top-header h1 {
            margin: 0;
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: #FFFFFF;
        }

        .top-header .subtitle {
            margin: 0.3rem 0 0 0;
            font-size: 0.95rem;
            font-weight: 400;
            color: #C9D9EC;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.3rem 0.75rem;
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            border: 1px solid transparent;
        }

        .badge-sample {
            background: var(--amber);
            color: var(--ink);
        }

        .badge-cache {
            background: var(--blue);
            color: #FFFFFF;
        }

        .badge-live {
            background: var(--teal);
            color: #FFFFFF;
        }

        .badge-live::before {
            content: "";
            width: 0.42rem;
            height: 0.42rem;
            border-radius: 50%;
            background: #FFFFFF;
            box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.3);
        }

        .badge-status-paused {
            background: var(--amber);
            color: var(--ink);
        }

        .badge-status-completed {
            background: var(--teal);
            color: #FFFFFF;
        }

        .badge-dual {
            background: var(--navy);
            color: #FFFFFF;
            border-color: rgba(47, 111, 208, 0.7);
            margin-left: 0.35rem;
            font-size: 0.62rem;
        }

        .fault-banner {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            padding: 0.8rem 1.15rem;
            margin-bottom: 1rem;
            border-radius: 14px;
            font-weight: 700;
            letter-spacing: 0.01em;
            color: #FFFFFF;
            background: linear-gradient(135deg, #D9473F 0%, #B8322B 100%);
            box-shadow: 0 14px 28px -14px rgba(184, 50, 43, 0.75);
        }

        .fault-banner::before {
            content: "!";
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.5rem;
            height: 1.5rem;
            border-radius: 50%;
            background: #FFFFFF;
            color: #B8322B;
            font-weight: 800;
            flex-shrink: 0;
        }

        .section-card {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 1.2rem 1.35rem;
            margin-bottom: 1rem;
            box-shadow: var(--card-shadow);
        }

        .kpi-card {
            position: relative;
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 1.1rem 1.2rem 1rem 1.2rem;
            box-shadow: var(--card-shadow);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }

        .kpi-card::before {
            content: "";
            position: absolute;
            left: 1.2rem;
            top: 0;
            width: 2.4rem;
            height: 3px;
            border-radius: 0 0 4px 4px;
            background: linear-gradient(90deg, var(--blue), var(--teal));
        }

        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 2px 4px rgba(11, 31, 58, 0.06), 0 20px 36px -18px rgba(11, 31, 58, 0.34);
        }

        .kpi-label {
            margin-bottom: 0.3rem;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--muted);
        }

        .kpi-value {
            font-size: 1.9rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: var(--ink);
            font-variant-numeric: tabular-nums;
        }

        .metrics-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            overflow: hidden;
            font-size: 0.92rem;
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 16px;
            box-shadow: var(--card-shadow);
        }

        .metrics-table th {
            padding: 0.85rem 1rem;
            text-align: left;
            font-size: 0.68rem;
            font-weight: 600;
            letter-spacing: 0.09em;
            text-transform: uppercase;
            color: #D5E3F4;
            background: linear-gradient(180deg, #17375F 0%, #0F2A4D 100%);
        }

        .metrics-table td {
            padding: 0.9rem 1rem;
            vertical-align: middle;
            color: var(--ink);
            border-bottom: 1px solid #EDF2F8;
            font-variant-numeric: tabular-nums;
        }

        .metrics-table td small {
            color: var(--muted);
            font-size: 0.76rem;
        }

        .metrics-table tbody tr {
            transition: background 0.12s ease;
        }

        .metrics-table tbody tr:hover td {
            background: #F3F8FE;
        }

        .metrics-table tr:last-child td {
            border-bottom: none;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            padding: 0.2rem 0.62rem;
            border-radius: 999px;
            font-size: 0.66rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            border: 1px solid transparent;
        }

        .pill-approved {
            background: #E1F6F2;
            color: #0A7A6D;
            border-color: #B9E7DF;
        }

        .pill-flagged {
            background: #FEF1D8;
            color: #946000;
            border-color: #F7DCA3;
        }

        .pill-rejected {
            background: #FBE3E1;
            color: #B3322B;
            border-color: #F3C0BC;
        }

        .pill-na {
            background: #E8EDF3;
            color: #55667B;
            border-color: #D3DDE8;
        }

        .conf-wrap {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            min-width: 130px;
            font-variant-numeric: tabular-nums;
        }

        .conf-track {
            flex: 1;
            height: 8px;
            overflow: hidden;
            border-radius: 999px;
            background: #E3EAF3;
        }

        .conf-fill {
            height: 100%;
            border-radius: 999px;
            transition: width 0.3s ease;
        }

        .filing-table {
            width: 100%;
            margin-top: 0.5rem;
            border-collapse: separate;
            border-spacing: 0;
            overflow: hidden;
            font-family: ui-monospace, 'SF Mono', Consolas, 'Liberation Mono', monospace;
            font-size: 0.84rem;
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 12px;
        }

        .filing-table th {
            padding: 0.55rem 0.8rem;
            text-align: left;
            font-weight: 600;
            color: var(--ink);
            background: #F1F5FA;
            border-bottom: 1px solid var(--line);
        }

        .filing-table td {
            padding: 0.5rem 0.8rem;
            color: var(--ink);
            border-bottom: 1px solid #EEF3F8;
        }

        .filing-row-highlight td {
            background: #FFF6E0 !important;
            font-weight: 700;
        }

        .filing-cell-highlight {
            padding: 0.15rem 0.45rem;
            border-radius: 6px;
            font-weight: 700;
            color: var(--ink);
            background: var(--amber);
        }

        .source-box {
            margin: 0.55rem 0;
            padding: 0.85rem 1rem;
            font-family: ui-monospace, 'SF Mono', Consolas, 'Liberation Mono', monospace;
            font-size: 0.88rem;
            color: var(--ink);
            background: #F4F8FD;
            border: 1px solid #DCE7F3;
            border-left: 4px solid var(--blue);
            border-radius: 0 12px 12px 0;
        }

        div.stButton > button,
        div.stDownloadButton > button,
        div.stFormSubmitButton > button {
            padding: 0.5rem 1.05rem;
            font-weight: 600;
            color: var(--ink);
            background: #FFFFFF;
            border: 1px solid #CDD9E8;
            border-radius: 10px;
            box-shadow: 0 1px 2px rgba(11, 31, 58, 0.06);
            transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease;
        }

        div.stButton > button:hover,
        div.stDownloadButton > button:hover,
        div.stFormSubmitButton > button:hover {
            color: var(--blue);
            border-color: var(--blue);
            transform: translateY(-1px);
            box-shadow: 0 8px 16px -8px rgba(47, 111, 208, 0.45);
        }

        div.stButton > button[kind="primary"],
        div.stFormSubmitButton > button[kind="primary"],
        div.stDownloadButton > button[kind="primary"] {
            color: #FFFFFF;
            background: linear-gradient(180deg, #3F7FE0 0%, #2F6FD0 100%);
            border-color: #2A63BC;
            box-shadow: 0 8px 16px -8px rgba(47, 111, 208, 0.65);
        }

        div.stButton > button[kind="primary"]:hover,
        div.stFormSubmitButton > button[kind="primary"]:hover,
        div.stDownloadButton > button[kind="primary"]:hover {
            color: #FFFFFF;
            filter: brightness(1.06);
        }

        div.stButton > button:active {
            transform: translateY(0);
            box-shadow: none;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.3rem;
            padding: 0.3rem;
            background: #E1E9F3;
            border-radius: 12px;
            border-bottom: none;
        }

        .stTabs button[data-baseweb="tab"] {
            height: auto;
            padding: 0.5rem 1.05rem;
            font-weight: 600;
            color: #4A607A;
            background: transparent;
            border-radius: 9px;
        }

        .stTabs button[data-baseweb="tab"][aria-selected="true"] {
            color: var(--ink);
            background: #FFFFFF;
            box-shadow: 0 1px 3px rgba(11, 31, 58, 0.16);
        }

        .stTabs [data-baseweb="tab-highlight"],
        .stTabs [data-baseweb="tab-border"] {
            display: none;
        }

        div[data-baseweb="input"],
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] {
            border-radius: 10px;
            border: 1px solid #CDD9E8;
            background: #FFFFFF;
        }

        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="textarea"]:focus-within {
            border-color: var(--blue);
            box-shadow: 0 0 0 3px rgba(47, 111, 208, 0.18);
        }

        div[data-testid="stAlert"] {
            border-radius: 12px;
            border: 1px solid var(--line);
        }

        div[data-testid="stMetric"] {
            padding: 0.85rem 1.05rem;
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 14px;
            box-shadow: var(--card-shadow);
        }

        details[data-testid="stExpander"] {
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 14px;
            box-shadow: var(--card-shadow);
        }

        div[data-testid="stDataFrame"] {
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: 12px;
        }

        .check-line {
            margin-bottom: 4px;
            line-height: 1.55;
        }

        .row-flagged td {
            background: #FFFBF1;
        }

        .metrics-table tbody tr.row-flagged:hover td {
            background: #FFF3D9;
        }

        .kpi-hint {
            margin-top: 0.25rem;
            font-size: 0.76rem;
            color: var(--muted);
        }

        .stepper {
            display: flex;
            align-items: center;
            padding: 0.95rem 1.3rem;
            margin-bottom: 1.1rem;
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 16px;
            box-shadow: var(--card-shadow);
            overflow-x: auto;
        }

        .step {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            white-space: nowrap;
        }

        .step-dot {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 1.7rem;
            height: 1.7rem;
            border-radius: 50%;
            font-size: 0.78rem;
            font-weight: 700;
        }

        .step-label {
            font-size: 0.82rem;
            font-weight: 600;
        }

        .step-link {
            flex: 1;
            min-width: 18px;
            height: 2px;
            margin: 0 0.8rem;
            background: #DCE5EF;
        }

        .step-done .step-dot {
            color: #FFFFFF;
            background: var(--teal);
        }

        .step-active .step-dot {
            color: var(--ink);
            background: var(--amber);
            box-shadow: 0 0 0 5px rgba(244, 166, 42, 0.25);
        }

        .step-pending .step-dot {
            color: #6B7C93;
            background: #E3EAF3;
        }

        .step-pending .step-label {
            color: #6B7C93;
        }

        .welcome-card {
            padding: 1.6rem 1.8rem;
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 18px;
            box-shadow: var(--card-shadow);
        }

        .welcome-card h3 {
            margin: 0 0 0.9rem 0;
        }

        .welcome-step {
            display: flex;
            align-items: flex-start;
            gap: 0.8rem;
            margin-bottom: 0.8rem;
            color: var(--ink);
        }

        .welcome-step .num {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            width: 1.7rem;
            height: 1.7rem;
            border-radius: 50%;
            font-size: 0.8rem;
            font-weight: 700;
            color: #FFFFFF;
            background: var(--blue);
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 16px;
        }

        .review-title {
            margin: 0 0 0.35rem 0;
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.01em;
            color: var(--ink);
        }

        .review-reason {
            margin: 0 0 0.7rem 0;
            color: var(--muted);
        }

        section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
        section[data-testid="stSidebar"] div[data-baseweb="input"],
        section[data-testid="stSidebar"] div[data-baseweb="base-input"],
        section[data-testid="stSidebar"] input {
            background-color: #FFFFFF !important;
            color: #0B1F3A !important;
            -webkit-text-fill-color: #0B1F3A !important;
        }

        section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
            fill: #0B1F3A;
        }

        .stTabs [data-baseweb="tab-list"] button,
        .stTabs [data-baseweb="tab-list"] button p {
            color: #3C5370 !important;
            font-weight: 600;
        }

        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"],
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {
            color: #0B1F3A !important;
        }

        .user-chip {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            margin: 0.4rem 0 0.6rem 0;
            padding: 0.6rem 0.75rem;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.14);
        }

        .avatar {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            width: 2.2rem;
            height: 2.2rem;
            border-radius: 50%;
            font-size: 0.82rem;
            font-weight: 700;
            color: #FFFFFF;
            background: linear-gradient(135deg, #4C8BEB, #0E9F8E);
        }

        .user-name {
            font-size: 0.9rem;
            font-weight: 600;
            line-height: 1.15;
            color: #FFFFFF;
        }

        .user-role {
            font-size: 0.74rem;
            color: #A9BFD8;
        }

        .header-user {
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.35rem 0.85rem 0.35rem 0.4rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.22);
            vertical-align: middle;
        }

        .header-user .avatar {
            width: 1.9rem;
            height: 1.9rem;
            font-size: 0.72rem;
        }

        .header-user .user-name {
            font-size: 0.8rem;
        }

        .ring-wrap {
            display: flex;
            align-items: center;
            gap: 0.9rem;
            margin-bottom: 0.8rem;
        }

        .ring-label {
            font-size: 0.85rem;
            font-weight: 600;
            line-height: 1.35;
            color: var(--ink);
        }

        .ring-label small {
            font-weight: 500;
            color: var(--muted);
        }

        .company-card {
            margin-bottom: 0.5rem;
            padding: 1rem 1.1rem;
            background: #FFFFFF;
            border: 1px solid var(--line);
            border-radius: 16px;
            box-shadow: var(--card-shadow);
        }

        .company-ticker {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: #1D4E9E;
            background: #E8F0FB;
        }

        .company-name {
            margin: 0.55rem 0 0 0;
            font-weight: 600;
            color: var(--ink);
        }

        section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] {
            background: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            box-shadow: none !important;
        }

        section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] p,
        section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] span {
            color: #FFFFFF !important;
        }

        section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover {
            background: rgba(255, 255, 255, 0.2) !important;
        }

        .company-card {
            min-height: 7.2rem;
        }

        .metrics-table {
            table-layout: fixed;
        }

        .pill {
            white-space: nowrap;
        }

        div.stButton > button,
        div.stDownloadButton > button,
        div.stFormSubmitButton > button {
            padding: 0.5rem 0.55rem;
            white-space: nowrap;
        }

        button[data-testid^="stBaseButton"] p,
        div.stButton > button p {
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: nowrap;
            font-size: 0.9rem;
        }

        .kpi-value {
            font-size: clamp(1.3rem, 1.8vw, 1.9rem);
            white-space: nowrap;
        }

        .kpi-label {
            font-size: 0.66rem;
            letter-spacing: 0.06em;
        }

        .kpi-card {
            padding: 1rem 1rem 0.9rem 1rem;
        }

        .conf-wrap {
            min-width: 0;
            gap: 0.45rem;
        }

        .conf-track {
            min-width: 36px;
        }

        .metrics-table th {
            padding: 0.8rem 0.7rem;
            font-size: 0.64rem;
            letter-spacing: 0.05em;
        }

        .metrics-table td {
            padding: 0.85rem 0.7rem;
        }

        .table-scroll {
            overflow-x: auto;
            border-radius: 16px;
        }

        .table-scroll .metrics-table {
            min-width: 880px;
        }

        .metrics-table td {
            word-break: break-word;
        }

        .metrics-table td:last-child {
            font-size: 0.84rem;
        }

        .checks-summary {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 0.7rem;
        }

        .checks-row {
            display: grid;
            grid-template-columns: 8.5rem 12rem 1fr;
            gap: 0.9rem;
            align-items: start;
            padding: 0.6rem 0;
            font-size: 0.88rem;
            border-bottom: 1px solid #EDF2F8;
        }

        .checks-row:last-child {
            border-bottom: none;
        }

        .checks-name {
            font-weight: 600;
            color: var(--ink);
        }

        .checks-name small {
            font-weight: 400;
            color: var(--muted);
        }

        .checks-reason {
            color: #2D4260;
            word-break: break-word;
        }

        section[data-testid="stSidebar"] .stCaption,
        section[data-testid="stSidebar"] small,
        section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {
            color: #BFD0E6 !important;
        }

        .completion-card {
            margin-bottom: 1rem;
            padding: 1.05rem 1.3rem;
            border-radius: 16px;
            color: var(--ink);
            background: linear-gradient(135deg, #E1F6F2, #EAF3FF);
            border: 1px solid #BDE8E1;
        }

        .stat-row {
            display: flex;
            justify-content: space-between;
            padding: 0.4rem 0;
            border-bottom: 1px solid #EDF2F8;
            font-size: 0.88rem;
        }

        .stat-row span:first-child {
            color: var(--muted);
        }

        .stat-row span:last-child {
            font-weight: 700;
            color: var(--ink);
            font-variant-numeric: tabular-nums;
        }

        @media (prefers-reduced-motion: reduce) {
            .kpi-card,
            .metrics-table tbody tr,
            .conf-fill,
            div.stButton > button {
                transition: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
