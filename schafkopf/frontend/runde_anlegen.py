import datetime as dt

import dash_bootstrap_components as dbc
import dash_html_components as html

from schafkopf.frontend.generic_objects import wrap_empty_dbc_row, wrap_footer_row


def wrap_runde_anlegen_layout():
    return html.Div([
        dbc.Container([
            wrap_empty_dbc_row(),
            dbc.Row([
                dbc.Col([
                    html.Div(html.H5('Runde anlegen'))
                ])], justify='start'),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.FormText('Name der neuen Runde'),
                            dbc.Input(id='runde_new_name', placeholder='', maxLength=20),
                        ]
                    )
                ], xl=6, xs=12),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.FormText('Ort der neuen Runde'),
                            dbc.Input(id='runde_new_ort', placeholder='', maxLength=20),
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
                                       color='primary', block=True, disabled=True),
                        ]
                    )
                ], xl=6, xs=12)
            ]),
            wrap_footer_row()
        ]),
    ])
