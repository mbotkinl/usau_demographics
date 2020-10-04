import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt
from plotly.offline import plot
import chart_studio.plotly as py
import plotly.graph_objects as go
from utils import STATE_MAPPING

# plt.style.use('fivethirtyeight')

import chart_studio
# todo: hide this on git
chart_studio.tools.set_credentials_file(username='micahkaye', api_key='gX9Ye6qtLUFyDMOYL4V7')


# national level census


# MAPPING = {'Black or African American alone, percent': 'Black/African American',
#            'American Indian and Alaska Native alone, percent': 'American Indian/Alaska Native/Aleutian',
#            'Asian alone, percent': 'Asian',
#            'Native Hawaiian and Other Pacific Islander alone, percent': 'Hawaiian Native/Other Pacific Islander',
#            'Two or More Races, percent': 'Multiracial',
#            'Hispanic or Latino, percent': 'Hispanic/Latinx',
#            'White alone, not Hispanic or Latino, percent': 'White'}

# https://www.census.gov/quickfacts/fact/table/US/PST045219
# https://www.census.gov/quickfacts/fact/table/AL,CA,US/RHI225219
# census_data_2019 = pd.read_csv('./data/QuickFacts Oct-01-2020.csv')
# census_data_2019 = census_data_2019[census_data_2019['Fact'].isin(MAPPING.keys())][['Fact', 'United States']]
# census_data_2019['us_pop_percent'] = census_data_2019['United States'].str.replace('%', '').astype(float)
# census_data_2019['Race/Ethnicity'] = census_data_2019['Fact'].map(MAPPING)

# state level census
# https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2010-2019/sc-est2019-alldata6.pdf
MAPPING = {2: 'Black/African American',
           3: 'American Indian/Alaska Native/Aleutian',
           4: 'Asian',
           5: 'Hawaiian Native/Other Pacific Islander',
           6: 'Multiracial',
           7: 'Hispanic/Latinx',
           1: 'White'}

# https://www.census.gov/data/tables/time-series/demo/popest/2010s-state-detail.html
# https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2010-2019/sc-est2019-alldata6.pdf
# Age, Sex, Race, and Hispanic Origin - 6 race groups (5 race alone groups and one multiple race group) (SC-EST2019-ALLDATA6)
census_data = pd.read_csv('./data/sc-est2019-alldata6.csv')
subset_total_groups = (census_data['SEX'] == 0) & (census_data['ORIGIN'] != 0)
census_state_data_raw = census_data[subset_total_groups].groupby(['NAME', 'ORIGIN', 'RACE'])['POPESTIMATE2019'].sum().reset_index()
print(census_state_data_raw.sum())
# sum all hispanic but keep non hispanic groups
hispanic_counts = census_state_data_raw[census_state_data_raw['ORIGIN'] == 2].groupby(['NAME'])['POPESTIMATE2019'].sum().reset_index()
hispanic_counts['RACE'] = 7
other_counts = census_state_data_raw.loc[census_state_data_raw['ORIGIN'] == 1, ['NAME', 'RACE', 'POPESTIMATE2019']]

census_state_data = pd.concat([hispanic_counts, other_counts])
census_state_data['Race/Ethnicity'] = census_state_data['RACE'].map(MAPPING)
print(census_state_data.sum())

census_total_data = census_state_data.groupby('Race/Ethnicity')['POPESTIMATE2019'].sum().reset_index()
census_total_data['us_pop_percent'] = census_total_data['POPESTIMATE2019'] / census_total_data['POPESTIMATE2019'].sum() * 100


# read in USAU data
data_2019 = pd.read_csv('./data/2019 USAU Members by state-age-gender-demographic-levels - Analysis.csv', skiprows=2)
# total_data_2019 = data_2019.iloc[0, racial_cols]
state_data_2019 = data_2019.loc[data_2019['Country'] == 'US', ['State/Prov'] + list(MAPPING.values())]


total_data_2019 = state_data_2019[MAPPING.values()].sum(axis=0)
# total_data_2019 = total_data_2019[~total_data_2019.index.isin(['Prefer Not to Answer', '[BLANK]'])]










# national plot
plot_data = total_data_2019.reset_index()

