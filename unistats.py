# from pydoc_data.topics import topics
# from turtle import width
# from types import CellType
from inspect import stack
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from PIL import Image
from st_aggrid import AgGrid,GridOptionsBuilder

st.set_page_config(layout="wide")

image = Image.open("logo2.png")
st.image(image)
st.title("ONLINE DEMAND ANALYSIS")


#### LOAD DATA ###

data_fr = pd.read_csv("data_fr.csv")
data_fr['Feb 2022'] = data_fr['Feb 2022'].fillna(0).astype(int, errors='ignore')
data_fr['Volume'] = data_fr['Volume'].fillna(0).astype(int, errors='ignore')
data_fr = data_fr.sort_values(by = 'Feb 2022', ascending= False)

data_us = pd.read_csv("data_us.csv")
data_us['Feb 2022'] = data_us['Feb 2022'].fillna(0).astype(int, errors='ignore')
data_us['Volume'] = data_us['Volume'].fillna(0).astype(int, errors='ignore')
data_us = data_us.sort_values(by = 'Feb 2022', ascending= False)

bubbles_fr = pd.read_csv("bubbles.csv")
bubbles_fr = bubbles_fr[bubbles_fr['Country']=='France']
bubbles_us = pd.read_csv("bubbles.csv")
bubbles_us = bubbles_us[bubbles_us['Country']=='United States']

demand_us = pd.read_csv("demandus.csv")
demand_fr = pd.read_csv("demandfr.csv")

#### SIDEBAR ###

with st.sidebar:

    country = st.radio(
        label = 'Countries',
        options = ("United States","France"

        )
    )

    if country == "France":
        data = data_fr
        bubbles = bubbles_fr
        size_factor = 2
    if country == "United States":
        data = data_us
        bubbles = bubbles_us
        size_factor = 5

    lvl = st.radio(
        label = 'Level of analysis',
        options = (
        "Topics",
        "Subtopics"
        )
    )

    if lvl == "Topics":
        data['subintention'] = data['Topics']
    elif lvl == "Subtopics":
        data['subintention'] = data['Subtopics']

    intentions_options = st.multiselect(
        'Intentions',
        data.Intentions.unique(),
        ['brands'],
        key='1'
        )
    if len(intentions_options) == 0:
        subintention_options = data.Topics.unique()


    subintention_options = st.multiselect(
        'Topics',
        data[data.Intentions.isin(intentions_options)].subintention.unique(),
        data[data.Intentions.isin(intentions_options)].subintention.unique()[:5],
        key='2'
        )
    if len(subintention_options) == 0:
        subintention_options = data[data.Intentions.isin(intentions_options)].subintention.unique()

    height = st.slider('Chart size', 500, 2000, 500)


col1, col2 = st.columns(2)

# Intentions

level0 = pd.DataFrame(data.groupby(['Intentions']).sum()['Feb 2022']).sort_values(by=['Feb 2022'], ascending = True).reset_index()
fig = go.Figure(go.Bar(
    y=level0["Intentions"],
    x=level0["Feb 2022"],
    marker_color='#feb82b',
    marker_line_color='rgba(0, 0, 0, 0)',
    orientation='h'))
fig.update_layout(
    height=500,
    title='Demand for top categories in Jan 2022',
    plot_bgcolor="#0c0c0e",
    )

with col1:
    st.header("Intentions")
    st.plotly_chart(fig)

data = data[data.Intentions.isin(intentions_options)]

# Topics

level1 = pd.DataFrame(data.groupby(['subintention']).sum()['Feb 2022']).sort_values(by=['Feb 2022'], ascending = True).reset_index()
fig = go.Figure(go.Bar(
    y=level1["subintention"],
    x=level1["Feb 2022"],
    marker_color='#feb82b',
    marker_line_color='rgba(0, 0, 0, 0)',
    orientation='h'))
fig.update_layout(
    height=height,
    title='Demand for top categories in Jan 2022',
    plot_bgcolor="#0c0c0e",
    )

with col2:
    st.header("Topics")
    st.plotly_chart(fig)


# Full table
st.header("Full table")
agdata = data
builder = GridOptionsBuilder.from_dataframe(agdata)
builder.configure_column("Keyword", editable=True)
grid_opt = builder.build()
AgGrid(data[data.subintention.isin(subintention_options)], theme='dark', gridOptions=grid_opt)

