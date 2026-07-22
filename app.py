import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="TP3 IoT — Temperature & Humidite",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# Petit style additionnel (cartes plus jolies, titres espacés)
# ------------------------------------------------------------------
st.markdown("""
<style>
    .main > div { padding-top: 1rem; }
    [data-testid="stMetric"] {
        background-color: #1C2128;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 15px 20px;
    }
    [data-testid="stMetricLabel"] { font-size: 14px; opacity: 0.8; }
    h1, h2, h3 { font-weight: 700; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1C2128;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Barre laterale
# ------------------------------------------------------------------
with st.sidebar:
    st.image("https://em-content.zobj.net/source/apple/391/thermometer_1f321-fe0f.png", width=60)
    st.title("TP3 — IoT")
    st.markdown("**Projet :** mesure temperature & humidite avec 1 seul capteur")
    st.markdown("---")
    st.markdown("**Etudiants :** _(vos noms ici)_")
    st.markdown("**Encadrant :** Prof CHERIF Walid")
    st.markdown("---")
    st.caption("Master IGOV-TAM · Universite Mohammed V · FSR")

# ------------------------------------------------------------------
# En-tete
# ------------------------------------------------------------------
st.title("🌡️ Dashboard IoT — Temperature & Humidite")
st.caption("Pipeline complet : capteur simule → base de donnees → nettoyage → visualisation")
st.markdown("---")

# ------------------------------------------------------------------
# Chargement + nettoyage des donnees
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
# Filtre (sidebar)
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔎 Filtrer les donnees")
    date_min, date_max = df["date_heure"].min(), df["date_heure"].max()
    plage = st.slider(
        "Periode",
        min_value=date_min.to_pydatetime(),
        max_value=date_max.to_pydatetime(),
        value=(date_min.to_pydatetime(), date_max.to_pydatetime()),
        format="DD/MM HH:mm",
    )

df_filtre = df[(df["date_heure"] >= plage[0]) & (df["date_heure"] <= plage[1])]
df_affichage = df_filtre.iloc[::15, :]

# ------------------------------------------------------------------
# Indicateurs cles (KPIs)
# ------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("📊 Mesures", f"{len(df_filtre):,}".replace(",", " "))
col2.metric("🌡️ Temp. moyenne", f"{df_filtre['mesureT'].mean():.1f} °C")
col3.metric("💧 Humidite moyenne", f"{df_filtre['mesureH'].mean():.1f} %")
col4.metric("🧹 Valeurs corrigees", int(maskT.sum() + maskH.sum()))

st.markdown("")

# ------------------------------------------------------------------
# Graphiques dans des onglets (plus propre qu'empiler tout)
# ------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📈 Courbes", "🔵 Correlation", "🧾 Donnees brutes", "🧪 Test de correction"])

plt.rcParams.update({
    "figure.facecolor": "#0E1117",
    "axes.facecolor": "#0E1117",
    "axes.edgecolor": "#888888",
    "axes.labelcolor": "#FAFAFA",
    "xtick.color": "#FAFAFA",
    "ytick.color": "#FAFAFA",
    "text.color": "#FAFAFA",
    "grid.color": "#30363d",
})

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Temperature dans le temps")
        fig, ax = plt.subplots()
        ax.plot(df_affichage["date_heure"], df_affichage["mesureT"], color="#FF6B35", linewidth=1.5)
        ax.fill_between(df_affichage["date_heure"], df_affichage["mesureT"], alpha=0.1, color="#FF6B35")
        ax.set_xlabel("Temps"); ax.set_ylabel("Temperature (°C)")
        ax.grid(alpha=0.3)
        plt.xticks(rotation=30)
        st.pyplot(fig)
    with c2:
        st.subheader("Humidite dans le temps")
        fig, ax = plt.subplots()
        ax.plot(df_affichage["date_heure"], df_affichage["mesureH"], color="#2E86AB", linewidth=1.5)
        ax.fill_between(df_affichage["date_heure"], df_affichage["mesureH"], alpha=0.1, color="#2E86AB")
        ax.set_xlabel("Temps"); ax.set_ylabel("Humidite (%)")
        ax.grid(alpha=0.3)
        plt.xticks(rotation=30)
        st.pyplot(fig)

with tab2:
    st.subheader("Nuage de points : Humidite en fonction de la Temperature")
    x, y = df_filtre["mesureT"].values, df_filtre["mesureH"].values
    coeffs = np.polyfit(x, y, 1)
    x_ligne = np.linspace(x.min(), x.max(), 100)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(x, y, s=6, alpha=0.35, color="#4ECDC4")
    ax.plot(x_ligne, coeffs[0]*x_ligne + coeffs[1], color="#FF6B35", linewidth=2.5)
    ax.set_xlabel("Temperature (°C)"); ax.set_ylabel("Humidite (%)")
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    correlation = np.corrcoef(x, y)[0, 1]
    st.info(f"**Coefficient de correlation :** {correlation:.3f}  →  "
            f"{'forte relation negative' if correlation < -0.7 else 'relation moderee'} "
            f"entre temperature et humidite.")

with tab3:
    st.subheader("Donnees (apres nettoyage)")
    st.dataframe(df_filtre[["date_heure", "mesureT", "mesureH"]], use_container_width=True, height=400)

with tab4:
    st.subheader("Preuve : la regle de correction fonctionne")
    st.write("Exemple donne par le prof : T = 32, 32, 33, 34, **20** (seuil = 4)")
    exemple = pd.Series([32, 32, 33, 34, 20], dtype=float)
    valeurs_corrigees, masque_demo = detecter_et_corriger(exemple)
    demo_df = pd.DataFrame({
        "Valeur brute": exemple,
        "Anomalie ?": ["✅ Oui" if m else "" for m in masque_demo],
        "Valeur corrigee": valeurs_corrigees,
    })
    st.dataframe(demo_df, use_container_width=True)
    st.success("Le '20' aberrant est detecte et remplace automatiquement.")

st.markdown("---")
st.caption("TP3 — Internet of Things · Prof CHERIF Walid · Master IGOV-TAM · FSR")
