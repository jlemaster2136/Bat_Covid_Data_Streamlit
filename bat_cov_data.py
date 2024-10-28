import pandas as pd 
import matplotlib.pyplot as plt 
import streamlit as st
import numpy as np
import plotly.graph_objects as go


data = pd.read_csv('/workspaces/codespaces-blank/exported-table.csv')

data[['Bat genus', 'Bat Species']] = data.pop('Bat species').str.split(' ', n=1, expand=True)
data['Year'] = data.pop('Study').str[-4:]
data = data.drop(columns=['🔗'])
data = data[(data['Study type'] == 'cross-sectional')]
data = data.astype('int', errors='ignore')



genus_list = ['betacoronavirus', 'alphacoronavirus']
color_scheme = ['lightgreen', 'skyblue']



def by_virus_genus_and_filter(dataset, genus, filter):
    if genus == 'Compare':
        if filter in ['Year', 'Sample tissue']:
            dataset = dataset.groupby([filter, 'Virus genus']).sum()
        else:
            dataset = dataset[(dataset['Virus genus'].isin(genus_list))]
            total_genera = dataset['Virus genus'].nunique()
            genera_per_country = dataset.groupby(filter)['Virus genus'].nunique()
            filter_is_one_to_all = genera_per_country == total_genera
            dataset['keep'] = dataset[filter].map(filter_is_one_to_all)
            dataset = dataset[(dataset['keep'] == True)]
            dataset = dataset.drop('keep', axis=1)
            dataset = dataset.groupby([filter, 'Virus genus']).sum()
    elif genus == 'Any':
        dataset = dataset.groupby(filter).sum()
    else:
        dataset = dataset[(dataset['Virus genus']==genus.lower())]
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
        ("Alphacoronavirus", "Betacoronavirus", 'Compare', 'Any'),
        index=None,
        placeholder="Select genus",
    )

    by = st.selectbox(
        "Prevalence by:",
        ('Year', 'Country', 'Bat genus', 'Sample tissue'),
        index=None,
        placeholder="Select filter",
    )


    if st.button('Generate Chart'):
        if option == 'Compare':
            data = by_virus_genus_and_filter(data, option, by)[['Virus genus', by, 'proportion', 'prop_error', '#']]
            fig = go.Figure()
            for i in range(len(genus_list)):
                data_genus = data[(data['Virus genus']==genus_list[i])]
                print(genus_list[i])
                x = data_genus[by]
                y = data_genus['proportion']
                y_error = data_genus['prop_error']
                name = genus_list[i]
                fig.add_trace(
                    go.Bar(
                        x=x,
                        y=y,
                        error_y=dict(type='data', array=y_error, visible=True),
                        marker_color=color_scheme[i],
                        name=genus_list[i],
                        text=data_genus['#'],  # Attach `#` column data for hover
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
            fig.update_layout(
                title={
                    'text': f'Positive Coronavirus Samples by {by}',
                    'x': 0.5,  # Center the title (0 is left, 0.5 is center, 1 is right)
                    'xanchor': 'center'}, 
                xaxis_title=by, 
                yaxis_title="Proportion of positive samples", 
                )

            # Display in Streamlit
            st.plotly_chart(fig)
        else:
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
            fig.update_layout(
                title={
                    'text': f'Positive Coronavirus Samples by {by}',
                    'x': 0.5,  # Center the title (0 is left, 0.5 is center, 1 is right)
                    'xanchor': 'center'}, 
                xaxis_title=by, 
                yaxis_title="Proportion of positive samples", 
                )

            # Display in Streamlit
            st.plotly_chart(fig)
            
url = 'Cohen, L.E., Fagre, A.C., Chen, B. et al. Coronavirus sampling and surveillance in bats from 1996–2019: a systematic review and meta-analysis. Nat Microbiol 8, 1176–1186 (2023). https://doi.org/10.1038/s41564-023-01375-1'


with tab2:
    st.header("Hello!")
    st.write("I've created this simple visualization tool out my curiosity for bat disease ecology. You can start by selecting a virus genus (or compare them) and then which factor you would like to analyze. The data is taken from the 2023 metanalysis by Cohen et al., as cited in the references. Thanks for checking it out!")
with tab3:
    st.header("References")
    st.write(url)