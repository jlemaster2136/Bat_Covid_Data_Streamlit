import pandas as pd 
import matplotlib.pyplot as plt 
import streamlit as st
import numpy as np
import plotly.graph_objects as go


data = pd.read_csv('/workspaces/codespaces-blank/exported-table.csv')

data[['Bat Genus', 'Bat Species']] = data.pop('Bat species').str.split(' ', n=1, expand=True)
data['Year'] = data.pop('Study').str[-4:]
data = data.drop(columns=['🔗'])
data = data[(data['Study type'] == 'cross-sectional')]
data = data.astype('int', errors='ignore')
print(data)



def by_virus_genus_and_filter(dataset, genus, filter):
    genus = genus.lower()
    dataset = dataset[(dataset['Virus genus']==genus)]
    dataset = dataset.groupby(filter).sum()
    dataset['proportion'] = dataset['+'] / dataset['#']
    dataset['prop_error'] = np.sqrt(dataset['proportion'] * (1 - dataset['proportion']) / dataset['#'])
    dataset = dataset.sort_values('proportion', ascending=False)
    dataset = dataset[(dataset['#']>10)]
    return dataset[['+', '#', 'proportion', 'prop_error']].reset_index()

st.title('Coronavirus Prevalence in Bats')

tab1, tab2, tab3 = st.tabs(["Virus Genus Prevalance", "About", "References"])

with tab1:
    option = st.selectbox(
        "Virus genus:",
        ("Alphacoronavirus", "Betacoronavirus", 'Compare them!', 'All'),
        index=None,
        placeholder="Select genus",
    )

    by = st.selectbox(
        "Prevalence by:",
        ('Year', 'Country', 'Bat Genus', 'Sample Type'),
        index=None,
        placeholder="Select filter",
    )


    if st.button('Generate Chart'):
        data = by_virus_genus_and_filter(data, option, by)[[by, 'proportion', 'prop_error', '#']]
        x = data[by]
        y = data['proportion']
        y_error = data['prop_error']
        
        fig = go.Figure(
                data=go.Bar(
                    x=x,
                    y=y,
                    error_y=dict(type='data', array=y_error, visible=True),
                    marker_color='skyblue',
                    name='Bar with Error',
                    text=data['#'],  # Attach `#` column data for hover
                    hovertemplate=(
                        "Category: %{x}<br>"            # x-axis label
                        "Proportion: %{y:.2f} ± %{error_y.array:.2f}<br>"  # y-value and error
                        "n: %{text}<br>"  # `#` column data
                        "<extra></extra>"                # Hides extra trace info
                    ),
                    textposition='none',
                )
            )
        # Add titles
        fig.update_layout(title="Bar Chart with Error Bars", xaxis_title="Categories", yaxis_title="Values")

        # Display in Streamlit
        st.plotly_chart(fig)
            
url = 'Cohen, L.E., Fagre, A.C., Chen, B. et al. Coronavirus sampling and surveillance in bats from 1996–2019: a systematic review and meta-analysis. Nat Microbiol 8, 1176–1186 (2023). https://doi.org/10.1038/s41564-023-01375-1'


with tab2:
    st.header("Hello!")
    st.write("I've created this simple visualization tool out my curiosity for bat disease ecology. You can start by selecting a virus genus (or compare them) and then which factor you would like to analyze. The data is taken from the 2023 metanalysis by Cohen et al., as cited in the references. Thanks for checking it out!")
with tab3:
    st.header("References")
    st.write(url)