# Evolutions
st.header("Evolutions")
#topic_options = st.multiselect('Topics',data.Topics.unique(),['planets','telescopes','high-end brands'],key='2')
evol = data.groupby('subintention').sum()
evol = evol.loc[:,'Mar 2018':'Feb 2022'].transpose().reset_index()
change = ((evol.loc[evol['index'].str.contains('2021'),subintention_options].sum()/evol.loc[evol['index'].str.contains('2020'),subintention_options].sum()-1))
change =pd.DataFrame(change)
change.columns = ['change']
change.style.format({'change': '{:.2f}%'.format})
val2021 = evol.loc[evol['index'].str.contains('2021'),subintention_options].sum().astype(int)
st.write('Queries per year and change since last year')
i=0
for col in st.columns(len(subintention_options)):
    #col.metric(label=change.index[i], value=val2021.values[i], delta=change.change[i])
    col.metric(label=change.index[i], value=f'{val2021.values[i]:,}', delta=f'{change.change[i]:.1%}')
    i+=1

fig = px.line(
    evol,
    x="index",
    y=subintention_options,
    color_discrete_sequence=px.colors.qualitative.Dark24,
    )
    #hover_data={"date": "|%B %d, %Y"},
    #title='custom tick labels'
    # )
fig.add_vline(x='Jan 2019', line_width=1, line_dash="dot", line_color="white")
fig.add_vline(x='Jan 2020', line_width=1, line_dash="dot", line_color="white")
fig.add_vline(x='Jan 2021', line_width=1, line_dash="dot", line_color="white")
fig.add_vline(x='Jan 2022', line_width=1, line_dash="dot", line_color="white")
fig.update_layout(xaxis=dict(showgrid=False),#True,gridcolor='red'),
              yaxis=dict(showgrid=False),
              plot_bgcolor="#0c0c0e",
              width=1000,
              height=500,
)
st.plotly_chart(fig)

# Bubble chart
st.header("Prioritization matrix")
st.write('Bubble size = Potential sales per month for Unistellar')
bubbles['Labels'] = bubbles['Topic'] + ' | Est. sales: ' + bubbles['Sales per year'].astype(int).astype(str)
fig = go.Figure(data=[go.Scatter(
    x=bubbles['Queries per month'],
    y=bubbles['Conversion rate'],
    mode='markers',
    marker=dict(
        color=bubbles['Sales per year']/10,
        size=bubbles['Sales per year']/size_factor,
    ),
    text=bubbles['Labels'],

)])
fig.update_layout(
    height=750,
    width=1000,
    plot_bgcolor="#0c0c0e",
    xaxis=dict(title='Number of queries per month'),
    yaxis=dict(title='Conversion rate'),
    )
st.plotly_chart(fig)

bubbles[['Topic','Queries per month','CTR','Conversion rate','Sales per year','Definition']]

#### DASHBOARD ###

st.header("Top websites per group")