plot_data.columns = ['Race/Ethnicity', 'member_count']
plot_data['member_percent'] = plot_data['member_count'] / total_data_2019.sum() * 100
plot_data = plot_data.merge(census_total_data[['Race/Ethnicity', 'us_pop_percent']])


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

py.plot(plotly_fig, filename='national-plot', auto_open=True)



# state plot

state_data_2019['state_members'] = state_data_2019[MAPPING.values()].sum(axis=1)
melt_df = pd.melt(state_data_2019, id_vars=['State/Prov', 'state_members'], value_vars=MAPPING.values(),
                  var_name='Race/Ethnicity', value_name='member_count')
melt_df['member_percent'] = melt_df['member_count'] / melt_df['state_members'] * 100
melt_df = melt_df.rename(columns={'State/Prov': 'state'})

census_state_pop = census_state_data.groupby('NAME')['POPESTIMATE2019'].sum().reset_index()
census_state_pop = census_state_pop.rename(columns={'POPESTIMATE2019': 'state_pop'})
census_state_data = pd.merge(census_state_data, census_state_pop, on='NAME')
census_state_data['census_percent'] = census_state_data['POPESTIMATE2019'] / census_state_data['state_pop'] * 100
census_state_data['state'] = census_state_data['NAME'].map(STATE_MAPPING)


state_plot_data = pd.merge(census_state_data[['state', 'Race/Ethnicity', 'census_percent']],
                           melt_df[['state', 'Race/Ethnicity', 'member_percent', 'state_members']],
                           on=['state', 'Race/Ethnicity'], how='outer')


race_select = 'Black/African American'

plot_df = state_plot_data[state_plot_data['Race/Ethnicity'] == race_select]
plot_df = plot_df.sort_values('state_members', ascending=False)

plot_df['percent_disparity'] = plot_df['census_percent'] - plot_df['member_percent']

new_max = 40
new_min = 5
old_max = plot_df['state_members'].max()
old_min = plot_df['state_members'].min()
plot_df['bubble_size'] = (((plot_df['state_members'] - old_min) * (new_max - new_min)) / (old_max - old_min)) + new_min


MARKER_SIZE = 15
fig = go.Figure()

# todo: show member size

# Add traces
fig.add_trace(go.Scatter(x=plot_df['member_percent'], y=plot_df['state'],
                         mode='markers',
                         marker={'size': MARKER_SIZE},
                         name='Member'))
fig.add_trace(go.Scatter(x=plot_df['census_percent'], y=plot_df['state'],
                         mode='markers',
                         marker={'size': MARKER_SIZE},
                         name='Census'))
fig.update_layout(width=1000, height=1500)
plot(fig)
py.plot(fig, filename='state-compare-plot', auto_open=True)


# fig = go.Figure()
# fig.add_trace(go.Scatter(x=plot_df['percent_disparity'], y=plot_df['state'],
#                          mode='markers',
#                          marker={'size': plot_df['bubble_size']}))
# fig.update_layout(width=1000, height=1500)
# plot(fig)


fig = go.Figure(data=go.Choropleth(
                locations=plot_df['state'],  # Spatial coordinates
                z=plot_df['percent_disparity'],  # Data to be color-coded
                locationmode='USA-states',  # set of locations match entries in `locations`
                colorscale='Reds',
                colorbar_title="Percent Disparity",
))

fig.update_layout(
    title_text='2019 Racial Disparity in Ultimate',
    geo_scope='usa', # limite map scope to USA
)
plot(fig)
py.plot(fig, filename='state-disparity-map', auto_open=True)


fig = go.Figure()
# Add traces
fig.add_trace(go.Scatter(x=plot_df['census_percent'], y=plot_df['member_percent'],
                         mode='markers',
                         text=plot_df['state'],
                         hovertemplate=
                         "state: %{text} <br>" +
                         # "state members: %{text} <br>" +
                         "census percent: %{x:.0}%<br>" +
                         "member percent: %{y:.0}%<br>" +
                         "<extra></extra>",
                         marker={'size': plot_df['bubble_size']}))
fig.update_xaxes(range=[0, 20])
fig.update_yaxes(range=[0, 20])
fig.update_layout(width=1000, height=1000)

plot(fig)
py.plot(fig, filename='state-compare-xy', auto_open=True)
