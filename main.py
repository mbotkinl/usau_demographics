import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from plotly.offline import plot
import plotly.graph_objects as go


plt.style.use('fivethirtyeight')


MAPPING = {'Black or African American alone, percent': 'Black/African American',
           'American Indian and Alaska Native alone, percent': 'American Indian/Alaska Native/Aleutian',
           'Asian alone, percent': 'Asian',
           'Native Hawaiian and Other Pacific Islander alone, percent': 'Hawaiian Native/Other Pacific Islander',
           'Two or More Races, percent': 'Multiracial',
           'Hispanic or Latino, percent': 'Hispanic/Latinx',
           'White alone, not Hispanic or Latino, percent': 'White'}


# https://www.census.gov/quickfacts/fact/table/US/PST045219
census_data_2019 = pd.read_csv('./data/QuickFacts Oct-01-2020.csv')
census_data_2019 = census_data_2019[census_data_2019['Fact'].isin(MAPPING.keys())][['Fact', 'United States']]
census_data_2019['us_pop_percent'] = census_data_2019['United States'].str.replace('%', '').astype(float)
census_data_2019['Race/Ethnicity'] = census_data_2019['Fact'].map(MAPPING)

# country_state_cols = [0, 1]
# racial_cols = range(47, 57)
# keep_cols = country_state_cols + list(racial_cols)

data_2019 = pd.read_csv('./data/2019 USAU Members by state-age-gender-demographic-levels - Analysis.csv', skiprows=2)
# total_data_2019 = data_2019.iloc[0, racial_cols]
state_data_2019 = data_2019.loc[data_2019['Country'] == 'US', MAPPING.values()]


total_data_2019 = state_data_2019.sum(axis=0)
# total_data_2019 = total_data_2019[~total_data_2019.index.isin(['Prefer Not to Answer', '[BLANK]'])]

plot_data = total_data_2019.reset_index()

plot_data.columns = ['Race/Ethnicity', 'member_count']
plot_data['member_percent'] = plot_data['member_count'] / total_data_2019.sum() * 100
plot_data = plot_data.merge(census_data_2019[['Race/Ethnicity', 'us_pop_percent']])


# fig, ax = plt.subplots(figsize=(16, 20))
# # ax1 = sns.barplot(x='Race/Ethnicity', y='member_percent', data=plot_data)
# ax1 = sns.barplot(y='Race/Ethnicity', x='member_percent', data=plot_data)


plotly_fig = go.Figure(data=[
    go.Bar(name='USAU Member Percent', x=plot_data['Race/Ethnicity'], y=plot_data['member_percent']),
    go.Bar(name='US Population Percent', x=plot_data['Race/Ethnicity'], y=plot_data['us_pop_percent'])
])
# Change the bar mode
plotly_fig.update_layout(barmode='group')
plot(plotly_fig)
