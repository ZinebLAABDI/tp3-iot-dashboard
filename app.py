import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

st.set_page_config(
    page_title="TP3 IoT — Temperature & Humidite",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Palette & typographie
# ------------------------------------------------------------------
INK       = "#14213D"
PAPER     = "#FAF9F6"
CARD      = "#FFFFFF"
LINE      = "#E4E1D8"
COPPER    = "#C1666B"   # temperature
STEEL     = "#2E5266"   # humidite
MUTED     = "#6B7280"

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    h1, h2, h3, .stTabs [data-baseweb="tab"] p {{
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -0.01em;
    }}
    .main > div {{ padding-top: 1.2rem; }}

    /* En-tete */
    .hero-title {{
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.1rem;
        font-weight: 700;
        color: {INK};
        margin-bottom: 0.1rem;
    }}
    .hero-line {{
        width: 56px; height: 3px; background: {COPPER};
        border: none; margin: 10px 0 14px 0;
    }}
    .hero-sub {{ color: {MUTED}; font-size: 0.98rem; }}

    /* Cartes metriques */
    [data-testid="stMetric"] {{
        background-color: {CARD};
        border: 1px solid {LINE};
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 1px 2px rgba(20,33,61,0.04);
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 13px; color: {MUTED}; font-weight: 500;
        text-transform: uppercase; letter-spacing: 0.04em;
    }}
    [data-testid="stMetricValue"] {{ color: {INK}; }}

    /* Onglets */
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; border-bottom: 1px solid {LINE}; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        padding: 8px 18px;
        color: {MUTED};
    }}
    .stTabs [aria-selected="true"] {{ color: {INK} !important; font-weight: 600; }}

    section[data-testid="stSidebar"] {{ background-color: {CARD}; border-right: 1px solid {LINE}; }}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# En-tete
# ------------------------------------------------------------------
st.markdown('<div class="hero-title">Temperature &amp; Humidite — Suivi capteur</div>', unsafe_allow_html=True)
st.markdown('<hr class="hero-line">', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">TP3 — Internet of Things · Pipeline capteur -> base de donnees -> nettoyage -> analyse</div>', unsafe_allow_html=True)
st.write("")

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
# Indicateurs cles
# ------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Mesures", f"{len(df_filtre):,}".replace(",", " "))
col2.metric("Temperature moy.", f"{df_filtre['mesureT'].mean():.1f} °C")
col3.metric("Humidite moy.", f"{df_filtre['mesureH'].mean():.1f} %")
col4.metric("Valeurs corrigees", int(maskT.sum() + maskH.sum()))

st.write("")

# ------------------------------------------------------------------
# Style Matplotlib assorti au theme clair
# ------------------------------------------------------------------
plt.rcParams.update({
    "figure.facecolor": PAPER, "axes.facecolor": PAPER,
    "axes.edgecolor": LINE, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "grid.color": LINE, "font.family": "sans-serif",
    "axes.spines.top": False, "axes.spines.right": False,
})

tab1, tab2, tab3, tab4 = st.tabs(["Courbes", "Correlation", "Donnees", "Verification"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Temperature dans le temps**")
        fig, ax = plt.subplots(figsize=(6, 3.2))
        ax.plot(df_affichage["date_heure"], df_affichage["mesureT"], color=COPPER, linewidth=1.6)
        ax.fill_between(df_affichage["date_heure"], df_affichage["mesureT"], alpha=0.08, color=COPPER)
        ax.set_ylabel("°C"); ax.grid(alpha=0.5, linewidth=0.6)
        plt.xticks(rotation=25); plt.tight_layout()
        st.pyplot(fig)
    with c2:
        st.markdown("**Humidite dans le temps**")
        fig, ax = plt.subplots(figsize=(6, 3.2))
        ax.plot(df_affichage["date_heure"], df_affichage["mesureH"], color=STEEL, linewidth=1.6)
        ax.fill_between(df_affichage["date_heure"], df_affichage["mesureH"], alpha=0.08, color=STEEL)
        ax.set_ylabel("%"); ax.grid(alpha=0.5, linewidth=0.6)
        plt.xticks(rotation=25); plt.tight_layout()
        st.pyplot(fig)

with tab2:
    st.markdown("**Humidite en fonction de la Temperature**")
    x, y = df_filtre["mesureT"].values, df_filtre["mesureH"].values
    coeffs = np.polyfit(x, y, 1)
    x_ligne = np.linspace(x.min(), x.max(), 100)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.scatter(x, y, s=7, alpha=0.3, color=STEEL, edgecolors="none")
    ax.plot(x_ligne, coeffs[0]*x_ligne + coeffs[1], color=COPPER, linewidth=2.2)
    ax.set_xlabel("Temperature (°C)"); ax.set_ylabel("Humidite (%)")
    ax.grid(alpha=0.5, linewidth=0.6)
    plt.tight_layout()
    st.pyplot(fig)
    correlation = np.corrcoef(x, y)[0, 1]
    st.markdown(
        f"<div style='background:{CARD};border:1px solid {LINE};border-radius:12px;padding:14px 18px;color:{INK};'>"
        f"Coefficient de correlation : <b>{correlation:.3f}</b> — relation "
        f"{'negative forte' if correlation < -0.7 else 'moderee'} entre temperature et humidite.</div>",
        unsafe_allow_html=True,
    )

with tab3:
    st.markdown("**Donnees apres nettoyage**")
    st.dataframe(df_filtre[["date_heure", "mesureT", "mesureH"]], use_container_width=True, height=420)

with tab4:
    st.markdown("**Preuve : la regle de correction fonctionne**")
    st.caption("Exemple du cours : T = 32, 32, 33, 34, 20 (seuil = 4)")
    exemple = pd.Series([32, 32, 33, 34, 20], dtype=float)
    valeurs_corrigees, masque_demo = detecter_et_corriger(exemple)
    demo_df = pd.DataFrame({
        "Valeur brute": exemple,
        "Anomalie": ["Oui" if m else "—" for m in masque_demo],
        "Valeur corrigee": valeurs_corrigees,
    })
    st.dataframe(demo_df, use_container_width=True)

st.write("")
st.markdown(f"<hr style='border-color:{LINE}'>", unsafe_allow_html=True)
st.caption("TP3 — Internet of Things · Prof CHERIF Walid · Master IGOV-TAM · FSR")
