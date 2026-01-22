import streamlit as st
import pandas as pd
import json
import os
import glob
import plotly.express as px

RECOMMENDATION_PATH = os.path.join("experimentation", "retornoJSON")
ENRICHED_PATH = os.path.join(RECOMMENDATION_PATH, "df_tracks_enriched.json")

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

@st.cache_data
def load_enriched():
    with open(ENRICHED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.DataFrame(data)

df = load_recommendations()
df_enriched = load_enriched()

st.set_page_config(page_title="Spotify Dashboard", layout="wide")

# Customização do tema das abas para verde Spotify
st.markdown(
    """
    <style>
    /* Cor da aba selecionada */
    .stTabs [data-baseweb="tab"]:not([aria-selected="true"]) {
        color: #1DB954;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #1DB95411;
        color: #ffffff;
        border-bottom: 3px solid #1DB954;
    }
    </style>
    """,
    unsafe_allow_html=True
)
tabs = st.tabs(["Recomendações", "Base de músicas global"])

with tabs[0]:
    st.header("Recomendações por Usuário")
    usuarios = df["usuario"].unique()
    selected_user = st.selectbox("Selecione o usuário para visualizar recomendações:", usuarios)
    user_df = df[df["usuario"] == selected_user]
    st.dataframe(user_df)
    if "genre" in user_df.columns:
        genero_counts = user_df["genre"].value_counts().reset_index()
        genero_counts.columns = ["Gênero", "Quantidade"]
        fig_pie_genero = px.pie(genero_counts, names="Gênero", values="Quantidade", title="Gêneros mais recomendados")
        st.plotly_chart(fig_pie_genero)
    if "genre" in user_df.columns and "similaridade" in user_df.columns:
        sim_por_genero = user_df.groupby("genre")["similaridade"].mean().reset_index()
        sim_por_genero.columns = ["Gênero", "Similaridade Média"]
        fig_bar = px.bar(sim_por_genero, x="Gênero", y="Similaridade Média", title="Similaridade média por gênero", color_discrete_sequence=["#1DB954"])
        st.plotly_chart(fig_bar)
    if "subgenre" in user_df.columns:
        subgenero_counts = user_df["subgenre"].value_counts().reset_index()
        subgenero_counts.columns = ["Subgênero", "Quantidade"]
        fig_pie_subgenero = px.pie(subgenero_counts, names="Subgênero", values="Quantidade", title="Subgêneros mais recomendados")
        st.plotly_chart(fig_pie_subgenero)

with tabs[1]:
    st.header("Detalhes das músicas global")
    playlists = ["Todos"] + sorted(df_enriched["playlist"].dropna().unique())
    selected_playlist = st.selectbox("Filtrar por playlist:", playlists)
    if selected_playlist == "Todos":
        filtered_df = df_enriched
    else:
        filtered_df = df_enriched[df_enriched["playlist"] == selected_playlist]
    st.dataframe(filtered_df)
    # Gráficos de treemap com percentual no hover
    if "genre" in filtered_df.columns:
        genero_counts = filtered_df["genre"].value_counts(normalize=False).reset_index()
        genero_counts.columns = ["Gênero", "Quantidade"]
        total = genero_counts["Quantidade"].sum()
        genero_counts["Percentual"] = genero_counts["Quantidade"] / total * 100
        fig_treemap_genero = px.treemap(
            genero_counts,
            path=["Gênero"],
            values="Quantidade",
            title="Gêneros no Enriquecido",
            custom_data=["Percentual"]
        )
        fig_treemap_genero.update_traces(
            hovertemplate='<b>%{label}</b><br>Percentual: %{customdata[0]:.2f}%<extra></extra>'
        )
        st.plotly_chart(fig_treemap_genero)
    if "subgenre" in filtered_df.columns:
        subgenero_counts = filtered_df["subgenre"].value_counts(normalize=False).reset_index()
        subgenero_counts.columns = ["Subgênero", "Quantidade"]
        total = subgenero_counts["Quantidade"].sum()
        subgenero_counts["Percentual"] = subgenero_counts["Quantidade"] / total * 100
        fig_treemap_subgenero = px.treemap(
            subgenero_counts,
            path=["Subgênero"],
            values="Quantidade",
            title="Subgêneros no Enriquecido",
            custom_data=["Percentual"]
        )
        fig_treemap_subgenero.update_traces(
            hovertemplate='<b>%{label}</b><br>Percentual: %{customdata[0]:.2f}%<extra></extra>'
        )
        st.plotly_chart(fig_treemap_subgenero)
    # Gráficos de barras (histograma)
    col1, col2, col3 = st.columns(3)
    with col1:
        if "popularity" in filtered_df.columns:
            fig_pop = px.histogram(filtered_df, x="popularity", nbins=20, title="Distribuição de Popularidade", labels={"popularity": "Popularidade"}, color_discrete_sequence=["#1DB954"])
            st.plotly_chart(fig_pop, use_container_width=True)
    with col2:
        if "danceability" in filtered_df.columns:
            fig_dance = px.histogram(filtered_df, x="danceability", nbins=20, title="Distribuição de Danceability", labels={"danceability": "Danceability"}, color_discrete_sequence=["#1DB954"])
            st.plotly_chart(fig_dance, use_container_width=True)
    with col3:
        if "energy" in filtered_df.columns:
            fig_energy = px.histogram(filtered_df, x="energy", nbins=20, title="Distribuição de Energy", labels={"energy": "Energy"}, color_discrete_sequence=["#1DB954"])
            st.plotly_chart(fig_energy, use_container_width=True)

 #/home/adn/MBA/spotfy-recommendation/.venv/bin/streamlit run experimentation/streamlit_dashboard.py