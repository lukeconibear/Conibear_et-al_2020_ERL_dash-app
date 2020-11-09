#!/usr/bin/env python3.8
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
import geopandas as gpd
from shapely.geometry import LineString, MultiLineString
import numpy as np
import plotly.express as px

path = './static/' # change this to the suitable path

mapboxt = open(path + ".mapbox_token").read().rstrip()

# --- functions ---
def shapefile_to_geojson(gdf, index_list, level=1, tolerance=0.025):
    """
    Description:
        Converts shapefile to geojson that can be used as a plotly go.Choroplethmapbox.
    Args:
        gdf (str): Path to geojson shapefile.
        index_list (list): Sublist of list(gdf.index) or gdf.index for all data.
        level (int, default=1): Shapefile level, 0=country, 1=state/province, 2=city/prefecture, etc.
        tolerance (float, default=0.025): Parameter to set the Polygon/MultiPolygon degree of simplification.
    Returns:
        geojson (dict): Dictionary of converted json shapefile.
    """
    geo_names = list(gdf[f'NAME_{level}'])
    geojson = {'type':'FeatureCollection', 'features':[]}
    for index in index_list:
        geo = gdf['geometry'][index].simplify(tolerance)
        if isinstance(geo.boundary, LineString):
            gtype = 'Polygon'
            bcoords = np.dstack(geo.boundary.coords.xy).tolist()
        elif isinstance(geo.boundary, MultiLineString):
            gtype = 'MultiPolygon'
            bcoords = []
            for b in geo.boundary:
                x, y = b.coords.xy
                coords = np.dstack((x,y)).tolist()
                bcoords.append(coords)
        else: pass
        feature = {'type':'Feature',
                   'id':index,
                   'properties':{'name':geo_names[index]},
                   'geometry':{'type':gtype, 'coordinates': bcoords},
                   }
        geojson['features'].append(feature)
        
    return geojson


# --- input data ---
level = 1
gdf = gpd.read_file(path + 'gadm36_IND_' + str(level) +'.shp', encoding='utf-8')
# remove superfluous states
gdf.drop(5, inplace=True)
gdf.drop(17, inplace=True)
gdf.reset_index(inplace=True)
del gdf['index']
geojsdata = shapefile_to_geojson(gdf, list(gdf.index))

appended_df = []
appended_format_df = []
scenarios = ['BASELINE', 'ALLLPG', 'URB15', 'EMIS50', 'STATE50']

for scenario in scenarios:
    df = pd.read_csv(path + 'Conibear_et_al_2020_supp-data_' + scenario + '.csv')[0:34]
    df.rename(columns={'Unnamed: 0':'geo-id'}, inplace=True)
    df['scenario'] = scenario
    appended_df.append(df)
    
    
plot_labels = [
    "Ambient PM\u2082.\u2085 concentration",
    "Household PM\u2082.\u2085 concentration, females",
    "Household PM\u2082.\u2085 concentration, males",
    "Household PM\u2082.\u2085 concentration, children",
    "MORT from total PM\u2082.\u2085 exposure",
    "MORT from ambient PM\u2082.\u2085 exposure",
    "MORT from household PM\u2082.\u2085 exposure",
    "DALYs rate from total PM\u2082.\u2085 exposure",
    "DALYs rate from ambient PM\u2082.\u2085 exposure",
    "DALYs rate from household PM\u2082.\u2085 exposure"
]
plot_variables = [
    'apm25_popweighted',
    'hpm25_female_popweighted',
    'hpm25_male_popweighted',
    'hpm25_child_popweighted',
    'mort_tpm25_6cod_mean_total',
    'mort_apm25_6cod_mean_total',
    'mort_hpm25_6cod_mean_total',
    'dalys_tpm25_rate_6cod_mean_total',
    'dalys_apm25_rate_6cod_mean_total',
    'dalys_hpm25_rate_6cod_mean_total'
]
min_values_abs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
max_values_abs = [100, 300, 300, 300, 150000, 150000, 150000, 3500, 3500, 3500]
min_values_diff = [-50, -300, -300, -300, -50000, -50000, -50000, -1500, -1500, -1500]
max_values_diff = [50, 300, 300, 300, 50000, 50000, 50000, 1500, 1500, 1500]
df_baseline = pd.read_csv(path + 'Conibear_et_al_2020_supp-data_BASELINE.csv')

