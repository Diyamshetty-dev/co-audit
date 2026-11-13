import streamlit as st

ROLES = ["Reviewer", "Senior reviewer", "Audit lead"]

BRAND_MARK = (
    '<svg viewBox="0 0 48 48" class="brand-mark" xmlns="http://www.w3.org/2000/svg">'
    '<defs><linearGradient id="brandGradient" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#4C8BEB"/><stop offset="1" stop-color="#0E9F8E"/></linearGradient></defs>'
    '<rect width="48" height="48" rx="13" fill="url(#brandGradient)"/>'
    '<path d="M24 11l11 4v8c0 7-4.6 12.2-11 15-6.4-2.8-11-8-11-15v-8z" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/>'
    '<path d="M18.5 24.5l4 4 7.5-8.5" fill="none" stroke="#fff" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>'
    "</svg>"
)

ICON_PERSON = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7FB2FF" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-6 8-6s8 2 8 6"/></svg>'
)
ICON_VERIFIED = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6EE7D4" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.7 2.7L16 9.5"/></svg>'
)
ICON_LOG = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFC75F" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 12h5M10 16h5"/></svg>'
)

LANDING_CSS = """
<style>
section[data-testid="stSidebar"],
div[data-testid="stSidebarCollapsedControl"],
button[data-testid="stExpandSidebarButton"] {
    display: none !important;
}

.stApp {
    background:
        radial-gradient(1100px 620px at 10% 6%, rgba(47, 111, 208, 0.38), transparent 60%),
        radial-gradient(900px 560px at 94% 92%, rgba(14, 159, 142, 0.3), transparent 60%),
        linear-gradient(160deg, #071427 0%, #0B1F3A 55%, #10294D 100%) !important;
}

.block-container {
    padding-top: 3rem;
    max-width: 1180px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.brand-mark {
    width: 2.7rem;
    height: 2.7rem;
    filter: drop-shadow(0 8px 14px rgba(0, 0, 0, 0.45));
}

.brand-name {
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: #FFFFFF;
}

.hero-title {
    margin: 1.8rem 0 1rem 0;
    font-size: 3.2rem;
    font-weight: 800;
    line-height: 1.04;
    letter-spacing: -0.035em;
    color: #FFFFFF;
}

.hero-title span {
    background: linear-gradient(90deg, #7FB2FF, #6EE7D4);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.hero-sub {
    max-width: 34rem;
    font-size: 1.08rem;
    line-height: 1.6;
    color: #B8CBE2;
}

.hero-points {
    display: grid;
    gap: 0.95rem;
    margin-top: 1.9rem;
}

.hero-point {
    display: flex;
    align-items: flex-start;
    gap: 0.85rem;
}

.hero-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 2.4rem;
    height: 2.4rem;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.14);
}

.hero-point strong {
    display: block;
    font-size: 0.98rem;
    color: #FFFFFF;
}

.hero-point .detail {
    font-size: 0.88rem;
    color: #A9BFD8;
}

.hero-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin-top: 2rem;
}

.hero-chip {
    padding: 0.4rem 0.9rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    color: #CFE0F5;
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.16);
}

.hero-foot {
    margin-top: 2.3rem;
    font-size: 0.8rem;
    color: #7E97B5;
}

div[data-testid="stForm"] {
    padding: 1.9rem 1.9rem 1.5rem 1.9rem;
    border: none;
    border-radius: 24px;
    background: rgba(255, 255, 255, 0.98);
    box-shadow: 0 34px 80px -28px rgba(0, 0, 0, 0.7);
}

button[data-testid="stBaseButton-primaryFormSubmit"],
div.stFormSubmitButton > button[kind="primaryFormSubmit"] {
    padding: 0.65rem 1rem;
    font-weight: 700;
    color: #FFFFFF !important;
    background: linear-gradient(180deg, #4C8BEB 0%, #2F6FD0 100%) !important;
    border: 1px solid #2A63BC !important;
    border-radius: 12px;
    box-shadow: 0 14px 24px -12px rgba(47, 111, 208, 0.8);
}

button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    filter: brightness(1.07);
    transform: translateY(-1px);
}

.signin-title {
    margin: 0 0 0.25rem 0;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #0B1F3A;
}

.signin-sub {
    margin: 0 0 1rem 0;
    font-size: 0.92rem;
    color: #5B6B7E;
}
</style>
"""

HERO_HTML = (
    f'<div class="brand">{BRAND_MARK}<span class="brand-name">Co Audit</span></div>'
    '<div class="hero-title">The AI auditor that<br><span>knows when it is unsure</span></div>'
    '<p class="hero-sub">Co Audit reads real SEC 10-K filings, checks every number, and stops to ask a human '
    "whenever it is not sure. Nothing is guessed, and every decision is recorded.</p>"
    '<div class="hero-points">'
    f'<div class="hero-point"><div class="hero-icon">{ICON_PERSON}</div>'
    '<div><strong>Human in the loop</strong><span class="detail">Flagged values pause the workflow until you approve, edit or reject them.</span></div></div>'
    f'<div class="hero-point"><div class="hero-icon">{ICON_VERIFIED}</div>'
    '<div><strong>Checked against the SEC</strong><span class="detail">Every value is compared with official XBRL data and three accounting checks.</span></div></div>'
    f'<div class="hero-point"><div class="hero-icon">{ICON_LOG}</div>'
    '<div><strong>Append-only audit log</strong><span class="detail">Decisions are added as new rows and are never edited or deleted.</span></div></div>'
    "</div>"
    '<div class="hero-chips"><span class="hero-chip">8 key metrics</span>'
    '<span class="hero-chip">3 accounting checks</span><span class="hero-chip">0 silent guesses</span></div>'
    '<div class="hero-foot">MineArena 1.0 &middot; PS-01 &middot; Financial Filing Auditor Agent</div>'
)


def render_login(stretch) -> None:
    st.markdown(LANDING_CSS, unsafe_allow_html=True)
    left, right = st.columns([1.2, 1], gap="large")
    with left:
        st.markdown(HERO_HTML, unsafe_allow_html=True)
    with right:
        st.markdown('<div style="height:2.4rem"></div>', unsafe_allow_html=True)
        with st.form("sign_in_form"):
            st.markdown(
                '<p class="signin-title">Sign in to the workbench</p>'
                '<p class="signin-sub">Choose who is reviewing. This name is written to the audit log.</p>',
                unsafe_allow_html=True,
            )
            reviewer_id = st.text_input("Reviewer ID", value="auditor_1", placeholder="For example auditor_1")
            role = st.selectbox("Role", ROLES, index=0)
            submitted = st.form_submit_button("Enter workbench", type="primary", **stretch)
            st.caption("Demo sign-in. No password is collected. Switch reviewer any time for two-person approvals.")
        if submitted:
            cleaned = reviewer_id.strip()
            if not cleaned:
                st.error("Enter a reviewer ID to continue.")
            else:
                st.session_state.reviewer_id = cleaned
                st.session_state.reviewer_role = role
                st.session_state.signed_in = True
                st.rerun()
