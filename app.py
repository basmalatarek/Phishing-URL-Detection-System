import streamlit as st
import re
import math
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from urllib.parse import urlparse

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PhishGuard AI",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# THEME STATE
# ─────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

dark = st.session_state.dark_mode

# ── Theme tokens ──────────────────────────────
if dark:
    BG          = "#050d1a"
    BG2         = "#0c1a2e"
    BG3         = "#07111e"
    BORDER      = "#0d3460"
    TEXT        = "#c9d8f0"
    TEXT_DIM    = "#5a7fa8"
    CARD_SHADOW = "0 0 40px rgba(0,112,243,0.12)"
    INPUT_CLR   = "#00f5d4"
    PLOTLY_BG   = "rgba(5,13,26,0)"
    PLOTLY_GRID = "#0d2a50"
    PLOTLY_TEXT = "#c9d8f0"
    SECTION_CLR = "#2a5a8a"
    INFO_BORDER = "#0070f3"
    HERO_SUBTITLE = "#5a7fa8"
else:
    BG          = "#f0f4fb"
    BG2         = "#ffffff"
    BG3         = "#e8eef8"
    BORDER      = "#c0d0e8"
    TEXT        = "#1a2a4a"
    TEXT_DIM    = "#5a6a8a"
    CARD_SHADOW = "0 4px 24px rgba(0,80,180,0.10)"
    INPUT_CLR   = "#0055c8"
    PLOTLY_BG   = "rgba(240,244,251,0)"
    PLOTLY_GRID = "#d0ddef"
    PLOTLY_TEXT = "#1a2a4a"
    SECTION_CLR = "#3a70c0"
    INFO_BORDER = "#2277ee"
    HERO_SUBTITLE = "#6a80aa"

# ─────────────────────────────────────────────
# DYNAMIC CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;600;900&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Exo 2', sans-serif;
    background-color: {BG} !important;
    color: {TEXT};
    transition: background-color 0.4s, color 0.4s;
}}
#MainMenu, footer, header {{visibility: hidden;}}

