import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from data import TAUX_INTERETS, TAUX_INFLATION  # Données externes

# --- Interface utilisateur ---
st.title("📈 Simulateur de pouvoir d’achat selon le placement")

montant_initial = st.number_input("💰 Montant initial (€)", value=1000, min_value=100)
produit = st.selectbox("🏦 Choisissez un placement", list(TAUX_INTERETS.keys()))


# Exemple : liste de dates disponibles
dates_disponibles = sorted(TAUX_INTERETS["Livret A"].keys())  # Format "YYYY-MM"

# Convertir les chaînes "YYYY-MM" en objets datetime.date pour le calendrier
def to_date_object(date_str):
    return datetime.strptime(date_str, "%Y-%m").date()

dates_obj = [to_date_object(d) for d in dates_disponibles]

# Choix du mois de début et de fin via date_input
col1, col2 = st.columns(2)
with col1:
    date_debut = st.date_input("📅 Mois de départ", value=dates_obj[0], min_value=dates_obj[0], max_value=dates_obj[-1])
with col2:
    date_fin = st.date_input("📅 Mois de fin", value=dates_obj[-1], min_value=dates_obj[0], max_value=dates_obj[-1])

# Convertir en "YYYY-MM"
mois_debut = date_debut.strftime("%Y-%m")
mois_fin = date_fin.strftime("%Y-%m")

# Vérification
if mois_debut > mois_fin:
    st.error("La date de fin doit être postérieure à la date de début.")
    st.stop()

# --- Simulation ---
capital = montant_initial
capital_constant = montant_initial
historique = []

# Liste des mois entre début et fin
dates_simulation = pd.date_range(start=mois_debut, end=mois_fin, freq="MS").strftime("%Y-%m").tolist()

produits_variations_mensuelles = ["Bitcoin", "Or", "ETF S&P500 (ESE)"]

for mois in dates_simulation:
    if produit in produits_variations_mensuelles:
        variation_mensuelle = TAUX_INTERETS[produit].get(mois, 0) / 100
        inflation_mensuelle = TAUX_INFLATION.get(mois, 0) / 100 / 12 
        
        capital *= (1 + variation_mensuelle)
        capital_constant *= (1 + variation_mensuelle) / (1 + inflation_mensuelle)
        
        taux_affichage = variation_mensuelle * 100 
    else:
        taux_annuel = TAUX_INTERETS[produit].get(mois, 0) / 100
        inflation_mensuelle = TAUX_INFLATION.get(mois, 0) / 100 / 12
        
        taux_mensuel = taux_annuel / 12
        capital *= (1 + taux_mensuel)
        capital_constant *= (1 + taux_mensuel) / (1 + inflation_mensuelle)
        
        taux_affichage = taux_annuel * 100

    historique.append({
        "Date": mois,
        "Capital (€)": capital,
        "Capital constant (€)": capital_constant,
        "Inflation (%)": inflation_mensuelle * 12 * 100, 
        "Taux placement (%)": taux_affichage
    })

df = pd.DataFrame(historique)

# --- Résultats ---
st.subheader("📊 Résultats")
st.write(f"**Capital final :** {capital:,.2f} €")
st.write(f"**Pouvoir d'achat (euros constants) :** {capital_constant:,.2f} €")
perte_pouvoir_achat = capital_constant - montant_initial
if perte_pouvoir_achat < 0:
    st.info(f"📉 Perte de pouvoir d'achat : {-perte_pouvoir_achat:,.2f} €")
else:
    st.success(f"📈 Gain de pouvoir d'achat : {perte_pouvoir_achat:,.2f} €")


# --- Graphique ---
st.subheader("📈 Évolution du capital")
fig, ax = plt.subplots()
ax.plot(df["Date"], df["Capital (€)"], label="Capital nominal (€)")
ax.plot(df["Date"], df["Capital constant (€)"], label="Pouvoir d'achat (€)")
ax.set_ylabel("Montant (€)")
ax.set_xlabel("Date")
ax.set_xticks(df["Date"][::max(len(df)//12,1)])  # Évite surcharge des ticks
ax.set_xticklabels(df["Date"][::max(len(df)//12,1)], rotation=45)
ax.grid(True)
ax.legend()
st.pyplot(fig)

# --- Graphique 2 : Taux de placement vs inflation ---
if produit not in produits_variations_mensuelles:
    st.subheader("📉 Taux de placement vs Inflation")
    fig2, ax2 = plt.subplots()
    ax2.plot(df["Date"], df["Taux placement (%)"], label="Taux placement (%)", color="green")
    ax2.plot(df["Date"], df["Inflation (%)"], label="Inflation (%)", color="red")
    ax2.set_ylabel("Taux (%)")
    ax2.set_xlabel("Date")
    ax2.set_xticks(df["Date"][::max(len(df)//12,1)])
    ax2.set_xticklabels(df["Date"][::max(len(df)//12,1)], rotation=45)
    ax2.grid(True)
    ax2.legend()
    st.pyplot(fig2)
else:
    st.info("📉 Graphique Taux vs Inflation non affiché pour ce type de placement (volatilité trop élevée).")