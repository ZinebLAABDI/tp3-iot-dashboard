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
INK      = "#14213D"
DEEP     = "#0B1424"   # bleu nuit, fond du bandeau hero
PAPER    = "#FAF9F6"
CARD     = "#FFFFFF"
LINE     = "#E4E1D8"
COPPER   = "#E08D6D"   # temperature (plus clair, lisible sur fond fonce)
STEEL    = "#7FB3C7"   # humidite (plus clair, lisible sur fond fonce)
COPPER_D = "#C1666B"   # temperature (version sombre, sur fond clair)
STEEL_D  = "#2E5266"   # humidite (version sombre, sur fond clair)
MUTED    = "#6B7280"

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"], p, span, div {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background-color: {PAPER}; }}
    section[data-testid="stSidebar"] > div {{ background-color: {CARD}; }}
    .block-container {{ padding-top: 0rem; max-width: 1200px; }}
    footer, #MainMenu {{ visibility: hidden; }}

    /* ---------- Bandeau hero ---------- */
    .hero-band {{
        background: linear-gradient(120deg, {DEEP} 0%, {INK} 55%, {STEEL_D} 130%);
        margin: 0 -5rem 28px -5rem;
        padding: 46px 5rem 34px 5rem;
        border-radius: 0 0 28px 28px;
    }}
    .hero-eyebrow {{
        color: {STEEL}; font-size: 0.78rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 10px;
    }}
    .hero-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.5rem; font-weight: 800; color: #FFFFFF;
        margin: 0 0 8px 0; letter-spacing: -0.02em; line-height: 1.1;
    }}
    .hero-sub {{ color: #C7CEDB; font-size: 1rem; margin-bottom: 26px; max-width: 640px; }}

    /* ---------- Cartes KPI verre depoli ---------- */
    .kpi-card {{
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.14);
        backdrop-filter: blur(6px);
        border-radius: 16px;
        padding: 18px 20px;
        height: 100%;
    }}
    .kpi-label {{
        font-size: 11px; font-weight: 600; color: #A9B4C7;
        text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px;
        display: flex; align-items: center; gap: 7px;
    }}
    .kpi-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; }}
    .kpi-value {{
        font-family: 'Space Grotesk', sans-serif; font-size: 2rem;
        font-weight: 700; color: #FFFFFF; letter-spacing: -0.01em;
    }}

    /* ---------- Corps clair ---------- */
    .section-title {{
        font-family: 'Space Grotesk', sans-serif; font-weight: 600;
        font-size: 1.05rem; color: {INK}; margin-bottom: 4px;
        display: flex; align-items: center; gap: 8px;
    }}
    .section-accent {{ width: 4px; height: 18px; border-radius: 2px; display: inline-block; }}
    .section-caption {{ color: {MUTED}; font-size: 0.85rem; margin-bottom: 14px; }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {LINE}; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent; border-radius: 8px 8px 0 0;
        padding: 8px 18px; color: {MUTED}; font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{ color: {INK} !important; font-weight: 700 !important; }}
</style>
""", unsafe_allow_html=True)

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

nb_mesures = f"{len(df_filtre):,}".replace(",", " ")
temp_moy = f"{df_filtre['mesureT'].mean():.1f} °C"
hum_moy = f"{df_filtre['mesureH'].mean():.1f} %"
nb_corrigees = int(maskT.sum() + maskH.sum())

# ------------------------------------------------------------------
# Bandeau HERO (titre + KPIs en verre depoli)
# ------------------------------------------------------------------
st.markdown(f"""
<div class="hero-band">
    <div class="hero-eyebrow">TP3 · INTERNET OF THINGS</div>
    <div class="hero-title">Temperature &amp; Humidite<br>Suivi capteur en temps reel</div>
    <div class="hero-sub">Pipeline complet : capteur simule -> base de donnees -> nettoyage automatique des anomalies -> analyse et visualisation.</div>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;">
        <div class="kpi-card">
            <div class="kpi-label"><span class="kpi-dot" style="background:#FFFFFF"></span>Mesures</div>
            <div class="kpi-value">{nb_mesures}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label"><span class="kpi-dot" style="background:{COPPER}"></span>Temperature moy.</div>
            <div class="kpi-value">{temp_moy}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label"><span class="kpi-dot" style="background:{STEEL}"></span>Humidite moy.</div>
            <div class="kpi-value">{hum_moy}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label"><span class="kpi-dot" style="background:#8FD694"></span>Valeurs corrigees</div>
            <div class="kpi-value">{nb_corrigees}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Style Matplotlib force par figure
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

def section_title(text, color):
    st.markdown(
        f'<div class="section-title"><span class="section-accent" style="background:{color}"></span>{text}</div>',
        unsafe_allow_html=True,
    )

tab1, tab2, tab3, tab4 = st.tabs(["Courbes", "Correlation", "Donnees", "Verification"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            section_title("Temperature dans le temps", COPPER_D)
            fig, ax = plt.subplots(figsize=(6, 3.2))
            ax.plot(df_affichage["date_heure"], df_affichage["mesureT"], color=COPPER_D, linewidth=1.8)
            ax.fill_between(df_affichage["date_heure"], df_affichage["mesureT"], alpha=0.10, color=COPPER_D)
            ax.set_ylabel("°C")
            style_figure(fig, ax)
            plt.xticks(rotation=25); plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
    with c2:
        with st.container(border=True):
            section_title("Humidite dans le temps", STEEL_D)
            fig, ax = plt.subplots(figsize=(6, 3.2))
            ax.plot(df_affichage["date_heure"], df_affichage["mesureH"], color=STEEL_D, linewidth=1.8)
            ax.fill_between(df_affichage["date_heure"], df_affichage["mesureH"], alpha=0.10, color=STEEL_D)
            ax.set_ylabel("%")
            style_figure(fig, ax)
            plt.xticks(rotation=25); plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

with tab2:
    with st.container(border=True):
        section_title("Humidite en fonction de la Temperature", STEEL_D)
        x, y = df_filtre["mesureT"].values, df_filtre["mesureH"].values
        coeffs = np.polyfit(x, y, 1)
        x_ligne = np.linspace(x.min(), x.max(), 100)
        fig, ax = plt.subplots(figsize=(8, 4.6))
        ax.scatter(x, y, s=8, alpha=0.30, color=STEEL_D, edgecolors="none")
        ax.plot(x_ligne, coeffs[0]*x_ligne + coeffs[1], color=COPPER_D, linewidth=2.4)
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
        section_title("Donnees apres nettoyage", INK)
        st.dataframe(df_filtre[["date_heure", "mesureT", "mesureH"]], use_container_width=True, height=420)

with tab4:
    with st.container(border=True):
        section_title("Preuve : la regle de correction fonctionne", "#8FD694")
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