.hero-title {{
    font-family: 'Exo 2', sans-serif;
    font-weight: 900;
    font-size: clamp(2.4rem, 6vw, 3.8rem);
    background: linear-gradient(135deg, #00f5d4 0%, #0070f3 60%, #9b59b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    letter-spacing: -1px;
    line-height: 1.1;
    margin-bottom: 0.2rem;
}}
.hero-sub {{
    text-align: center;
    color: {HERO_SUBTITLE};
    font-size: 0.95rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-weight: 300;
    margin-bottom: 2.5rem;
}}
.card {{
    background: {BG2};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 2rem 2.2rem;
    box-shadow: {CARD_SHADOW};
    margin-bottom: 1.5rem;
}}
.stTextInput > div > div > input {{
    background: {BG3} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {INPUT_CLR} !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: #0070f3 !important;
    box-shadow: 0 0 0 3px rgba(0,112,243,0.18) !important;
}}
.stTextInput > div > div > input::placeholder {{
    color: {'#2a4a6a' if dark else '#8aaccc'} !important;
}}
.stButton > button {{
    background: linear-gradient(135deg, #0070f3, #00b4d8) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 1px !important;
    padding: 0.65rem 2rem !important;
    width: 100% !important;
    text-transform: uppercase;
    transition: all 0.2s;
}}
.stButton > button:hover {{
    background: linear-gradient(135deg, #0055c8, #0090b0) !important;
    box-shadow: 0 0 24px rgba(0,112,243,0.45) !important;
}}
.result-safe {{
    background: {'linear-gradient(135deg,#0a2e1e,#0d3d28)' if dark else 'linear-gradient(135deg,#e8faf4,#d0f5e8)'};
    border: 1.5px solid #00c896;
    border-radius: 14px;
    padding: 1.6rem 2rem;
    text-align: center;
    box-shadow: 0 0 30px rgba(0,200,150,0.18);
}}
.result-suspicious {{
    background: {'linear-gradient(135deg,#1e1a0a,#2e2508)' if dark else 'linear-gradient(135deg,#fdf8e8,#faf0cc)'};
    border: 1.5px solid #f0a500;
    border-radius: 14px;
    padding: 1.6rem 2rem;
    text-align: center;
    box-shadow: 0 0 30px rgba(240,165,0,0.2);
}}
.result-phish {{
    background: {'linear-gradient(135deg,#2e0a0a,#3d0d0d)' if dark else 'linear-gradient(135deg,#fdf0f0,#fad8d8)'};
    border: 1.5px solid #ff4444;
    border-radius: 14px;
    padding: 1.6rem 2rem;
    text-align: center;
    animation: pulse-red 2s infinite;
}}
@keyframes pulse-red {{
    0%, 100% {{ box-shadow: 0 0 30px rgba(255,68,68,0.22); }}
    50%       {{ box-shadow: 0 0 55px rgba(255,68,68,0.45); }}
}}
.result-label {{
    font-family: 'Exo 2', sans-serif;
    font-weight: 900;
    font-size: 2rem;
    letter-spacing: 2px;
}}
.confidence-bar-bg {{
    background: {'#0a1525' if dark else '#dde8f5'};
    border-radius: 8px;
    height: 10px;
    margin-top: 0.8rem;
    overflow: hidden;
    border: 1px solid {BORDER};
}}
.feat-chip {{
    background: {BG3};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 0.55rem 0.7rem;
    font-size: 0.72rem;
    font-family: 'Share Tech Mono', monospace;
    color: {'#5a9fd4' if dark else '#3a6ab0'};
    margin-bottom: 0.4rem;
    display: flex;
    justify-content: space-between;
}}
.feat-val  {{ color: {'#00f5d4' if dark else '#0066cc'}; font-weight: bold; }}
.feat-warn {{ color: #ff5555; font-weight: bold; }}
.section-title {{
    font-family: 'Exo 2', sans-serif;
    font-weight: 600;
    font-size: 0.78rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: {SECTION_CLR};
    margin-bottom: 0.8rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid {BORDER};
}}
.risk-label {{ font-family: 'Share Tech Mono', monospace; font-size: 0.8rem; color: {'#3a6a9a' if dark else '#6a90cc'}; margin-top: 0.3rem; }}
.info-box {{
    background: {'#060f1c' if dark else '#eaf0fb'};
    border-left: 3px solid {INFO_BORDER};
    border-radius: 0 8px 8px 0;
    padding: 0.9rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.85rem;
    color: {'#7a9fc0' if dark else '#4a6a9a'};
}}
.theme-toggle {{
    display: flex;
    justify-content: flex-end;
    margin-bottom: 0.5rem;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
TRUSTED_DOMAINS = {
    "google.com","youtube.com","facebook.com","amazon.com","wikipedia.org",
    "twitter.com","x.com","instagram.com","linkedin.com","github.com",
    "microsoft.com","apple.com","paypal.com","netflix.com","reddit.com",
    "stackoverflow.com","whatsapp.com","telegram.org","tiktok.com",
    "yahoo.com","bing.com","outlook.com","gmail.com","live.com",
    "office.com","dropbox.com","spotify.com","ebay.com","aliexpress.com",
}
SUSPICIOUS_TLDS = {".xyz",".top",".club",".online",".site",".info",".tk",".ml",".ga",".cf",".gq",".pw",".cc",".su",".click"}
SHORTENERS      = {"bit.ly","tinyurl.com","t.co","goo.gl","ow.ly","is.gd","buff.ly","adf.ly","cutt.ly","rb.gy","short.link","tiny.cc"}
PHISH_KEYWORDS  = ["login","signin","account","update","verify","secure","banking","paypal","ebay","amazon","apple","microsoft","google","confirm","password","credential","suspended","urgent","alert","unusual","recover","unlock","limited","access","support","helpdesk","checkout","billing","invoice","refund","winner","prize","free"]
BRANDS          = ["paypal","amazon","apple","google","facebook","microsoft","netflix","ebay","instagram","whatsapp","wellsfargo","bankofamerica","chase","citibank","hsbc","barclays"]
FLAG_COLORS     = {"critical":"#ff4444","high":"#ff8c42","medium":"#f0c040","low":"#7aafdf"}
FLAG_ICONS      = {"critical":"🔴","high":"🟠","medium":"🟡","low":"🔵"}


# ─────────────────────────────────────────────
# FEATURE EXTRACTION
# ─────────────────────────────────────────────
def get_root_domain(hostname):
    parts = hostname.lower().replace("www.", "").split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else hostname.lower()

def extract_features(url):
    full   = url.strip()
    parsed = urlparse(full if "://" in full else "http://" + full)
    host   = (parsed.netloc or parsed.path.split("/")[0]).lower().split(":")[0]
    path   = parsed.path

    f = {}
    f["length_url"]          = len(full)
    f["length_hostname"]     = len(host)
    f["https_token"]         = 1 if parsed.scheme == "https" else 0
    f["ip"]                  = 1 if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host) else 0
    f["nb_dots"]             = full.count(".")
    f["nb_hyphens"]          = full.count("-")
    f["hostname_hyphens"]    = host.count("-")
    f["nb_at"]               = full.count("@")
    f["nb_qm"]               = full.count("?")
    f["nb_percent"]          = full.count("%")
    f["nb_slash"]            = full.count("/")
    parts = host.replace("www.", "").split(".")
    f["subdomain_depth"]     = max(0, len(parts) - 2)
    f["ratio_digits_url"]    = sum(c.isdigit() for c in full) / max(len(full), 1)
    f["ratio_digits_host"]   = sum(c.isdigit() for c in host) / max(len(host), 1)
    f["is_shortener"]        = 1 if any(s in host for s in SHORTENERS) else 0
    f["punycode"]            = 1 if "xn--" in host else 0
    f["port"]                = 1 if re.search(r":\d{2,5}$", parsed.netloc or "") else 0
    tld = "." + host.split(".")[-1] if "." in host else ""
    f["suspicious_tld"]      = 1 if tld in SUSPICIOUS_TLDS else 0
    f["double_slash"]        = 1 if "//" in path else 0
    sus_ext = [".exe",".zip",".rar",".bat",".sh",".vbs"]
    f["sus_extension"]       = 1 if any(path.lower().endswith(e) for e in sus_ext) else 0
    f["kw_in_url"]           = sum(kw in full.lower()  for kw in PHISH_KEYWORDS)
    f["kw_in_host"]          = sum(kw in host.lower()  for kw in PHISH_KEYWORDS)
    root = get_root_domain(host)
    f["trusted_domain"]      = 1 if root in TRUSTED_DOMAINS else 0
    f["brand_impersonation"] = 1 if (any(b in host for b in BRANDS) and root not in TRUSTED_DOMAINS) else 0
    return f

def compute_risk(feats):
    score = 0.0
    flags = []
    contributions = {}   # for visualization

    def add(s, sev, msg, key):
        nonlocal score
        score += s
        flags.append((sev, msg))
        contributions[key] = round(s * 100)

    if feats["ip"]:                   add(0.40,"critical","IP address used instead of domain name","IP Address")
    if feats["brand_impersonation"]:  add(0.45,"critical","Brand name in hostname — NOT the real domain","Brand Impersonation")
    if feats["punycode"]:             add(0.40,"critical","Punycode homograph — mimics real brand visually","Punycode/IDN")
    if feats["nb_at"] > 0:            add(0.30,"critical","'@' redirects browser past visible hostname","@ Symbol")
    if feats["is_shortener"]:         add(0.25,"high",   "URL shortener hides real destination","URL Shortener")
    if feats["kw_in_host"] >= 2:      add(0.30,"high",   f"{feats['kw_in_host']} phishing keywords in hostname","KW in Hostname")
    elif feats["kw_in_host"] == 1:    add(0.18,"high",   "Phishing keyword found in hostname","KW in Hostname")
    if feats["subdomain_depth"] >= 3: add(0.22,"high",   f"Deep subdomain nesting ({feats['subdomain_depth']} levels)","Subdomain Depth")
    elif feats["subdomain_depth"]==2: add(0.10,"medium", "Multiple subdomain levels","Subdomain Depth")
    if feats["suspicious_tld"]:       add(0.20,"high",   "Suspicious free/abused TLD","Suspicious TLD")
    if feats["hostname_hyphens"] >= 3:add(0.18,"high",   f"{feats['hostname_hyphens']} hyphens in hostname","Hostname Hyphens")
    elif feats["hostname_hyphens"]>=1:add(0.07,"low",    f"{feats['hostname_hyphens']} hyphen(s) in hostname","Hostname Hyphens")
    if feats["sus_extension"]:        add(0.18,"high",   "Suspicious file extension in path","Suspicious Ext")
    if not feats["https_token"]:      add(0.12,"medium", "No HTTPS — unencrypted connection","No HTTPS")
    if feats["length_url"] > 100:     add(0.14,"medium", f"Very long URL ({feats['length_url']} chars)","URL Length")
    elif feats["length_url"] > 75:    add(0.07,"low",    f"Long URL ({feats['length_url']} chars)","URL Length")
    if feats["kw_in_url"] >= 3 and feats["kw_in_host"]==0:
                                      add(0.10,"medium", f"{feats['kw_in_url']} phishing keywords in path/query","KW in URL")
    if feats["nb_percent"] > 10:      add(0.10,"medium", f"Heavy URL encoding ({feats['nb_percent']} '%' chars)","URL Encoding")
    if feats["double_slash"]:         add(0.08,"medium", "Double slash — possible open redirect","Double Slash")
    if feats["port"]:                 add(0.10,"medium", "Non-standard port in URL","Custom Port")

    if feats["trusted_domain"]:
        score -= 0.40
        contributions["Trusted Domain (discount)"] = -40

    return min(max(score, 0.0), 1.0), flags, contributions

def verdict(score):
    if score < 0.20:
        return "LEGITIMATE","#00c896","✅","result-safe","This URL appears safe based on structural analysis."
    elif score < 0.50:
        return "SUSPICIOUS","#f0a500","⚠️","result-suspicious","Proceed with caution — one or more red flags detected."
    else:
        return "PHISHING","#ff4444","🚨","result-phish","High probability of phishing. Do NOT visit this URL."


# ─────────────────────────────────────────────
# PLOTLY THEME HELPER
# ─────────────────────────────────────────────
def plotly_layout(title=""):
    return dict(
        title=dict(text=title, font=dict(family="Exo 2", size=14, color=PLOTLY_TEXT)),
        paper_bgcolor=PLOTLY_BG,
        plot_bgcolor=PLOTLY_BG,
        font=dict(family="Share Tech Mono", color=PLOTLY_TEXT, size=11),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(gridcolor=PLOTLY_GRID, zerolinecolor=PLOTLY_GRID),
        yaxis=dict(gridcolor=PLOTLY_GRID, zerolinecolor=PLOTLY_GRID),
    )


# ─────────────────────────────────────────────
# VISUALIZATION BUILDERS
# ─────────────────────────────────────────────
def make_gauge(score, color, dark_mode):
    pct = score * 100
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct,
        number={"suffix": "%", "font": {"size": 32, "family": "Exo 2", "color": color}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1,
                     "tickcolor": PLOTLY_GRID, "tickfont": {"color": PLOTLY_TEXT, "size": 10}},
            "bar":  {"color": color, "thickness": 0.28},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,   20],  "color": "rgba(0,200,150,0.15)"},
                {"range": [20,  50],  "color": "rgba(240,165,0,0.15)"},
                {"range": [50,  100], "color": "rgba(255,68,68,0.15)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.85,
                "value": pct,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor=PLOTLY_BG,
        font=dict(family="Exo 2", color=PLOTLY_TEXT),
        height=220,
        margin=dict(l=20, r=20, t=20, b=0),
    )
    return fig


def make_radar(feats, dark_mode):
    categories = [
        "URL Length", "Hostname\nLength", "Special\nChars",
        "Keywords", "Subdomain\nDepth", "Trust\nScore"
    ]
    max_vals = [200, 60, 20, 10, 5, 1]
    raw_vals = [
        feats["length_url"],
        feats["length_hostname"],
        feats["nb_hyphens"] + feats["nb_at"] + feats["nb_percent"],
        feats["kw_in_url"],
        feats["subdomain_depth"],
        feats["trusted_domain"],
    ]
    norm = [min(v / m, 1.0) for v, m in zip(raw_vals, max_vals)]
    norm.append(norm[0])
    cats = categories + [categories[0]]

    fill_clr  = "rgba(0,112,243,0.25)"
    line_clr  = "#0070f3"

    fig = go.Figure(go.Scatterpolar(
        r=norm, theta=cats,
        fill="toself", fillcolor=fill_clr,
        line=dict(color=line_clr, width=2),
        marker=dict(color=line_clr, size=6),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0,1], showticklabels=False,
                            gridcolor=PLOTLY_GRID, linecolor=PLOTLY_GRID),
            angularaxis=dict(gridcolor=PLOTLY_GRID, linecolor=PLOTLY_GRID,
                             tickfont=dict(color=PLOTLY_TEXT, size=10)),
        ),
        paper_bgcolor=PLOTLY_BG,
        font=dict(family="Exo 2", color=PLOTLY_TEXT),
        height=280,
        margin=dict(l=40, r=40, t=20, b=20),
        showlegend=False,
    )
    return fig


def make_bar_contributions(contributions, dark_mode):
    if not contributions:
        return None
    items = [(k, v) for k, v in contributions.items() if v != 0]
    if not items:
        return None
    items.sort(key=lambda x: x[1], reverse=True)
    keys = [k for k, _ in items]
    vals = [v for _, v in items]
    colors = []
    for v in vals:
        if v < 0:    colors.append("#00c896")
        elif v >= 30: colors.append("#ff4444")
        elif v >= 15: colors.append("#ff8c42")
        elif v >= 8:  colors.append("#f0c040")
        else:         colors.append("#7aafdf")

    fig = go.Figure(go.Bar(
        x=vals, y=keys, orientation="h",
        marker_color=colors,
        text=[f"+{v}%" if v > 0 else f"{v}%" for v in vals],
        textposition="outside",
        textfont=dict(family="Share Tech Mono", size=10, color=PLOTLY_TEXT),
        hovertemplate="%{y}: %{x}%<extra></extra>",
    ))
    layout = plotly_layout("Risk Contribution per Signal")
    layout["height"] = max(180, len(items) * 34 + 60)
    layout["xaxis"].update(range=[min(vals)-5, max(vals)+15], showgrid=True)
    layout["yaxis"].update(showgrid=False, automargin=True)
    fig.update_layout(**layout)
    return fig


def make_url_length_benchmark(url_len, dark_mode):
    """Compare this URL length vs typical legitimate and phishing lengths."""
    categories  = ["Typical Legit", "Typical Phishing", "This URL"]
    values      = [35, 95, url_len]
    colors      = ["#00c896", "#ff4444",
                   "#00c896" if url_len < 55 else ("#f0a500" if url_len < 80 else "#ff4444")]

    fig = go.Figure(go.Bar(
        x=categories, y=values,
        marker_color=colors,
        text=[f"{v} chars" for v in values],
        textposition="outside",
        textfont=dict(family="Share Tech Mono", size=11, color=PLOTLY_TEXT),
        width=0.45,
    ))
    layout = plotly_layout("URL Length Benchmark")
    layout["yaxis"].update(title="Characters", showgrid=True)
    layout["xaxis"].update(showgrid=False)
    layout["height"] = 260
    fig.update_layout(**layout)
    return fig


def make_feature_heatmap(feats, dark_mode):
    """Mini heatmap of key binary/numeric features."""
    feat_labels = [
        "HTTPS","IP Addr","Punycode","Brand\nImpersonation","Shortener",
        "Sus TLD","KW Host","KW URL","Sub Depth","Hyphens"
    ]
    feat_vals = [
        feats["https_token"], feats["ip"], feats["punycode"],
        feats["brand_impersonation"], feats["is_shortener"],
        feats["suspicious_tld"],
        min(feats["kw_in_host"] / 3, 1.0),
        min(feats["kw_in_url"] / 5, 1.0),
        min(feats["subdomain_depth"] / 4, 1.0),
        min(feats["hostname_hyphens"] / 4, 1.0),
    ]
    # HTTPS is good when 1, rest are bad when 1
    risk_vals = [1 - feat_vals[0]] + feat_vals[1:]

    colorscale = [
        [0.0, "#00c896" if dark_mode else "#b8f0e0"],
        [0.5, "#f0c040" if dark_mode else "#ffe088"],
        [1.0, "#ff4444" if dark_mode else "#ff8888"],
    ]

    fig = go.Figure(go.Heatmap(
        z=[risk_vals],
        x=feat_labels,
        colorscale=colorscale,
        showscale=False,
        text=[[f"{v:.0%}" for v in risk_vals]],
        texttemplate="%{text}",
        textfont=dict(family="Share Tech Mono", size=10, color=PLOTLY_TEXT),
        hovertemplate="%{x}: %{z:.0%}<extra></extra>",
        zmin=0, zmax=1,
    ))
    layout = plotly_layout("Feature Risk Heatmap")
    layout["height"] = 120
    layout["yaxis"].update(showticklabels=False, showgrid=False)
    layout["xaxis"].update(showgrid=False, tickangle=-20,
                           tickfont=dict(size=9, color=PLOTLY_TEXT))
    fig.update_layout(**layout)
    return fig


# ─────────────────────────────────────────────
# TOP BAR: theme toggle
# ─────────────────────────────────────────────
toggle_col, _ = st.columns([1, 5])
with toggle_col:
    toggle_label = "☀️ Light" if dark else "🌙 Dark"
    if st.button(toggle_label, key="theme_btn"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown('<div class="hero-title">🛡️ PhishGuard AI</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Phishing URL Detection System · XGBoost Powered</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="info-box"><b>87 Features</b><br/>Extracted per URL</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="info-box"><b>XGBoost</b><br/>Tuned Classifier</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="info-box"><b>11,430</b><br/>Training Samples</div>', unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INPUT CARD
# ─────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🔍 Analyze URL</div>', unsafe_allow_html=True)
url_input = st.text_input("", placeholder="https://example.com/login?redirect=...",
                          key="url_input", label_visibility="collapsed")
analyze_btn = st.button("⚡ ANALYZE URL", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

with st.expander("💡 Try example URLs"):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**✅ Legitimate**")
        st.code("https://www.google.com")
        st.code("https://paypal.com/account")
        st.code("https://github.com/login")
    with col_b:
        st.markdown("**🚨 Phishing**")
        st.code("http://paypal-secure-login.xyz/update")
        st.code("http://192.168.1.1/bank/login")
        st.code("http://xn--pypl-0ra.com/signin")
        st.code("https://amazon-account-suspended.top/verify")

# ─────────────────────────────────────────────
# ANALYSIS
# ─────────────────────────────────────────────
if analyze_btn and url_input.strip():
    url = url_input.strip()
    with st.spinner("Extracting features & scoring…"):
        feats                   = extract_features(url)
        score, flags, contrib   = compute_risk(feats)

    label, color, icon, css_class, desc = verdict(score)
    pct = int(score * 100)

    bar_clr = {
        "result-safe":       "linear-gradient(90deg,#00c896,#00f5a0)",
        "result-suspicious": "linear-gradient(90deg,#f0a500,#ffcc00)",
        "result-phish":      "linear-gradient(90deg,#ff4444,#ff0000)",
    }[css_class]

    # ── Result banner ──
    st.markdown(f"""
    <div class="{css_class}">
        <div style="font-size:3rem">{icon}</div>
        <div class="result-label" style="color:{color}">{label}</div>
        <div style="color:{color}99;margin-top:0.4rem;font-size:0.95rem">{desc}</div>
        <div class="confidence-bar-bg">
            <div style="height:100%;width:{pct}%;background:{bar_clr};border-radius:8px;"></div>
        </div>
        <div class="risk-label">Risk Score: {pct}%</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ══════════════════════════════════════════
    # VISUALIZATION SECTION
    # ══════════════════════════════════════════
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Visual Analysis</div>', unsafe_allow_html=True)

    # Row 1: Gauge + Radar
    v_col1, v_col2 = st.columns([1, 1])
    with v_col1:
        st.markdown(f"<div style='text-align:center;font-size:0.75rem;letter-spacing:2px;color:{SECTION_CLR};margin-bottom:-0.5rem'>RISK GAUGE</div>", unsafe_allow_html=True)
        st.plotly_chart(make_gauge(score, color, dark), use_container_width=True)
    with v_col2:
        st.markdown(f"<div style='text-align:center;font-size:0.75rem;letter-spacing:2px;color:{SECTION_CLR};margin-bottom:-0.5rem'>FEATURE RADAR</div>", unsafe_allow_html=True)
        st.plotly_chart(make_radar(feats, dark), use_container_width=True)

    # Row 2: Feature Heatmap (full width)
    st.markdown(f"<div style='font-size:0.75rem;letter-spacing:2px;color:{SECTION_CLR};margin-bottom:0.2rem'>FEATURE RISK HEATMAP</div>", unsafe_allow_html=True)
    st.plotly_chart(make_feature_heatmap(feats, dark), use_container_width=True)

    # Row 3: Contributions bar + URL length benchmark
    v_col3, v_col4 = st.columns([3, 2])
    with v_col3:
        bar_fig = make_bar_contributions(contrib, dark)
        if bar_fig:
            st.plotly_chart(bar_fig, use_container_width=True)
    with v_col4:
        st.plotly_chart(make_url_length_benchmark(feats["length_url"], dark), use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Security signals ──
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⚠️ Security Signals</div>', unsafe_allow_html=True)
    if flags:
        for severity, msg in sorted(flags, key=lambda x: ["critical","high","medium","low"].index(x[0])):
            ic  = FLAG_ICONS[severity]
            clr = FLAG_COLORS[severity]
            st.markdown(
                f'<div style="padding:0.45rem 0;border-bottom:1px solid {BORDER};font-size:0.88rem;">'
                f'<span style="color:{clr}">{ic} [{severity.upper()}]</span> '
                f'<span style="color:{TEXT}">{msg}</span></div>',
                unsafe_allow_html=True
            )
    if feats["trusted_domain"]:
        st.markdown(
            f'<div style="padding:0.45rem 0;font-size:0.88rem;color:#00c896">'
            f'🟢 [TRUST BOOST] Root domain is a known-trusted site</div>',
            unsafe_allow_html=True
        )
    if not flags and not feats["trusted_domain"]:
        st.markdown('<div style="color:#2a8a5a;font-size:0.9rem">✅ No red flags detected.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Feature chips ──
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Extracted Features</div>', unsafe_allow_html=True)
    display_feats = [
        ("URL Length",          feats["length_url"],           feats["length_url"] > 75),
        ("Hostname Length",     feats["length_hostname"],      feats["length_hostname"] > 30),
        ("Uses IP",             feats["ip"],                   feats["ip"] == 1),
        ("HTTPS",               feats["https_token"],          feats["https_token"] == 0),
        ("Dots",                feats["nb_dots"],              feats["nb_dots"] > 5),
        ("Hyphens (host)",      feats["hostname_hyphens"],     feats["hostname_hyphens"] >= 3),
        ("@ Symbols",           feats["nb_at"],                feats["nb_at"] > 0),
        ("Subdomain Depth",     feats["subdomain_depth"],      feats["subdomain_depth"] >= 2),
        ("Phish KW (host)",     feats["kw_in_host"],           feats["kw_in_host"] >= 1),
        ("Phish KW (url)",      feats["kw_in_url"],            feats["kw_in_url"] >= 3),
        ("Suspicious TLD",      feats["suspicious_tld"],       feats["suspicious_tld"] == 1),
        ("Brand Impersonation", feats["brand_impersonation"],  feats["brand_impersonation"] == 1),
        ("URL Shortener",       feats["is_shortener"],         feats["is_shortener"] == 1),
        ("Punycode",            feats["punycode"],             feats["punycode"] == 1),
        ("Trusted Domain",      feats["trusted_domain"],       False),
    ]
    cols = st.columns(3)
    per  = math.ceil(len(display_feats) / 3)
    for ci, col in enumerate(cols):
        with col:
            for name, val, bad in display_feats[ci*per:(ci+1)*per]:
                vc = "feat-warn" if bad else "feat-val"
                st.markdown(
                    f'<div class="feat-chip"><span>{name}</span><span class="{vc}">{val}</span></div>',
                    unsafe_allow_html=True
                )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── URL breakdown ──
    parsed = urlparse(url if "://" in url else "http://" + url)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔗 URL Breakdown</div>', unsafe_allow_html=True)
    for k, v in [("Scheme", parsed.scheme), ("Hostname", parsed.netloc),
                 ("Path", parsed.path), ("Query", parsed.query), ("Fragment", parsed.fragment)]:
        if v:
            st.markdown(
                f'<div style="padding:0.35rem 0;border-bottom:1px solid {BORDER};font-size:0.85rem;">'
                f'<span style="color:{SECTION_CLR};font-family:Share Tech Mono,monospace;'
                f'width:90px;display:inline-block">{k}</span>'
                f'<span style="color:{INPUT_CLR};font-family:Share Tech Mono,monospace">'
                f'{v[:90]}{"…" if len(v)>90 else ""}</span></div>',
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)

elif analyze_btn:
    st.warning("Please enter a URL first.")

st.markdown(f"""
<div style="text-align:center;color:{TEXT_DIM};font-size:0.75rem;
     font-family:Share Tech Mono,monospace;padding:1.5rem 0 0.5rem;">
INFO SECURITY PROJECT · XGBoost · RobustScaler · 11,430 URLs · 87 Features
</div>
""", unsafe_allow_html=True)