site_types = {
    'out of scope':[['imdb','allocine','starcitygames',
                    'sezane','gala','dragonforms','gerbeaud','jardiner-malin','siriusxm','siriuscom','eclipse','nebuleusebijoux','telescop','latelescop','etoiltour','etoiltours','etoilverif',
                    'venus','mercurymarine','pluto','issworld','meteor','bluemoonbrewingcompany','observatoryoc',
                    'wiktionary','merriam-webster','larousse','lerobert','cnrtl','dicocitations',
                    'timeanddate','almanac','farmersalmanac','calendarr','moongiant','calendrier-365','calendrier-lunaire','ephemeride','ephemeride-jour','very-utile','nouvellelune','calagenda','lalanguefrancaise','synonymo',
                    'google',
                    ],'#333333'],
    'Generalist & Social Media':[['wikipedia','britannica','vikidia','universalis','harvard','stanford',
                        'reddit','twitter','instagram','facebook','linkedin','youtube','curiositystream','tripadvisor',
                        'cnn','nytimes','npr','insidehook','usnews','livenation','outdoorproject',
                        'francetvinfo','ouest-france','lemonde','linternaute','numerama','01net','bfmtv','lepoint','20minutes','familiscope','lesechos',
                        ],'#767782'],
    'Specialised Media':[['futura-sciences','universcience','techno-science','sciencesetavenir','presse-citron',
                        't3','digitalcameraworld','arstechnica','petapixel','on-mag',
                        'destination-orbite','astrofiles','webastro','astrosurf','le-systeme-solaire','constellation-guide',
                        'scientificamerican','sciencenewsforstudents','nationalgeographic','constellation','astronomy','skyandtelescope','magazineheaven','skyatnightmagazine','lovethenightsky','spaceflightnow','astrobackyard','nineplanets','earthsky',
                        'stellarium',#software map
                        ],'#0808e1'],
    'Space Organizations & Places':[['nasa','esa','esahubble','cnes','agences-spatiales','hubblesite','moonexpress','aas','amsmeteors','afastronomie','astronomerswithoutborders', #meteor society
                        'spacex','starlink','blueorigin','virgingalactic',
                        'enseignementsup-recherche','arxiv','eventhorizontelescope','aanda','si', #si = airandspace.si.edu
                        'griffithobservatory','kennedyspacecenter','amnh','rmg','adventuresci','intrepidmuseum','mods-museum','spacecenter','visitspacecoast','lowell','sandiegoairandspace','cincinnatiobservatory',
                        'cite-sciences','cite-espace','parisinfo','cap-sciences','nantes','bordeaux','psl','reims','nantesmetropole','espace-sciences','lyon-france','vaulx-en-velin','saintmichellobservatoire','unistra','forumdepartementaldessciences',
                        ],'#6dc85a'],
    'brands':[['unistellaroptics','unistellar','skywatcher','bresser','vaonis','celestron','omegon','meade','bushnell','zhumell'],'#d20623'],
    'ressellers':[['amazon','telescope','space',
                'stelvision','medas-instruments','pierro-astro','astroshop','maison-astronomie','maisonastronomie','telescopes-et-accessoires','achat-telescope','promo-optique','laclefdesetoiles','univers-astro','promo-optique','jeulin','exop',
                'optcorp','telescopicwatch','highpointscientific','levenhuk','bhphotovideo','telescopesplus','buytelescopes','shopatsky','adorama',
                'natureetdecouvertes','loisirsplaisirs','fnac','cdiscount','carrefour','boulanger',
                'walmart','tasco','target','costco','bestbuy',
                'ebay','leboncoin','aliexpress','rakuten','pagesjaunes',],'#95331e'],
    }
column1, column2 = st.columns(2)
bubble_names = ['Space','Planets / moon / sun','Observable objects','Astronomy','Places','Telescopes','Buy Telescopes','Resellers','High-end brands','Unistellar']
def plot_charts(demand_us,where):
    for n in bubble_names:

        top20 = demand_us[demand_us['Topics']==n].groupby(['Domain']).sum().sort_values(by=['Traffic'], axis=0, ascending=True, inplace=False, kind='quicksort', na_position='last').drop('Avg. monthly searches', axis=1)
        top20 = top20.tail(20)
        top20 = top20.reset_index()
        top20['site_type']='other'

        fig = go.Figure()

        for t in site_types:
            top20.loc[top20["Domain"].isin(site_types[t][0]),'site_type'] = t

        fig.add_trace(go.Bar(
            y=top20[top20.site_type == 'other']["Domain"],
            x=top20[top20.site_type == 'other']["Traffic"],
            marker_color='#feb82b',
            marker_line_color='rgba(0, 0, 0, 0)',
            name='other',
            orientation='h'))

        for t in site_types:
            fig.add_trace(go.Bar(
                y=top20[top20.site_type == t]["Domain"],
                x=top20[top20.site_type == t]["Traffic"],
                marker_color=site_types[t][1],
                marker_line_color='rgba(0, 0, 0, 0)',
                name=t,
                orientation='h'))



        fig.update_layout(
            height=500,
            width=500,
            title=n + where,
            plot_bgcolor="#0c0c0e",
            barmode='stack',
            )
        st.plotly_chart(fig)

with column1:
    plot_charts(demand_us,' - Top Websites - United States')


with column2:
    plot_charts(demand_fr,' - Top Websites - France')

if country == 'United States':
    fulldomain = demand_us[demand_us.Topics=='Telescopes'].sort_values(by='Traffic',ascending=False)[['Domain','Url','Traffic']]
elif country == 'France':
    fulldomain = demand_fr.sort_values(by='Traffic',ascending=False)[['Domain','Url','Traffic']]

st.dataframe(demand_us[demand_us.Topics=='Telescopes'])

agdata1 = fulldomain
builder1 = GridOptionsBuilder.from_dataframe(agdata1)
builder1.configure_column("Domain", editable=True)
grid_opt1 = builder1.build()
AgGrid(agdata1, theme='dark', gridOptions=grid_opt1)

# Display top keywords
comment = """
with column1:
    for b in bubble_names:
        st.dataframe(data_us[data_us.bubble == b].head(10)[['Keyword']])

with column2:
    for b in bubble_names:
        st.dataframe(data_fr[data_fr.bubble == b].head(10)[['Keyword']])
"""