for scenario in scenarios:
    df = pd.read_csv(path + 'Conibear_et_al_2020_supp-data_' + scenario + '.csv')
    if scenario == 'BASELINE':
        plot_title = [
            ('Ambient ' + u'PM\u2082.\u2085' + ' concentration', '(India = ' + str(df.apm25_popweighted.values[-1]) + ' ' + u'\u03bcg' + '/' + u'm\u00b3' + ")"),
            ('Household ' + u'PM\u2082.\u2085' + ' concentration, females', '(India = ' + str(df.hpm25_female_popweighted.values[-1]) + ' ' + u'\u03bcg' + '/' + u'm\u00b3' + ')'),
            ('Household ' + u'PM\u2082.\u2085' + ' concentration, males', '(India = ' + str(df.hpm25_male_popweighted.values[-1]) + ' ' + u'\u03bcg' + '/' + u'm\u00b3' + ')'),
            ('Household ' + u'PM\u2082.\u2085' + ' concentration, children', '(India = ' + str(df.hpm25_child_popweighted.values[-1]) + ' ' + u'\u03bcg' + '/' + u'm\u00b3' + ')'),
            ('MORT from total ' + u'PM\u2082.\u2085' + ' exposure', '(India = ' + '{:,}'.format(int(round(df.mort_tpm25_6cod_mean_total.values[-1], -3))) + ')'),
            ('MORT from ambient ' + u'PM\u2082.\u2085' + ' exposure', '(India = ' + '{:,}'.format(int(round(df.mort_apm25_6cod_mean_total.values[-1], -3))) + ')'),
            ('MORT from household ' + u'PM\u2082.\u2085' + ' exposure', '(India = ' + '{:,}'.format(int(round(df.mort_hpm25_6cod_mean_total.values[-1], -3))) + ')'),
            ('DALYs rate from total ' + u'PM\u2082.\u2085' + ' exposure', '(India = ' + '{:,}'.format(int(round(df.dalys_tpm25_rate_6cod_mean_total.values[-1]))) + ')'),
            ('DALYs rate from ambient ' + u'PM\u2082.\u2085' + ' exposure', '(India = ' + '{:,}'.format(int(round(df.dalys_apm25_rate_6cod_mean_total.values[-1]))) + ')'),
            ('DALYs rate from household ' + u'PM\u2082.\u2085' + ' exposure', '(India = ' + '{:,}'.format(int(round(df.dalys_hpm25_rate_6cod_mean_total.values[-1]))) + ')')
        ]
    else:
        plot_title = [
            ('Ambient ' + u'PM\u2082.\u2085' + ' concentration', '(India = ' + str(df.apm25_popweighted.values[-1]) + ' ' + u'\u03bcg' + '/' + u'm\u00b3' + ", " + str(int(100 * df.apm25_popweighted.values[-1] / df_baseline.apm25_popweighted.values[-1])) + "%)"),
            ('Household ' + u'PM\u2082.\u2085' + ' concentration, females', '(India = ' + str(df.hpm25_female_popweighted.values[-1]) + ' ' + u'\u03bcg' + '/' + u'm\u00b3' + ", " + str(int(100 * df.hpm25_female_popweighted.values[-1] / df_baseline.hpm25_female_popweighted.values[-1])) + "%)"),
            ('Household ' + u'PM\u2082.\u2085' + ' concentration, males', '(India = ' + str(df.hpm25_male_popweighted.values[-1]) + ' ' + u'\u03bcg' + '/' + u'm\u00b3' + ", " + str(int(100 * df.hpm25_male_popweighted.values[-1] / df_baseline.hpm25_male_popweighted.values[-1])) + "%)"),
            ('Household ' + u'PM\u2082.\u2085' + ' concentration, children', '(India = ' + str(df.hpm25_child_popweighted.values[-1]) + ' ' + u'\u03bcg' + '/' + u'm\u00b3' + ", " + str(int(100 * df.hpm25_child_popweighted.values[-1] / df_baseline.hpm25_child_popweighted.values[-1])) + "%)"),
            ('MORT from total ' + u'PM\u2082.\u2085' + ' exposure', '(India = ' + '{:,}'.format(int(round(df.mort_tpm25_6cod_mean_total.values[-1], -3))) + ", " + str(int(100 * df.mort_tpm25_6cod_mean_total.values[-1] / df_baseline.mort_tpm25_6cod_mean_total.values[-1])) + "%)"),
            ('MORT from ambient ' + u'PM\u2082.\u2085' + ' exposure', '(India = ' + '{:,}'.format(int(round(df.mort_apm25_6cod_mean_total.values[-1], -3))) + ", " + str(int(100 * df.mort_apm25_6cod_mean_total.values[-1] / df_baseline.mort_apm25_6cod_mean_total.values[-1])) + "%)"),
            ('MORT from household ' + u'PM\u2082.\u2085' + ' exposure', '(India = ' + '{:,}'.format(int(round(df.mort_hpm25_6cod_mean_total.values[-1], -3))) + ", " + str(int(100 * df.mort_hpm25_6cod_mean_total.values[-1] / df_baseline.mort_hpm25_6cod_mean_total.values[-1])) + "%)"),
            ('DALYs rate from total ' + u'PM\u2082.\u2085' + ' exposure', '(India = ' + '{:,}'.format(int(round(df.dalys_tpm25_rate_6cod_mean_total.values[-1]))) + ", " + str(int(100 * df.dalys_tpm25_rate_6cod_mean_total.values[-1] / df_baseline.dalys_tpm25_rate_6cod_mean_total.values[-1])) + "%)"),
            ('DALYs rate from ambient ' + u'PM\u2082.\u2085' + ' exposure', '(India = ' + '{:,}'.format(int(round(df.dalys_apm25_rate_6cod_mean_total.values[-1]))) + ", " + str(int(100 * df.dalys_apm25_rate_6cod_mean_total.values[-1] / df_baseline.dalys_apm25_rate_6cod_mean_total.values[-1])) + "%)"),
            ('DALYs rate from household ' + u'PM\u2082.\u2085' + ' exposure', '(India = ' + '{:,}'.format(int(round(df.dalys_hpm25_rate_6cod_mean_total.values[-1]))) + ", " + str(int(100 * df.dalys_hpm25_rate_6cod_mean_total.values[-1] / df_baseline.dalys_hpm25_rate_6cod_mean_total.values[-1])) + "%)")
        ]
        
    format_data_abs = []
    format_data_diff = []
    for plot_index in range(10):    
        format_data_abs.append(
            (
                plot_labels[plot_index],
                plot_variables[plot_index],
                min_values_abs[plot_index],
                max_values_abs[plot_index],
                '0,0',
                plot_title[plot_index][0],
                plot_title[plot_index][1]
            )
        )
        format_data_diff.append(
            (
                plot_labels[plot_index],
                plot_variables[plot_index],
                min_values_diff[plot_index],
                max_values_diff[plot_index],
                '0,0',
                plot_title[plot_index][0],
                plot_title[plot_index][1]
            )
        )
        
    if scenario == 'BASELINE':
        format_df = pd.DataFrame(format_data_abs, columns=['variable_map', 'variable' , 'min_range', 'max_range' , 'format', 'verbage', 'verbage_value'])
    else:
        format_df = pd.DataFrame(format_data_diff, columns=['variable_map', 'variable' , 'min_range', 'max_range' , 'format', 'verbage', 'verbage_value'])
        
        
    format_df['scenario'] = scenario
    appended_format_df.append(format_df)

    
