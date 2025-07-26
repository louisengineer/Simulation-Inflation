import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Taux simulés historiques (tu pourras les automatiser via une API ensuite)
TAUX_INTERETS = {
    "Livret A": {
        2015: 0.75, 2016: 0.75, 2017: 0.75, 2018: 0.75,
        2019: 0.75, 2020: 0.5, 2021: 0.5, 2022: 2.0,
        2023: 3.0, 2024: 3.0
    },
    "LDDS": {
        # mêmes taux que Livret A pour simplifier
        2015: 0.75, 2016: 0.75, 2017: 0.75, 2018: 0.75,
        2019: 0.75, 2020: 0.5, 2021: 0.5, 2022: 2.0,
        2023: 3.0, 2024: 3.0
    },
    "Fonds monétaire": {
        2015: 0.3, 2016: 0.1, 2017: 0.1, 2018: 0.2,
        2019: 0.3, 2020: 0.2, 2021: 0.1, 2022: 1.5,
        2023: 2.0, 2024: 2.2
    },
    "Compte courant": {
        2015: 0.0, 2016: 0.0, 2017: 0.0, 2018: 0.0,
        2019: 0.0, 2020: 0.0, 2021: 0.0, 2022: 0.0,
        2023: 0.0, 2024: 0.0
    }
}

TAUX_INFLATION = {
    2015: 0.0, 2016: 0.2, 2017: 1.0, 2018: 1.8,
    2019: 1.1, 2020: 0.5, 2021: 1.6, 2022: 5.2,
    2023: 4.9, 2024: 2.4
}

# --- Interface utilisateur ---
st.title("📈 Simulateur de rendement : Livret A, LDDS, Fonds Monétaire vs Inflation")

montant_initial = st.number_input("💰 Montant initial (€)", value=1000, min_value=100)
produit = st.selectbox("🏦 Choisissez un placement", list(TAUX_INTERETS.keys()))
annees = st.slider("⏳ Durée de placement (années)", min_value=1, max_value=10, value=5)

annee_courante = 2024
annees_simulation = list(range(annee_courante - annees + 1, annee_courante + 1))

# --- Calculs ---
capital = montant_initial
capital_constant = montant_initial
historique = []

for annee in annees_simulation:
    taux_interet = TAUX_INTERETS[produit].get(annee, 0) / 100
    inflation = TAUX_INFLATION.get(annee, 0) / 100

    capital *= (1 + taux_interet)
    capital_constant *= (1 + taux_interet) / (1 + inflation)

    historique.append({
        "Année": annee,
        "Capital (€)": capital,
        "Capital constant (€)": capital_constant,
        "Inflation (%)": inflation * 100,
        "Taux placement (%)": taux_interet * 100
    })

df = pd.DataFrame(historique)

# --- Affichage des résultats ---
st.subheader("📊 Résultats")
st.write(f"**Capital final :** {capital:,.2f} €")
st.write(f"**Pouvoir d'achat (euros constants) :** {capital_constant:,.2f} €")
perte = capital - capital_constant
if perte > 0:
    st.info(f"📉 Perte de pouvoir d'achat due à l'inflation : {perte:,.2f} €")

# --- Graphiques ---
st.subheader("📈 Évolution du capital")
fig, ax = plt.subplots()
ax.plot(df["Année"], df["Capital (€)"], label="Capital nominal (€)")
ax.plot(df["Année"], df["Capital constant (€)"], label="Pouvoir d'achat (€)")
ax.set_ylabel("Montant (€)")
ax.set_xlabel("Année")
ax.legend()
st.pyplot(fig)

st.subheader("📋 Détail annuel")
st.dataframe(df.set_index("Année").style.format("{:,.2f}"))
