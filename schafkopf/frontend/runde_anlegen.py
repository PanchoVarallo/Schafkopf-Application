import datetime as dt
import pathlib

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from schafkopf.database.queries import get_runden
from schafkopf.frontend.generic_objects import wrap_empty_dbc_row, wrap_footer_row


def wrap_runde_anlegen_layout():
    current = pathlib.Path(__file__).name.split('.')[0]
    return html.Div([
        dcc.Store(id='create_runde_modal_open_n_clicks', data={'n_clicks': 0}),
        dcc.Store(id='create_runde_modal_close_n_clicks', data={'n_clicks': 0}),
        dbc.Modal([
            dbc.ModalHeader(id='create_runde_modal_header'),
            dbc.ModalBody(html.Div(id='create_runde_modal_body')),
            dbc.ModalFooter([
                dbc.Button('Schließen', id='create_runde_modal_close', color='primary', block=True),
                dbc.Button('Schließen', id='create_runde_modal_close_reload', color='primary', block=True,
                           href=f'/{current}', external_link=True)]
            ), ], id='create_runde_modal', size='xl', scrollable=True),
        dbc.Container([
            wrap_empty_dbc_row(),
            dbc.Row([
                dbc.Col([
                    html.Div(html.H5('Runde anlegen'))
                ])], justify='start'),
            html.Datalist(id='name_list', children=[html.Option(value=name)
                                                    for name in get_runden(dataframe=True)['name'].unique().tolist()]),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.FormText('Name der neuen Runde'),
                            dbc.Input(id='runde_new_name', placeholder='', maxLength=40, list='name_list'),
                        ]
                    )
                ], xl=6, xs=12),
            ]),
            html.Datalist(id='ort_list', children=[html.Option(value=ort)
                                                   for ort in get_runden(dataframe=True)['ort'].unique().tolist()]),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.FormText('Ort der neuen Runde'),
                            dbc.Input(id='runde_new_ort', placeholder='', maxLength=20, list='ort_list'),
                        ]
                    )
                ], xl=6, xs=12),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.FormText('Datum der neuen Runde'),
                            dbc.Input(id='runde_new_date', type='Date', value=dt.date.today()),
                        ]
                    )
                ], xl=6, xs=12),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.Button('Neue Runde erstellen',
                                       id='create_runde_modal_open',
                                       color='primary', block=True),
                        ]
                    )
                ], xl=6, xs=12)
            ]),
            wrap_footer_row()
        ]),
    ])