df_merged = pd.concat(appended_df, sort=False)
format_df_merged = pd.concat(appended_format_df, sort=False)

# --- app ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

body = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("Public health benefits of clean household energy in India", style={'fontSize': 16}),
                        html.P(
                            """\
An interactive plot visualising how a complete transition to
clean household energy in India can save one-quarter of the
healthy life lost to particulate matter pollution exposure in India.""",
                        style={'fontSize': 12}),
                        html.A("For more information, see the paper here.", href='https://doi.org/10.1088/1748-9326/ab8e8a', target="_blank", style={'fontSize': 12}),
                        html.H5("Scenario", style={'fontSize': 14}),
                        html.Div(
                            [
                             dcc.Dropdown(
                                 id='scenario-select', value='BASELINE', searchable=False, clearable=False, style={'fontSize': 12},
                                 options=[{'label':scenario, 'value':scenario} for scenario in scenarios],
                                 )
                             ]
                        ),
                        html.Ul(
                            [
                             html.Li('BASELINE = Present-day emissions.', style={'fontSize': 12}),
                             html.Li('ALLLPG = Complete household transition from solid fuels to LPG.', style={'fontSize': 12}),
                             html.Li('URB15 = Partial transition of ALLLPG within 15 km of urban areas.', style={'fontSize': 12}),
                             html.Li('STATE50 = Emission reduction of URB15 applied evenly across each state.', style={'fontSize': 12}),
                             html.Li('EMIS50 = Continued solid fuel use (stacking) at 50% after transitioning to LPG.', style={'fontSize': 12})
                            ]
                        ),
                        html.H5("Variable", style={'fontSize': 14}),
                        html.Div(
                            [
                             dcc.Dropdown(
                                 id='variable-select', value='apm25_popweighted', searchable=False, clearable=False, style={'fontSize': 12},
                                 options=[{'label':row['variable_map'], 'value':row['variable']} for index, row in format_df.iterrows()],
                                 )
                            ]
                        ),
                        html.Ul(
                            [
                             html.Li('PM\u2082.\u2085 = Fine particulate matter.', style={'fontSize': 12}),
                             html.Li('MORT = Premature mortality, per year.', style={'fontSize': 12}),
                             html.Li('DALYs = Disability-adjusted life years, per year.', style={'fontSize': 12})
                            ]
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dcc.Graph(id='choropleth-graph'),
                    ]
                ),
            ]
        )
    ],
    className="mt-4",
)

