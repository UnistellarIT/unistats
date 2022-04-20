# from pydoc_data.topics import topics
# from turtle import width
# from types import CellType
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

data = pd.read_csv("data.csv")
data['Feb 2022'] = data['Feb 2022'].fillna(0).astype(int, errors='ignore')
data['Volume'] = data['Volume'].fillna(0).astype(int, errors='ignore')
data = data.sort_values(by = 'Feb 2022', ascending= False)

bubbles = pd.read_csv("bubbles.csv")

#### SIDEBAR ###

with st.sidebar:

    country = st.radio(
        label = 'Countries',
        options = ("France",
        "United States"
        )
    )

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

#### DASHBOARD ###

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
bubbles['Labels'] = bubbles['Topic'] + ' | Est. sales: ' + bubbles['Sales per year'].astype(int).astype(str)
fig = go.Figure(data=[go.Scatter(
    x=bubbles['Queries per month'],
    y=bubbles['Conversion rate'],
    mode='markers',
    marker=dict(
        color=bubbles['Sales per year']/10,
        size=bubbles['Sales per year']/10,
    ),
    text=bubbles['Labels'],

)])
fig.update_layout(
    height=1000,
    width=1000,
    plot_bgcolor="#0c0c0e",
    xaxis=dict(title='Number of queries per month'),
    yaxis=dict(title='Conversion rate'),
    )
st.plotly_chart(fig)
