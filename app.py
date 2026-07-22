import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="TP3 IoT — Temperature & Humidite",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Palette
# ------------------------------------------------------------------
INK    = "#14213D"
PAPER  = "#FAF9F6"
CARD   = "#FFFFFF"
LINE   = "#E4E1D8"
COPPER = "#C1666B"   # temperature
STEEL  = "#2E5266"   # humidite
MUTED  = "#6B7280"

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"], p, span, div {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background-color: {PAPER}; }}
    section[data-testid="stSidebar"] > div {{ background-color: {CARD}; }}
    .block-container {{ padding-top: 2rem; max-width: 1200px; }}

    .hero-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.3rem; font-weight: 700; color: {INK};
        margin: 0 0 6px 0; letter-spacing: -0.02em;
    }}
    .hero-line {{ width: 52px; height: 3px; background: {COPPER}; margin: 4px 0 16px 0; border-radius: 2px; }}
    .hero-sub {{ color: {MUTED}; font-size: 0.98rem; margin-bottom: 28px; }}

    .kpi-card {{
        background: {CARD}; border: 1px solid {LINE}; border-radius: 14px;
        padding: 18px 20px; box-shadow: 0 2px 8px rgba(20,33,61,0.06);
        height: 100%;
    }}
    .kpi-label {{
        font-size: 11px; font-weight: 600; color: {MUTED};
        text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px;
        display: flex; align-items: center; gap: 6px;
    }}
    .kpi-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; }}
    .kpi-value {{
        font-family: 'Space Grotesk', sans-serif; font-size: 1.9rem;
        font-weight: 700; color: {INK}; letter-spacing: -0.01em;
    }}

    .section-title {{
        font-family: 'Space Grotesk', sans-serif; font-weight: 600;
        font-size: 1.05rem; color: {INK}; margin-bottom: 4px;
    }}
    .section-caption {{ color: {MUTED}; font-size: 0.85rem; margin-bottom: 14px; }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {LINE}; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent; border-radius: 8px 8px 0 0;
        padding: 8px 18px; color: {MUTED}; font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{ color: {INK} !important; font-weight: 700 !important; }}

    footer, #MainMenu {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# En-tete