app.layout = html.Div([body])

@app.callback(
    dash.dependencies.Output('choropleth-graph', 'figure'),
        [
         dash.dependencies.Input('scenario-select', 'value'),
         dash.dependencies.Input('variable-select', 'value')
        ]
    )

def update_graph(scenario, variable):
    if scenario == 'BASELINE':
        colors = 'YlOrRd'
    else:
        colors = px.colors.diverging.BrBG[::-1]
        
    trace = go.Choroplethmapbox(
        z=df_merged[df_merged['scenario'] == scenario][variable],
        locations=df_merged[df_merged['scenario'] == scenario]['geo-id'], 
        geojson=geojsdata,
        colorscale=colors, 
        colorbar=dict(thickness=20, ticklen=3),
        zmin=format_df_merged[(format_df_merged['scenario'] == scenario) & (format_df_merged['variable'] == variable)]['min_range'].values[0],
        zmax=format_df_merged[(format_df_merged['scenario'] == scenario) & (format_df_merged['variable'] == variable)]['max_range'].values[0],
        text=df_merged[df_merged['scenario'] == scenario]['location'],     
        marker_line_width=0.1, 
        marker_opacity=0.7,             
        hovertemplate='<b>State</b>: <b>%{text}</b>'+ '<br> <b>Value </b>: %{z}<br>'
    )
    layout = go.Layout(
        title=scenario + '<br>' \
              + format_df_merged.loc[(format_df_merged['scenario'] == scenario) & (format_df_merged['variable'] == variable)]['verbage'].values[0] + '<br>' \
              + format_df_merged.loc[(format_df_merged['scenario'] == scenario) & (format_df_merged['variable'] == variable)]['verbage_value'].values[0], 
        mapbox=dict(center=dict(lat=22.5, lon=83.0), accesstoken=mapboxt, zoom=3.1), 
        margin=dict(t=100, b=0, l=0, r=0), 
        height=500,
        font={'size': 11}
    )
    return {'data':[trace], 'layout':layout}


if __name__ == '__main__':
    app.run_server()
