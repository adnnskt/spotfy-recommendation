import streamlit as st
import pandas as pd
import json
import os
import glob
import plotly.express as px

# Caminho para os arquivos de recomendação
RECOMMENDATION_PATH = os.path.join("experimentation", "retornoJSON")

# Função para carregar todos os arquivos de recomendação
@st.cache_data
def load_recommendations():
    files = glob.glob(os.path.join(RECOMMENDATION_PATH, "recommendation_*.json"))
    data = []
    for file in files:
        user = os.path.basename(file).replace("recommendation_", "").replace(".json", "")
        with open(file, "r", encoding="utf-8") as f:
            tracks = json.load(f)
            for track in tracks:
                track["usuario"] = user
                data.append(track)
    return pd.DataFrame(data)

df = load_recommendations()

# Tabela dinâmica de usuários
usuarios = df["usuario"].unique()
selected_user = st.selectbox("Selecione o usuário para visualizar recomendações:", usuarios)

user_df = df[df["usuario"] == selected_user]

st.dataframe(user_df)

# Gráfico de pizza dos gêneros mais recomendados
if "genre" in user_df.columns:
    genero_counts = user_df["genre"].value_counts().reset_index()
    genero_counts.columns = ["Gênero", "Quantidade"]
    fig_pie_genero = px.pie(genero_counts, names="Gênero", values="Quantidade", title="Gêneros mais recomendados")
    st.plotly_chart(fig_pie_genero)

# Gráfico de barras da similaridade média por gênero
if "genre" in user_df.columns and "similaridade" in user_df.columns:
    sim_por_genero = user_df.groupby("genre")["similaridade"].mean().reset_index()
    sim_por_genero.columns = ["Gênero", "Similaridade Média"]
    fig_bar = px.bar(sim_por_genero, x="Gênero", y="Similaridade Média", title="Similaridade média por gênero")
    st.plotly_chart(fig_bar)

# Gráfico de pizza dos subgêneros
if "subgenre" in user_df.columns:
    subgenero_counts = user_df["subgenre"].value_counts().reset_index()
    subgenero_counts.columns = ["Subgênero", "Quantidade"]
    fig_pie_subgenero = px.pie(subgenero_counts, names="Subgênero", values="Quantidade", title="Subgêneros mais recomendados")
    st.plotly_chart(fig_pie_subgenero)

'''
Para rodar o dashboard
# /home/adn/MBA/spotfy-recommendation/.venv/bin/streamlit run experimentation/streamlit_dashboard.py
'''