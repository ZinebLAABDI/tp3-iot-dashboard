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
# Palette — creme chaleureux + bleu tech (style Stripe / Notion)
# ------------------------------------------------------------------
CREAM   = "#FAF6EE"   # fond general
CARD    = "#FFFFFF"   # cartes
BORDER  = "#E8E2D3"   # bordures fines, chaudes
INK     = "#1F2937"   # texte principal (slate fonce)
MUTED   = "#8B8578"   # texte secondaire (chaud, pas gris froid)
BLUE    = "#C6E0FF"   # accent principal
BLUE_L  = "#EFF3FE"   # fond badge/pill bleu clair
AMBER   = "#C2793D"   # 2e serie (temperature), complementaire chaud

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"], p, span, div {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background-color: {CREAM}; }}
    section[data-testid="stSidebar"] > div {{ background-color: {CARD}; border-right: 1px solid {BORDER}; }}
    .block-container {{ padding-top: 2.2rem; max-width: 1180px; }}
    footer, #MainMenu {{ visibility: hidden; }}

    .eyebrow {{
        display: inline-flex; align-items: center; gap: 6px;
        background: {BLUE_L}; color: {BLUE}; font-size: 0.75rem; font-weight: 600;
        padding: 5px 12px; border-radius: 20px; margin-bottom: 16px;
    }}
    .hero-title {{
        font-size: 2rem; font-weight: 700; color: {INK};
        margin: 0 0 8px 0; letter-spacing: -0.02em; line-height: 1.2;
    }}
    .hero-sub {{ color: {MUTED}; font-size: 0.98rem; margin-bottom: 30px; max-width: 680px; }}

    .kpi-card {{
        background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px;
        padding: 18px 20px; height: 100%;
    }}
    .kpi-icon {{
        width: 34px; height: 34px; border-radius: 9px; display: flex;
        align-items: center; justify-content: center; font-size: 16px;
        margin-bottom: 12px;
    }}
    .kpi-label {{ font-size: 12.5px; font-weight: 500; color: {MUTED}; margin-bottom: 4px; }}
    .kpi-value {{ font-size: 1.65rem; font-weight: 700; color: {INK}; letter-spacing: -0.01em; }}

    .section-title {{ font-weight: 700; font-size: 1rem; color: {INK}; margin-bottom: 2px; }}
    .section-caption {{ color: {MUTED}; font-size: 0.85rem; margin-bottom: 14px; }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 2px; background: {CARD}; border: 1px solid {BORDER};
        border-radius: 10px; padding: 4px; width: fit-content;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 7px; padding: 6px 16px; color: {MUTED}; font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        background: {BLUE_L} !important; color: {BLUE} !important; font-weight: 600 !important;
    }}

    [data-testid="stSlider"] > div > div > div > div {{ background-color: {BLUE}; }}
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
    st.markdown("**Equipe** — _(Zineb LAABDI , Ikram El Alt)_")
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
# En-tete
# ------------------------------------------------------------------
st.markdown('<div class="eyebrow">● TP3 · Internet of Things</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Temperature &amp; Humidite — Suivi capteur</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Pipeline complet : capteur simule → base de donnees → nettoyage automatique des anomalies → analyse et visualisation.</div>',
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Cartes KPI
# ------------------------------------------------------------------
def kpi_card(icon, icon_bg, icon_color, label, value):
    return f"""
    <div class="kpi-card">
        <div class="kpi-icon" style="background:{icon_bg};color:{icon_color};">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(kpi_card("◧", BLUE_L, BLUE, "Mesures", f"{len(df_filtre):,}".replace(",", " ")), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_card("◔", "#FBEEE0", AMBER, "Temperature moy.", f"{df_filtre['mesureT'].mean():.1f} °C"), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_card("◑", BLUE_L, BLUE, "Humidite moy.", f"{df_filtre['mesureH'].mean():.1f} %"), unsafe_allow_html=True)
with k4:
    st.markdown(kpi_card("✓", "#E9F5EC", "#2F9E58", "Valeurs corrigees", int(maskT.sum() + maskH.sum())), unsafe_allow_html=True)

st.write("")
st.write("")

# ------------------------------------------------------------------
# Style Matplotlib assorti (creme + bleu/amber)
# ------------------------------------------------------------------
def style_figure(fig, ax):
    fig.patch.set_facecolor(CARD)
    ax.set_facecolor(CARD)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(BORDER)
    ax.spines["bottom"].set_color(BORDER)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(MUTED)
    ax.yaxis.label.set_color(MUTED)
    ax.grid(alpha=0.5, linewidth=0.6, color=BORDER)

def section_title(text, caption=None):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="section-caption">{caption}</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Courbes", "Correlation", "Donnees", "Verification"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            section_title("Temperature dans le temps")
            fig, ax = plt.subplots(figsize=(6, 3.2))
            ax.plot(df_affichage["date_heure"], df_affichage["mesureT"], color=AMBER, linewidth=1.8)
            ax.fill_between(df_affichage["date_heure"], df_affichage["mesureT"], alpha=0.08, color=AMBER)
            ax.set_ylabel("°C")
            style_figure(fig, ax)
            plt.xticks(rotation=25); plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
    with c2:
        with st.container(border=True):
            section_title("Humidite dans le temps")
            fig, ax = plt.subplots(figsize=(6, 3.2))
            ax.plot(df_affichage["date_heure"], df_affichage["mesureH"], color=BLUE, linewidth=1.8)
            ax.fill_between(df_affichage["date_heure"], df_affichage["mesureH"], alpha=0.08, color=BLUE)
            ax.set_ylabel("%")
            style_figure(fig, ax)
            plt.xticks(rotation=25); plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

with tab2:
    with st.container(border=True):
        section_title("Humidite en fonction de la Temperature")
        x, y = df_filtre["mesureT"].values, df_filtre["mesureH"].values
        coeffs = np.polyfit(x, y, 1)
        x_ligne = np.linspace(x.min(), x.max(), 100)
        fig, ax = plt.subplots(figsize=(8, 4.6))
        ax.scatter(x, y, s=8, alpha=0.30, color=BLUE, edgecolors="none")
        ax.plot(x_ligne, coeffs[0]*x_ligne + coeffs[1], color=AMBER, linewidth=2.4)
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
        section_title("Donnees apres nettoyage")
        st.dataframe(df_filtre[["date_heure", "mesureT", "mesureH"]], use_container_width=True, height=420)

with tab4:
    with st.container(border=True):
        section_title("Preuve : la regle de correction fonctionne", "Exemple du cours : T = 32, 32, 33, 34, 20 (seuil = 4)")
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
