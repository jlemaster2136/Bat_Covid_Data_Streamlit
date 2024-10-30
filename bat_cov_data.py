import pandas as pd 
import streamlit as st
import numpy as np
import plotly.graph_objects as go


data = pd.read_csv('exported-table.csv')

#Generate Separate Columns for Genus and species
data[['Bat genus', 'Bat species']] = data.pop('Bat species').str.split(' ', n=1, expand=True)

#Generate column for study year. This allows analyses across time.
    #This assumes inevitable inaccuracies due to factors like publishing lag, but the overall trends may maintain their shape since they will likely still be in realive order accross time. 
data['Year'] = data.pop('Study').str[-4:]

#Drop the hyperlink column as we do not have significant use for it. 
data = data.drop(columns=['🔗'])

#Only keep cross-sectional studies. This allows for temporal analyses using cross-sectional 'time stamps'. 
data = data[(data['Study type'] == 'cross-sectional')]

#Convert dataframe to integer dtype and ignore errors for series that are not integer dtypes. 
data = data.astype('int', errors='ignore')


#List for analysis of coronavirus genera. Not 'not specified' is ignored for this list. 
genus_list = ['betacoronavirus', 'alphacoronavirus']


#Funtion that takes entries from Streamlit form (option, by) and manipulates dataframe to produce the requested data. 
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

    #Create proportion of positives column.
    dataset['proportion'] = dataset['+'] / dataset['#']

    #Create standard error of proportion column.
    dataset['prop_error'] = np.sqrt(dataset['proportion'] * (1 - dataset['proportion']) / dataset['#'])

    #Sort values by proportion
    dataset = dataset.sort_values('proportion', ascending=False)

    #Drop rows with low sample size (n<10). While the value of this can be debated, it is not anticipated that very small n values are reliable and reflect broader trends. 
    dataset = dataset[(dataset['#']>10)]

    #Return dataframe with positive cases, n (#), proportion of positives, and standard error. 
    return dataset[['+', '#', 'proportion', 'prop_error']].reset_index()


st.title('Bat Conoravirus Ecology Explorer')

#Create Streamlit tabs.
tab1, tab2, tab3 = st.tabs(["Data Visualization", "About", "References"])

with tab1:
    #option variable is selection of virus genus on x-axis. Alpha- and Betacoronavirus alone, Any (including 'not-specified'), and a comparision between Alpha- and Betacoronavirus are options.
    option = st.selectbox(
        "Virus genus:",
        ("Alphacoronavirus", "Betacoronavirus", 'Compare', 'Any'),
        index=None,
        placeholder="Select genus",
    )

    #by variable is the the measurement on y-axis. Options are Year, Country, Bat genus, and Sample tissue.
    by = st.selectbox(
        "Prevalence by:",
        ('Year', 'Country', 'Bat genus', 'Sample tissue'),
        index=None,
        placeholder="Select filter",
    )

    #Color list for graphs. 
    color_scheme = ['lightgreen', 'skyblue']

    #Button to generate a graph. 
    if st.button('Generate Graph'):
        #To compare the Alpha- and Betacoronavirus virus genera. 
        if option == 'Compare':
            data = by_virus_genus_and_filter(data, option, by)[['Virus genus', by, 'proportion', 'prop_error', '#']]
            fig = go.Figure()
            for i in range(len(genus_list)):
                data_genus = data[(data['Virus genus']==genus_list[i])]
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
                        text=data_genus['#'], 
                        hovertemplate=(
                            f"{by}"": %{x}<br>"      
                            "Proportion: %{y:.2f} ± %{error_y.array:.2f}<br>" 
                            "n: %{text}<br>"  # `#` column data
                            "<extra></extra>"
                        ),
                        textposition='none',
                    )
                )
            # Add titles
            fig.update_layout(
                title={
                    'text': f'Positive Coronavirus Samples by {by}',
                    'x': 0.5,  
                    'xanchor': 'center'}, 
                xaxis_title=by, 
                yaxis_title="Proportion of positive samples", 
                )

            # Display in Streamlit
            st.plotly_chart(fig, use_container_width=True)
        else:
            #If not for comparision, and just singular genus or any analysis.    
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
                        text=data['#'],  
                        hovertemplate=(
                            f"{by}"": %{x}<br>"          
                            "Proportion: %{y:.2f} ± %{error_y.array:.2f}<br>"  
                            "n: %{text}<br>"  
                            "<extra></extra>"           
                        ),
                        textposition='none',
                    )
                )
            #Add titles to graph.
            fig.update_layout(
                title={
                    'text': f'Positive Coronavirus Samples by {by}',
                    'x': 0.5,  # Center the title (0 is left, 0.5 is center, 1 is right)
                    'xanchor': 'center'}, 
                xaxis_title=by, 
                yaxis_title="Proportion of positive samples", 
                )

            #Display graph. 
            st.plotly_chart(fig, use_container_width=True)
        


with tab2:
    st.header("Hello!")
    st.write("I've created this simple visualization tool out my curiosity for bat disease ecology.\
              You can start by selecting a virus genus (or compare them) and then which factor you would like to measure.\
              Do note that this project is a preliminary, exploratory exercise rather than a rigorous examination of the data.\
             The data used is from the 2023 metanalysis by Cohen et al., as cited in the references.\
              Thanks for checking it out!")

source_1 = 'Cohen, L.E., Fagre, A.C., Chen, B. et al. Coronavirus sampling and surveillance in bats from 1996–2019: a systematic review and meta-analysis. Nat Microbiol 8, 1176–1186 (2023). https://doi.org/10.1038/s41564-023-01375-1'

with tab3:
    st.header("References")
    st.write(source_1)