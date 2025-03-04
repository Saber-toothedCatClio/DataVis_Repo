import wbdata
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np

# Step 1: Validate and Choose Indicators for Data Fetching
indicators = {
    'NY.GDP.PCAP.CD': 'GDP per capita (current US$)',
    'SP.DYN.LE00.IN': 'Life expectancy at birth (years)',
    'SE.XPD.TOTL.GD.ZS': 'Education spending (% of GDP)',
    'SH.XPD.CHEX.GD.ZS': 'Health spending (% of GDP)'
    # Removed 'EN.ATM.CO2E.PC': 'CO2 emissions (metric tons per capita)' due to retrieval issue
}

# Select countries
countries = ['USA', 'CHN', 'IND', 'BRA', 'ZAF', 'DEU', 'JPN']

# Fetch data for the chosen indicators and countries for the years 2000-2022
data_date = datetime(2000, 1, 1), datetime(2022, 12, 31)
df_list = []

for indicator, indicator_name in indicators.items():
    try:
        # Get data for this indicator
        data = wbdata.get_data(indicator, country=countries, date=data_date)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Extract country name and date
        df['country'] = df['country'].apply(lambda x: x['value'])
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        
        # Add indicator name
        df['indicator'] = indicator_name
        
        df_list.append(df)
    except Exception as e:
        print(f"Error fetching data for indicator {indicator}: {e}")

# Step 2: Combine all data if there are valid responses, else exit
if df_list:
    combined_df = pd.concat(df_list)
else:
    raise Exception("No data fetched. Please check the indicators again.")

# Pivot to get indicators as columns
pivot_df = combined_df.pivot_table(
    index=['country', 'year'],
    columns='indicator',
    values='value'
).reset_index()

# Handle missing values with forward/backward filling using new methods
pivot_df.ffill(axis=0, inplace=True)
pivot_df.bfill(axis=0, inplace=True)

# Step 3: Create Interactive Visualization with Plotly
fig = px.scatter(
    pivot_df, 
    x='GDP per capita (current US$)',
    y='Life expectancy at birth (years)',
    color='country',
    size=np.sqrt(pivot_df['GDP per capita (current US$)']),
    size_max=50,
    hover_name='country',
    hover_data={
        'GDP per capita (current US$)': ':,.2f',
        'Life expectancy at birth (years)': ':,.1f',
        'Education spending (% of GDP)': ':,.2f',
        'Health spending (% of GDP)': ':,.2f'
    },
    animation_frame='year',
    animation_group='country',
    range_x=[0, pivot_df['GDP per capita (current US$)'].max() * 1.1],
    range_y=[pivot_df['Life expectancy at birth (years)'].min() * 0.9, 
             pivot_df['Life expectancy at birth (years)'].max() * 1.05],
    labels={
        'GDP per capita (current US$)': 'GDP per Capita (USD)',
        'Life expectancy at birth (years)': 'Life Expectancy (years)'
    },
    title='Development Indicators (2000-2022)'
)

# Improve layout
fig.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(size=12),
    legend=dict(
        title=dict(text='Country'),
        bordercolor='LightGrey',
        borderwidth=1
    ),
    margin=dict(l=20, r=20, t=50, b=20),
    xaxis=dict(
        showgrid=True,
        gridcolor='lightgrey',
        zeroline=False
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='lightgrey',
        zeroline=False
    ),
    updatemenus=[{
        'buttons': [
            {
                'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}],
                'label': 'Play',
                'method': 'animate'
            },
            {
                'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                'label': 'Pause',
                'method': 'animate'
            }
        ],
        'direction': 'left',
        'pad': {'r': 10, 't': 10},
        'showactive': False,
        'type': 'buttons',
        'x': 0.1,
        'y': 0
    }],
    sliders=[{
        'active': 0,
        'yanchor': 'top',
        'xanchor': 'left',
        'currentvalue': {
            'font': {'size': 16},
            'prefix': 'Year: ',
            'visible': True,
            'xanchor': 'right'
        },
        'transition': {'duration': 300, 'easing': 'cubic-in-out'},
        'pad': {'b': 10, 't': 50},
        'len': 0.9,
        'x': 0.1,
        'y': 0,
    }]
)

# Show the figure
fig.show()

# Optional: Save as HTML file
# fig.write_html("world_bank_data_visualization.html")