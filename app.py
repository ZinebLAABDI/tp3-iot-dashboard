import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="TP3 IoT - Temperature & Humidite", layout="wide")
st.title("🌡️ TP3 IoT — Dashboard Temperature & Humidite")
st.caption("Projet realise avec 1 seul capteur (temperature + humidite)")

# ---- Chargement des donnees ----
@st.cache_data
def charger_donnees():
    df = pd.read_excel("mesures_iot.xlsx", sheet_name="mesures_iot_7jours")
    df.columns = [c.strip() for c in df.columns]
    df["date_heure"] = pd.to_datetime(df["date_heure"])
    return df

df = charger_donnees()

# ---- Nettoyage (regle du seuil = 4) ----
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

df["mesureT"], maskT = detecter_et_corriger(df["temperature_C"])
df["mesureH"], maskH = detecter_et_corriger(df["humidite_pct"])

# ---- KPIs ----
col1, col2, col3, col4 = st.columns(4)
col1.metric("Nombre de mesures", len(df))
col2.metric("Temp. moyenne", f"{df['mesureT'].mean():.1f} °C")
col3.metric("Humidite moyenne", f"{df['mesureH'].mean():.1f} %")
col4.metric("Valeurs corrigees", int(maskT.sum() + maskH.sum()))

# ---- Filtre par date ----
date_min, date_max = df["date_heure"].min(), df["date_heure"].max()
plage = st.slider("Filtrer par periode", min_value=date_min.to_pydatetime(),
                   max_value=date_max.to_pydatetime(),
                   value=(date_min.to_pydatetime(), date_max.to_pydatetime()))
df_filtre = df[(df["date_heure"] >= plage[0]) & (df["date_heure"] <= plage[1])]
df_affichage = df_filtre.iloc[::15, :]

# ---- Courbes ----
c1, c2 = st.columns(2)
with c1:
    st.subheader("Temperature en fonction du temps")
    fig, ax = plt.subplots()
    ax.plot(df_affichage["date_heure"], df_affichage["mesureT"], color="red")
    ax.set_xlabel("Temps"); ax.set_ylabel("Temperature (°C)")
    plt.xticks(rotation=30)
    st.pyplot(fig)

with c2:
    st.subheader("Humidite en fonction du temps")
    fig, ax = plt.subplots()
    ax.plot(df_affichage["date_heure"], df_affichage["mesureH"], color="blue")
    ax.set_xlabel("Temps"); ax.set_ylabel("Humidite (%)")
    plt.xticks(rotation=30)
    st.pyplot(fig)

# ---- Nuage de points ----
st.subheader("Nuage de points : Humidite en fonction de la Temperature")
x, y = df_filtre["mesureT"].values, df_filtre["mesureH"].values
coeffs = np.polyfit(x, y, 1)
x_ligne = np.linspace(x.min(), x.max(), 100)
fig, ax = plt.subplots()
ax.scatter(x, y, s=5, alpha=0.3, color="teal")
ax.plot(x_ligne, coeffs[0]*x_ligne + coeffs[1], color="orange", linewidth=2)
ax.set_xlabel("Temperature (°C)"); ax.set_ylabel("Humidite (%)")
st.pyplot(fig)
st.write(f"Coefficient de correlation : **{np.corrcoef(x,y)[0,1]:.3f}**")

# ---- Tableau brut ----
with st.expander("Voir les donnees brutes"):
    st.dataframe(df_filtre[["date_heure", "mesureT", "mesureH"]])