# ------------------------------------------------------------------
st.markdown('<div class="hero-title">Temperature &amp; Humidite — Suivi capteur</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-line"></div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">TP3 — Internet of Things · Pipeline capteur → base de donnees → nettoyage → analyse</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# Chargement + nettoyage
# ------------------------------------------------------------------
@st.cache_data
def charger_donnees():
    df = pd.read_excel("mesures_iot.xlsx", sheet_name="mesures_iot_7jours")
    df.columns = [c.strip() for c in df.columns]
    df["date_heure"] = pd.to_datetime(df["date_heure"])
    return df

def detecter_et_corriger(serie, seuil=4):
    valeurs = serie.copy().astype(float)
    masque = pd.Series(False, index=serie.index)
    derniere_valide = valeurs.iloc[0]
    for i in range(1, len(valeurs)):
        v = valeurs.iloc[i]
        if abs(derniere_valide - v) > seuil:
            masque.iloc[i] = True
            valeurs.iloc[i] = np.nan
        else:
            derniere_valide = v
    return valeurs.interpolate().bfill().ffill(), masque

df = charger_donnees()
df["mesureT"], maskT = detecter_et_corriger(df["temperature_C"])
df["mesureH"], maskH = detecter_et_corriger(df["humidite_pct"])

# ------------------------------------------------------------------
# Barre laterale
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("#### Projet")
    st.caption("Master IGOV-TAM · Universite Mohammed V · FSR")
    st.markdown("**Encadrant** — Prof CHERIF Walid")
    st.markdown("**Equipe** — _(vos noms ici)_")
    st.markdown("---")
    st.markdown("#### Periode")
    date_min, date_max = df["date_heure"].min(), df["date_heure"].max()
    plage = st.slider(
        " ", min_value=date_min.to_pydatetime(), max_value=date_max.to_pydatetime(),
        value=(date_min.to_pydatetime(), date_max.to_pydatetime()), format="DD/MM HH:mm",
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("Seuil de correction des anomalies : **4**")

df_filtre = df[(df["date_heure"] >= plage[0]) & (df["date_heure"] <= plage[1])]
df_affichage = df_filtre.iloc[::15, :]

# ------------------------------------------------------------------
# Cartes KPI (HTML pur, fiable quelle que soit la version Streamlit)
# ------------------------------------------------------------------
def kpi_card(label, value, color):
    return f"""
    <div class="kpi-card">
        <div class="kpi-label"><span class="kpi-dot" style="background:{color}"></span>{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(kpi_card("Mesures", f"{len(df_filtre):,}".replace(",", " "), INK), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_card("Temperature moy.", f"{df_filtre['mesureT'].mean():.1f} °C", COPPER), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_card("Humidite moy.", f"{df_filtre['mesureH'].mean():.1f} %", STEEL), unsafe_allow_html=True)
with k4:
    st.markdown(kpi_card("Valeurs corrigees", int(maskT.sum() + maskH.sum()), MUTED), unsafe_allow_html=True)

st.write("")
st.write("")

# ------------------------------------------------------------------
# Style Matplotlib force par figure (pas seulement rcParams globaux)
# ------------------------------------------------------------------
def style_figure(fig, ax):
    fig.patch.set_facecolor(CARD)
    ax.set_facecolor(CARD)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(LINE)
    ax.spines["bottom"].set_color(LINE)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    ax.grid(alpha=0.4, linewidth=0.6, color=LINE)

tab1, tab2, tab3, tab4 = st.tabs(["Courbes", "Correlation", "Donnees", "Verification"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown('<div class="section-title">Temperature dans le temps</div>', unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(6, 3.2))
            ax.plot(df_affichage["date_heure"], df_affichage["mesureT"], color=COPPER, linewidth=1.8)
            ax.fill_between(df_affichage["date_heure"], df_affichage["mesureT"], alpha=0.10, color=COPPER)
            ax.set_ylabel("°C")
            style_figure(fig, ax)
            plt.xticks(rotation=25); plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
    with c2:
        with st.container(border=True):
            st.markdown('<div class="section-title">Humidite dans le temps</div>', unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(6, 3.2))
            ax.plot(df_affichage["date_heure"], df_affichage["mesureH"], color=STEEL, linewidth=1.8)
            ax.fill_between(df_affichage["date_heure"], df_affichage["mesureH"], alpha=0.10, color=STEEL)
            ax.set_ylabel("%")
            style_figure(fig, ax)
            plt.xticks(rotation=25); plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

with tab2:
    with st.container(border=True):
        st.markdown('<div class="section-title">Humidite en fonction de la Temperature</div>', unsafe_allow_html=True)
        x, y = df_filtre["mesureT"].values, df_filtre["mesureH"].values
        coeffs = np.polyfit(x, y, 1)
        x_ligne = np.linspace(x.min(), x.max(), 100)
        fig, ax = plt.subplots(figsize=(8, 4.6))
        ax.scatter(x, y, s=8, alpha=0.30, color=STEEL, edgecolors="none")
        ax.plot(x_ligne, coeffs[0]*x_ligne + coeffs[1], color=COPPER, linewidth=2.4)
        ax.set_xlabel("Temperature (°C)"); ax.set_ylabel("Humidite (%)")
        style_figure(fig, ax)
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        correlation = np.corrcoef(x, y)[0, 1]
        st.markdown(
            f'<div class="section-caption">Coefficient de correlation : <b style="color:{INK}">{correlation:.3f}</b> — '
            f'relation {"negative forte" if correlation < -0.7 else "moderee"} entre temperature et humidite.</div>',
            unsafe_allow_html=True,
        )

with tab3:
    with st.container(border=True):
        st.markdown('<div class="section-title">Donnees apres nettoyage</div>', unsafe_allow_html=True)
        st.dataframe(df_filtre[["date_heure", "mesureT", "mesureH"]], use_container_width=True, height=420)

with tab4:
    with st.container(border=True):
        st.markdown('<div class="section-title">Preuve : la regle de correction fonctionne</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-caption">Exemple du cours : T = 32, 32, 33, 34, 20 (seuil = 4)</div>', unsafe_allow_html=True)
        exemple = pd.Series([32, 32, 33, 34, 20], dtype=float)
        valeurs_corrigees, masque_demo = detecter_et_corriger(exemple)
        demo_df = pd.DataFrame({
            "Valeur brute": exemple,
            "Anomalie": ["Oui" if m else "—" for m in masque_demo],
            "Valeur corrigee": valeurs_corrigees,
        })
        st.dataframe(demo_df, use_container_width=True)

st.write("")
st.markdown(f'<div style="text-align:center;color:{MUTED};font-size:0.82rem;padding:10px 0;">TP3 — Internet of Things · Prof CHERIF Walid · Master IGOV-TAM · FSR</div>', unsafe_allow_html=True)
