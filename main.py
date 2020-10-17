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




# TODO: increase text size everywhere

# TODO show populations on hover?
##### national plot
nat_plot_data = total_data_2019.reset_index()

nat_plot_data.columns = ['Race/Ethnicity', 'member_count']
nat_plot_data['member_percent'] = nat_plot_data['member_count'] / total_data_2019.sum() * 100
nat_plot_data = nat_plot_data.merge(census_total_data[['Race/Ethnicity', 'us_pop_percent']])

nat_plot_data['member_percent_rounded'] = nat_plot_data['member_percent'].round(decimals=2)
nat_plot_data['us_pop_percent_rounded'] = nat_plot_data['us_pop_percent'].round(decimals=2)


# fig, ax = plt.subplots(figsize=(16, 20))
# # ax1 = sns.barplot(x='Race/Ethnicity', y='member_percent', data=plot_data)
# ax1 = sns.barplot(y='Race/Ethnicity', x='member_percent', data=plot_data)

nat_plot_data_1 = nat_plot_data.iloc[[0, 2, 5, 6]]
nat_plot_data_2 = nat_plot_data.iloc[[1, 3, 4]]


def nat_bar_plot(df, file_name):
    plotly_fig = go.Figure(data=[
        go.Bar(name='USAU Members', x=df['Race/Ethnicity'], y=df['member_percent_rounded'],
               text=df['member_percent_rounded'], textposition='outside', hoverinfo='skip'),
        go.Bar(name='US Census Population', x=df['Race/Ethnicity'], y=df['us_pop_percent_rounded'],
               text=df['us_pop_percent_rounded'], textposition='outside', hoverinfo='skip')
    ])
    # Change the bar mode
    plotly_fig.update_layout(barmode='group', legend=dict(orientation="h", y=1.1),
                             xaxis_title="",
                             yaxis_title="Percent of Group",
                             # width=1000,
                             # height=2000,
                             )
    # plot(plotly_fig)
    py.plot(plotly_fig, filename=file_name, auto_open=True)


nat_bar_plot(df=nat_plot_data_1, file_name='national-plot-1')
nat_bar_plot(df=nat_plot_data_2, file_name='national-plot-2')



### STATE DATA
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









##### state plot vertical

MARKER_SIZE = 15
fig = go.Figure()

# todo: show member size

# Add traces
fig.add_trace(go.Scatter(x=plot_df['member_percent'], y=plot_df['state'],
                         mode='markers',
                         marker={'size': MARKER_SIZE},
                         name='USAU Members'))
fig.add_trace(go.Scatter(x=plot_df['census_percent'], y=plot_df['state'],
                         mode='markers',
                         marker={'size': MARKER_SIZE},
                         name='US Census Population'))
fig.update_layout(width=1000, height=1500, legend=dict(orientation="h", y=1.1), xaxis_title="Percent of Group",)
plot(fig)
py.plot(fig, filename='state-compare-plot', auto_open=True)


# fig = go.Figure()
# fig.add_trace(go.Scatter(x=plot_df['percent_disparity'], y=plot_df['state'],
#                          mode='markers',
#                          marker={'size': plot_df['bubble_size']}))
# fig.update_layout(width=1000, height=1500)
# plot(fig)






#### MAP PLOT
fig = go.Figure(data=go.Choropleth(
                locations=plot_df['state'],  # Spatial coordinates
                z=plot_df['percent_disparity'],  # Data to be color-coded
                locationmode='USA-states',  # set of locations match entries in `locations`
                colorscale='Reds',
                colorbar_title="Percent Disparity",
))

fig.update_layout(
    title_text='2019 Racial Disparity in Ultimate',
    geo_scope='usa',  # limite map scope to USA
)
plot(fig)
py.plot(fig, filename='state-disparity-map', auto_open=True)



#### BUBBLE PLOT zoomed in
fig = go.Figure()
# Add traces
fig.add_trace(go.Scatter(x=plot_df['census_percent'], y=plot_df['member_percent'],
                         mode='markers + text',
                         text=plot_df['state'],
                         textposition='top center',
                         hovertemplate=
                         "state: %{text} <br>" +
                         "USAU members: %{marker.size} <br>" +
                         "census percent: %{x:.1f}%<br>" +
                         "member percent: %{y:.1f}%<br>" +
                         "<extra></extra>",
                         marker=dict(
                                size=plot_df['state_members'],
                                sizemode='area',
                                sizeref=2. * max(plot_df['state_members']) / (40. ** 2),
                                sizemin=4
                            )
                         ))
fig.update_xaxes(range=[-0.5, 20])
fig.update_yaxes(range=[-0.1, 4])
fig.update_layout(width=1000, height=1000,
                  xaxis_title="US Census Population Percent",
                  yaxis_title="USAU Member Percent",
                  )
fig.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
plot(fig)
py.plot(fig, filename='state-compare-xy', auto_open=True)



# TODO: add color for states that are close
#### BUBBLE PLOT proportional
fig = go.Figure()
# Add traces
fig.add_trace(go.Scatter(x=[-5, 20], y=[-5, 20],  mode='lines', line=dict(color='firebrick', width=4)))
fig.add_trace(go.Scatter(x=plot_df['census_percent'], y=plot_df['member_percent'],
                         mode='markers',
                         text=plot_df['state'],
                         hovertemplate=
                         "state: %{text} <br>" +
                         "USAU members: %{marker.size} <br>" +
                         "census percent: %{x:.1f}%<br>" +
                         "member percent: %{y:.1f}%<br>" +
                         "<extra></extra>",
                         marker=dict(
                             size=plot_df['state_members'],
                             sizemode='area',
                             sizeref=2. * max(plot_df['state_members']) / (40. ** 2),
                             sizemin=4
                         )))
fig.update_xaxes(range=[-0.5, 20])
fig.update_yaxes(range=[-0.1, 20])
fig.update_layout(width=1000, height=1000,
                  xaxis_title="US Census Population Percent",
                  yaxis_title="USAU Member Percent",
                  )
fig.update_layout(showlegend=False)
fig.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='black')
plot(fig)
py.plot(fig, filename='state-compare-xy-proportional', auto_open=True)