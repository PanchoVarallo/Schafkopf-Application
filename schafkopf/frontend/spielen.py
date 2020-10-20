import dash_bootstrap_components as dbc
import dash_html_components as html

from schafkopf.database.queries import get_teilnehmer, \
    get_latest_einzelspiel_id, get_runde_id_by_einzelspiel_id, get_einzelspiele_by_einzelspiel_ids, get_runden
from schafkopf.frontend.generic_objects import wrap_empty_dbc_row, wrap_select_div, wrap_checklist_div, \
    wrap_footer_row


def wrap_spielen_layout():
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
            dbc.Modal([
                dbc.ModalHeader(id='rufspiel_stats_modal_header'),
                dbc.ModalBody(html.Div(id='rufspiel_stats_modal_body')),
                dbc.ModalFooter(
                    html.Div(id='rufspiel_stats_modal_close_button')
                ), ], id='rufspiel_spielstand_modal', size='xl', scrollable=True),
            dbc.Modal([
                dbc.ModalHeader(id='solo_stats_modal_header'),
                dbc.ModalBody(html.Div(id='solo_stats_modal_body')),
                dbc.ModalFooter(
                    html.Div(id='solo_stats_modal_close_button')
                ), ], id='solo_spielstand_modal', size='xl', scrollable=True),
            dbc.Modal([
                dbc.ModalHeader(id='hochzeit_stats_modal_header'),
                dbc.ModalBody(html.Div(id='hochzeit_stats_modal_body')),
                dbc.ModalFooter(
                    html.Div(id='hochzeit_stats_modal_close_button')
                ), ], id='hochzeit_spielstand_modal', size='xl', scrollable=True),
            dbc.Modal([
                dbc.ModalHeader(id='ramsch_stats_modal_header'),
                dbc.ModalBody(html.Div(id='ramsch_stats_modal_body')),
                dbc.ModalFooter(
                    html.Div(id='ramsch_stats_modal_close_button')
                ), ], id='ramsch_spielstand_modal', size='xl', scrollable=True),
        ]),
        dbc.Container([
            wrap_empty_dbc_row(),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            html.Div(html.H4('Spielen'))
                        ])], justify='start'),
                    dbc.Row([
                        dbc.Col([
                            wrap_select_div(form_text='Runde', id='runde_id',
                                            options=[{'label': f'{r.datum.strftime("%d. %b %Y")} - {r.name} - '
                                                               f'{r.ort}',
                                                      'value': f'{r.id}'} for r in get_runden()],
                                            value=runde_id),
                        ], xl=12, xs=12)]),
                    wrap_empty_dbc_row(),
                    dbc.Row([
                        dbc.Col([
                            wrap_select_div(form_text='Geber', id='geber_id',
                                            options=teilnehmers_options,
                                            value=geber_id
                                            ),
                        ], xl=10, xs=10)]),
                    wrap_empty_dbc_row(),
                    dbc.Row([
                        dbc.Col([
                            wrap_select_div(form_text='Ausspieler', id='ausspieler_id',
                                            options=teilnehmers_options,
                                            value=ausspieler_id
                                            ),
                        ], xl=10, xs=10),
                        dbc.Col([
                            wrap_checklist_div(form_text='Gelegt', id='gelegt_ausspieler_id',
                                               options=[{'label': '', 'value': 1}],
                                               value=[]),
                        ], xl=2, xs=2)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            wrap_select_div(form_text='Mittelhand', id='mittelhand_id',
                                            options=teilnehmers_options,
                                            value=mittelhand_id
                                            ),
                        ], xl=10, xs=10),
                        dbc.Col([
                            wrap_checklist_div(form_text='Gelegt', id='gelegt_mittelhand_id',
                                               options=[{'label': '', 'value': 1}],
                                               value=[]),
                        ], xl=2, xs=2)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            wrap_select_div(form_text='Hinterhand', id='hinterhand_id',
                                            options=teilnehmers_options,
                                            value=hinterhand_id
                                            ),
                        ], xl=10, xs=10),
                        dbc.Col([
                            wrap_checklist_div(form_text='Gelegt', id='gelegt_hinterhand_id',
                                               options=[{'label': '', 'value': 1}],
                                               value=[]),
                        ], xl=2, xs=2)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            wrap_select_div(form_text='Geberhand', id='geberhand_id',
                                            options=teilnehmers_options,
                                            value=geberhand_id
                                            ),
                        ], xl=10, xs=10),
                        dbc.Col([
                            wrap_checklist_div(form_text='Gelegt', id='gelegt_geberhand_id',
                                               options=[{'label': '', 'value': 1}],
                                               value=[]),
                        ], xl=2, xs=2)
                    ]),
                ], xs=12, xl=4),
                # ]),
                # wrap_empty_dbc_row(),
                # dbc.Row([
                dbc.Col([html.Div([dbc.Tabs([
                    dbc.Tab(tab_id='rufspiel_tab', label='Rufspiel'),
                    dbc.Tab(tab_id='solo_tab', label='Solo'),
                    dbc.Tab(tab_id='hochzeit_tab', label='Hochzeit'),
                    dbc.Tab(tab_id='ramsch_tab', label='Ramsch')],
                    id='tabs', active_tab='rufspiel_tab'),
                    html.Div(id='tab_content')])
                ], xs=12, xl=8)
            ]),
            wrap_footer_row()
        ]),
    ])
