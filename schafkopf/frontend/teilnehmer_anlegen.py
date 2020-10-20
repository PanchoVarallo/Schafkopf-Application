import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from schafkopf.frontend.generic_objects import wrap_empty_dbc_row, wrap_footer_row


def wrap_teilnehmer_anlegen_layout():
    return html.Div([
        dcc.Store(id='create_teilnehmer_modal_open_n_clicks', data={'n_clicks': 0}),
        dcc.Store(id='create_teilnehmer_modal_close_n_clicks', data={'n_clicks': 0}),
        dbc.Modal([
            dbc.ModalHeader(id='create_teilnehmer_modal_header'),
            dbc.ModalBody(html.Div(id='create_teilnehmer_modal_body')),
            dbc.ModalFooter(
                dbc.Button('Schließen', id='create_teilnehmer_modal_close', color='primary', block=True)
            ), ], id='create_teilnehmer_modal', size="xl", scrollable=True),
        dbc.Container([
            wrap_empty_dbc_row(),
            dbc.Row([
                dbc.Col([
                    html.Div(html.H5('Teilnehmer anlegen'))
                ])], justify='start'),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.FormText('Vorname des neuen Teilnehmers'),
                            dbc.Input(id='teilnehmer_new_vorname', placeholder='', maxLength=20),
                        ]
                    )
                ], xl=6, xs=12),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.FormGroup(
                        [
                            dbc.FormText('Nachname des neuen Teilnehmers'),
                            dbc.Input(id='teilnehmer_new_nachname', placeholder='', maxLength=20),
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
                                       color='primary', block=True),
                        ]
                    )
                ], xl=6, xs=12)
            ]),
            wrap_footer_row()
        ]),
    ])
