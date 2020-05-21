import dash
import pandas as pd
import dash_html_components as html
import dash_core_components as dcc
import dash_table
import datetime
from dash.dependencies import Input, Output


def records_to_dict(pool_id):
    record = {
        'Site: Pool': get_site(pool_id) + ": " + get_pool_name(pool_id),
        'Pool Id': pool_id,
        'Minimum Batteries': format(get_avg_min_batts(pool_id), '.2f'),
        'Trucks': get_trucks(pool_id),
        'Batteries': get_batteries(pool_id),
        'Chargers': get_chargers(pool_id),
        'Active Chargers': get_active_chargers(pool_id),
        'Ratio': format(get_ratio(pool_id), '.2f'),
        'Reserve': format(get_reserve(pool_id), '.2%'),
        'Zero Available Picks': get_zap(pool_id),
        'Picks': get_picks(pool_id),
        '-Zero Avail': format(get_per_zap(pool_id), '.1%'),
        'Days with Zero Avail': get_days_zap(pool_id),
        'Charge Time': get_charge_time(pool_id),
        'Queue Time': get_queue_time(pool_id),
        'QT/CT Ratio': format(get_qt_to_ct(pool_id), '.2f')
    }

    return record


def get_avg_min_batts(pool_id):
    return df.loc[df['PoolId'] == pool_id].groupby(['DateLocal'])['QCountAvailable'].min().mean()


def get_pool_ids():
    global cns_sites
    pool_ids = []
    for site in cns_sites:
        pools = sorted(list(dict.fromkeys(df.loc[df['SiteName'] == site]['PoolId'].tolist())))
        for pool in pools:
            pool_ids.append(pool)

    return pool_ids


def get_site(pool_id):
    return df.loc[df['PoolId'] == pool_id]['SiteName'].tolist()[0]


def get_pool_name(pool_id):
    return df.loc[df['PoolId'] == pool_id]['PoolName'].tolist()[0]


def get_trucks(pool_id):
    return df.loc[df['PoolId'] == pool_id]['PoolTruckCount'].tolist()[0]


def get_batteries(pool_id):
    return df.loc[df['PoolId'] == pool_id]['PoolBatCount'].tolist()[0]


def get_chargers(pool_id):
    return df.loc[df['PoolId'] == pool_id]['PoolChargerCount'].tolist()[0]


def get_active_chargers(pool_id):
    if df.loc[df['PoolId'] == pool_id]['ChargerAlias'].nunique() > get_chargers(pool_id):
        return df.loc[df['PoolId'] == pool_id]['ChargerAlias'].nunique()/2 -1
    else:
        return df.loc[df['PoolId'] == pool_id]['ChargerAlias'].nunique()


def get_ratio(pool_id):
    if get_trucks(pool_id) == 0:
        return -1
    else:
        return get_batteries(pool_id)/get_trucks(pool_id)


def get_reserve(pool_id):
    if get_trucks(pool_id) == 0:
        return -1
    else:
        return get_avg_min_batts(pool_id)/get_trucks(pool_id)


def get_zap(pool_id):
    return df.loc[(df['PoolId'] == pool_id) & (df['EventCodeId'] == 101)]['EventCodeId'].count()


def get_picks(pool_id):
    return df.loc[(df['PoolId'] == pool_id) & ((df['EventCodeId'] == 2) | (df['EventCodeId'] == 3) |
                                               (df['EventCodeId'] == 5) | (df['EventCodeId'] == 101))]['EventCodeId'].count()


def get_charge_time(pool_id):
    return df.loc[(df['PoolId'] == pool_id)]['ChargerDurationBucket'].sum()


def get_queue_time(pool_id):
    return df.loc[(df['PoolId'] == pool_id)]['CooldownDurationBucket'].sum()


def get_qt_to_ct(pool_id):
    if get_charge_time(pool_id) == 0:
        return -1
    else:
        return get_queue_time(pool_id)/get_charge_time(pool_id)


def get_per_zap(pool_id):
    if get_picks(pool_id) == 0:
        return -1
    else:
        return get_zap(pool_id)/get_picks(pool_id)


def get_days_zap(pool_id):
    return df.loc[(df['PoolId'] == pool_id) & (df['EventCodeId'] == 101)][['DateLocal', 'EventCodeId']]['DateLocal'].nunique()


df = pd.read_csv('data.csv')
df['DateLocal'] = pd.to_datetime(df['DateLocal'])
df = pd.read_csv('data.csv', parse_dates=['DateLocal', 'EventStartTimeLocal', 'EventTime', 'EventTimeLocal'])


# columns = ['Site', 'Pool Id', 'Minimum Batteries', 'Trucks', 'Batteries', 'Chargers', 'Active Chargers', 'Ratio', 'Reserve',
#            'Zero Abailable Picks', 'Picks', '-Zero Avail', 'Days With Zero Avail', 'Charge Time', 'Queue Time',
#            'QT/CT Ratio']

columns = ['Site: Pool', 'Pool Id', 'Minimum Batteries', 'Trucks', 'Batteries', 'Chargers', 'Active Chargers', 'Ratio',
           'Reserve', 'Zero Available Picks', 'Picks', '-Zero Avail', 'Days with Zero Avail', 'Charge Time',
           'Queue Time', 'QT/CT Ratio']

sites = sorted(list(dict.fromkeys(df['SiteName'])))
cns_sites = sorted(dict.fromkeys(df.loc[(df['EnterpriseName'] == 'C&S Grocers')]['SiteName']))
pool_ids = get_pool_ids()

app = dash.Dash()


app.layout = html.Div([
    # dcc.Dropdown(
    #     id='enterprise-dd',
    #     options=[{'label': name, 'value': name} for name in sorted(list(dict.fromkeys(df['EnterpriseName'].tolist())))],
    #     placeholder='Enterprise',
    #     value=sorted(list(dict.fromkeys(df['EnterpriseName'].tolist())))[0]
    # ),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in columns],
        data=[records_to_dict(pool_id) for pool_id in pool_ids],
        fixed_columns={'headers': True, 'data': 1},
        fixed_rows={'headers': True},
        style_table={'minWidth': '100%'},
        style_cell={
            'height': 'auto',
            # all three widths are needed
            'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
            'whiteSpace': 'normal'
        }
    ),
    dcc.Graph(id="table-output")
])


@app.callback(
    Output('table-output', 'figure'),
    [Input('table', 'data'),
     Input('table', 'columns')]
)
def display_output(rows, columns):
    df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    return {
        'data': [dict(
                type='bar',
                x=df['Site: Pool'],
                y=df['Reserve'],
                yaxis='y1'
            ),
            dict(
                type='scatter',
                x=df['Site: Pool'],
                y=df['QT/CT Ratio'],
                yaxis='y2'
            )],
        'layout': dict(
            yaxis=dict(
                title='Reserve'
            ),
            yaxis2=dict(
                title='QT/CT Ratio',
                side='right',
                overlaying='y'
            )
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)




