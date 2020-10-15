import datetime as dt

import dash_bootstrap_components as dbc
import dash_html_components as html

from schafkopf.frontend.generic_objects import wrap_empty_dbc_row, wrap_footer_row


def wrap_daten_layout():
    return html.Div([
        dbc.Container([
            wrap_empty_dbc_row(),
            dbc.Row([
                dbc.Col([
                    html.Div(html.H5('Neue Daten eintragen'))
                ])], justify='start'),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.FormText("Name der neuen Runde"),
                            dbc.Input(id="runde_new_name", placeholder="", maxLength=20),
                        ]
                    )
                ], xl=6, xs=12),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.FormText("Ort der neuen Runde"),
                            dbc.Input(id="runde_new_ort", placeholder="", maxLength=20),
                        ]
                    )
                ], xl=6, xs=12),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.FormText("Datum der neuen Runde"),
                            dbc.Input(id="runde_new_date", type='Date', value=dt.date.today()),
                        ]
                    )
                ], xl=6, xs=12),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Button('Neue Runde erstellen',
                               id='create_runde_modal_open',
                               color='primary', block=True, disabled=True),
                ], xl=6, xs=12)
            ]),
            wrap_empty_dbc_row(),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.FormText("Vorname des neuen Teilnehmers"),
                            dbc.Input(id="teilnehmer_new_vorname", placeholder="", maxLength=20),
                        ]
                    )
                ], xl=6, xs=12),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.FormText("Nachname des neuen Teilnehmers"),
                            dbc.Input(id="teilnehmer_new_nachname", placeholder="", maxLength=20),
                        ]
                    )
                ], xl=6, xs=12),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.Button('Neuen Teilnehmer erstellen',
                                       id='create_teilnehmer_modal_open',
                                       color='primary', block=True, disabled=True),
                        ]
                    )
                ], xl=6, xs=12)
            ]),
            wrap_footer_row()
        ]),
    ])
