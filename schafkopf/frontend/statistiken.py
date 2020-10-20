import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from schafkopf.database.queries import get_teilnehmer, \
    get_latest_einzelspiel_id, get_runde_id_by_einzelspiel_id, get_einzelspiele_by_einzelspiel_ids, get_runden
from schafkopf.frontend.generic_objects import wrap_empty_dbc_row, wrap_dbc_col, wrap_dash_dropdown_div, wrap_footer_row


def wrap_statistiken_layout():
    teilnehmers_options = [{'label': f'{s.name}', 'value': f'{s.id}'} for s in get_teilnehmer()]
    einzelspiel_id = get_latest_einzelspiel_id()
    runde_id = get_runde_id_by_einzelspiel_id(einzelspiel_id)
    einzelspiel = get_einzelspiele_by_einzelspiel_ids([einzelspiel_id])
    geber_id = einzelspiel[0].ausspieler_id if len(einzelspiel) == 1 else None
    ausspieler_id = einzelspiel[0].mittelhand_id if len(einzelspiel) == 1 else None
    mittelhand_id = einzelspiel[0].hinterhand_id if len(einzelspiel) == 1 else None
    hinterhand_id = einzelspiel[0].geberhand_id if len(einzelspiel) == 1 else None
    if len(einzelspiel) == 1 and einzelspiel[0].geber_id != einzelspiel[0].geberhand_id:
        geberhand_id = einzelspiel[0].geber_id
    elif len(einzelspiel) == 1 and einzelspiel[0].geber_id == einzelspiel[0].geberhand_id:
        geberhand_id = einzelspiel[0].ausspieler_id
    else:
        geberhand_id = None
    return html.Div([
        html.Div([
            dcc.Store(id='stats_teilnehmer_modal_open_n_clicks', data={'n_clicks': 0}),
            dcc.Store(id='stats_teilnehmer_modal_close_n_clicks', data={'n_clicks': 0}),
            dcc.Store(id='stats_runden_modal_open_n_clicks', data={'n_clicks': 0}),
            dcc.Store(id='stats_runden_modal_close_n_clicks', data={'n_clicks': 0}),
            dcc.Store(id='stats_all_modal_open_n_clicks', data={'n_clicks': 0}),
            dcc.Store(id='stats_all_modal_close_n_clicks', data={'n_clicks': 0}),
            dbc.Modal([
                dbc.ModalHeader(id='stats_teilnehmer_modal_header'),
                dbc.ModalBody(html.Div(id='stats_teilnehmer_modal_body')),
                dbc.ModalFooter(
                    dbc.Button('Schließen', id='stats_teilnehmer_modal_close', color='primary', block=True)
                ), ], id='stats_teilnehmer_modal', size='xl', scrollable=True),
            dbc.Modal([
                dbc.ModalHeader(id='stats_runden_modal_header'),
                dbc.ModalBody(html.Div(id='stats_runden_modal_body')),
                dbc.ModalFooter(
                    dbc.Button('Schließen', id='stats_runden_modal_close', color='primary', block=True)
                ), ], id='stats_runden_modal', size='xl', scrollable=True),
            dbc.Modal([
                dbc.ModalHeader(id='stats_all_modal_header'),
                dbc.ModalBody(html.Div(id='stats_all_modal_body')),
                dbc.ModalFooter(
                    dbc.Button('Schließen', id='stats_all_modal_close', color='primary', block=True)
                ), ], id='stats_all_modal', size='xl', scrollable=True),
        ]),
        dbc.Container([
            wrap_empty_dbc_row(),
            dbc.Row([
                wrap_dbc_col([
                    html.Div(
                        dbc.Row([
                            dbc.Col([
                                html.Div(html.H4('Statistiken'))
                            ])], justify='start'),
                    ),
                    dbc.Row([
                        dbc.Col([
                            wrap_dash_dropdown_div(form_text='Teilnehmer wählen', id='selected_teilnehmer_ids',
                                                   options=teilnehmers_options,
                                                   value=list({geber_id, ausspieler_id, mittelhand_id, hinterhand_id,
                                                               geberhand_id})),
                        ], xl=6, xs=12),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button('Statistiken gewählter Teilnehmer anzeigen',
                                       id='stats_teilnehmer_modal_open',
                                       color='primary', block=True),
                        ], xl=6, xs=12),
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col([
                            wrap_dash_dropdown_div(form_text='Runden wählen', id='selected_runden_ids',
                                                   options=[{'label': f'{r.datum.strftime("%d. %b %Y")} - {r.name} - '
                                                                      f'{r.ort}',
                                                             'value': f'{r.id}'} for r in get_runden()],
                                                   value=[runde_id]),
                        ], xl=6, xs=12),
                    ]),
                    html.Div(
                        dbc.Row([
                            dbc.Col([
                                dbc.Button('Statistiken gewählter Runden anzeigen',
                                           id='stats_runden_modal_open',
                                           color='primary', block=True),
                            ], xl=6, xs=12),
                        ])),
                    html.Br(),
                    html.Br(),
                    html.Div(
                        dbc.Row([
                            dbc.Col([
                                dbc.Button('Alle Statistiken anzeigen',
                                           id='stats_all_modal_open',
                                           color='primary', block=True),
                            ], xl=6, xs=12),
                        ])),
                ]),
            ]),
            wrap_footer_row()
        ]),
    ])
