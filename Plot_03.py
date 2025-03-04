import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Fruit Price Analysis Dashboard", page_icon=":bar_chart:", layout="wide")

st.title(":bar_chart: Fruit Price Analysis Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)


fl = st.file_uploader(":file_folder: Upload a file", type=(["csv", "txt", "xlsx", "xls"]))
if fl is not None:
    df = pd.read_csv(fl)
else:
    df = pd.read_csv("/Users/clioluo/Desktop/Data Visualization/Week 8/Fruit-Prices-2022.csv")


form_color_map = {
    "Fresh": px.colors.qualitative.Pastel[0],
    "Frozen": px.colors.qualitative.Pastel[1],
    "Canned": px.colors.qualitative.Pastel[2],
    "Dried": px.colors.qualitative.Pastel[3],
    "Juice": px.colors.qualitative.Pastel[4],
    "Other": px.colors.qualitative.Pastel[5]
}

def map_colors(data, color_map, column):
    return [color_map[val] for val in data[column]]


def generate_charts(df):
    col1, col2 = st.columns(2)

    with col1:
        # Most common form of fruit (Pie Chart)
        form_counts = df['Form'].value_counts().reset_index()
        form_counts.columns = ['Form', 'Count']
        form_counts['Color'] = map_colors(form_counts, form_color_map, 'Form')
        fig1 = px.pie(form_counts, names='Form', values='Count', title='Most Common Form of Fruit', 
                      color='Form', color_discrete_sequence=form_counts['Color'])
        st.plotly_chart(fig1)

    with col2:
        # Most expensive form of fruit based on CupEquivalentPrice (Bar Chart)
        avg_form_price = df.groupby('Form')['CupEquivalentPrice'].mean().sort_values(ascending=False).reset_index()
        avg_form_price['Color'] = map_colors(avg_form_price, form_color_map, 'Form')
        fig2 = px.bar(avg_form_price, x='Form', y='CupEquivalentPrice', title='Most Expensive Form of Fruit Based on Cup Equivalent Price', 
                      color='Form', color_discrete_sequence=avg_form_price['Color'], 
                      labels={'Form': 'Form', 'CupEquivalentPrice': 'Average Cup Equivalent Price (US dollars)'})
        st.plotly_chart(fig2)
    
    # Most expensive fruit based on CupEquivalentPrice (Heat Map with gridlines)
    fruit_form_price = df.pivot_table(index='Fruit', columns='Form', values='CupEquivalentPrice', aggfunc='mean').fillna(0)
    fig3 = go.Figure(data=go.Heatmap(
        z=fruit_form_price.values,
        x=fruit_form_price.columns,
        y=fruit_form_price.index,
        colorscale='OrRd',
        showscale=True,
        text=fruit_form_price.values,
        texttemplate="%{text:.2f} USD",
        textfont={"size":12},
        xgap=1,
        ygap=1
    ))
    fig3.update_layout(title='Most Expensive Fruit Based on Cup Equivalent Price (US dollars)', width=1500, height=1000)
    fig3.update_xaxes(title="Form", side='top')
    fig3.update_yaxes(title="Fruit")
    st.plotly_chart(fig3)


generate_charts(df)

st.markdown("**Data Source:** [USDA - Fruit and Vegetable Prices](https://www.ers.usda.gov/data-products/fruit-and-vegetable-prices)")