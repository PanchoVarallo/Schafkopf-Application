from typing import List, Dict, Union, Tuple

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

from schafkopf.database.analyzer import get_ranking_dataframe_by_runde_ids, get_list_dataframe_by_einzelspiele_ids, \
    get_stats_by_einzelspiel_ids
from schafkopf.database.data_model import Farbgebung, Spielart
from schafkopf.database.queries import get_einzelspiel_ids_by_runde_ids, get_teilnehmers_by_ids, \
    get_einzelspiele_by_teilnehmer_ids


def wrap_empty_dbc_row() -> dbc.Row:
    return dbc.Row([html.Div(html.Br())])


def wrap_dbc_col(div: List[html.Div]) -> dbc.Col:
    return dbc.Col(div)


def wrap_html_tr(entries: List[str]) -> html.Tr:
    return html.Tr([html.Td(e) for e in entries])


def wrap_html_tbody(entries: List[html.Tr]) -> html.Tbody:
    return html.Tbody(entries)


def wrap_divs(divs: List[html.Div]) -> html.Div:
    return html.Div(dbc.Row(dbc.Col([html.Div(divs)])))


def wrap_select_div(form_text: str,
                    id: str,
                    options: List[Dict],
                    value: Union[None, str] = None) -> html.Div:
    return html.Div(
        dbc.FormGroup([
            dbc.FormText(form_text),
            dbc.Select(
                id=id,
                options=options,
                value=value
            ),
        ])
    )


def wrap_dash_dropdown_div(form_text: str,
                           id: str,
                           options: List[Dict],
                           multi: bool = True,
                           value: Union[None, int, List[int]] = None) -> html.Div:
    # This is just used once because this kind of multi dropdown does not exist in dbc.
    # Unfortunately I have to adjust the style manually ... at least the color
    return html.Div(
        dbc.FormGroup([
            dbc.FormText(form_text),
            dcc.Dropdown(
                id=id,
                options=options,
                value=value,
                multi=multi,
                placeholder='',
                style={'color': 'black'}
            ),
        ])
    )


def wrap_checklist_div(form_text: str,
                       id: str,
                       options: List[Dict],
                       switch: bool = True,
                       value: List[int] = []) -> html.Div:
    return html.Div(
        dbc.FormGroup([
            dbc.FormText(form_text),
            dbc.Checklist(
                id=id,
                options=options,
                value=value,
                switch=switch
            )
        ])
    )


def wrap_radioitem_div(form_text: str,
                       id: str,
                       options: List[Dict],
                       switch: bool = True,
                       value: Union[int, str] = None) -> html.Div:
    return html.Div(
        dbc.FormGroup([
            dbc.FormText(form_text),
            dbc.RadioItems(
                id=id,
                options=options,
                value=value,
                switch=switch
            )
        ])
    )


def wrap_laufende_div(form_text: str,
                      laufende_id: str) -> html.Div:
    return html.Div([
        dbc.FormGroup([
            dbc.FormText(form_text),
            html.Div(
                [
                    dbc.Input(
                        id=laufende_id,
                        type='number', min=0, max=8, step=1, value=0),
                ],
                id='styled-numeric-input',
            )
        ])
    ])


def wrap_augen_div(spieler_nichtspieler_id: str,
                   augen_id: str,
                   schwarz_id: str) -> html.Div:
    return html.Div([
        dbc.FormGroup([
            dbc.FormText('Augen'),
            dbc.RadioItems(
                id=spieler_nichtspieler_id,
                options=[{'label': l, 'value': v} for (l, v) in [('Spieler', 1), ('Nicht-Spieler', 0)]],
                switch=True,
                inline=True,
                value=1
            ),
            html.Div(
                [
                    dbc.Input(
                        id=augen_id,
                        type='number', min=0, max=120, step=1,
                        value=120
                    )
                ],
                id='styled-numeric-input',
            ),
            html.Div(
                dbc.RadioItems(
                    id=schwarz_id,
                    options=[{'label': 'Schwarz gespielt', 'value': 1},
                             {'label': 'Nicht Schwarz gespielt', 'value': 0}],
                    value=0,
                    switch=True
                )
            )
        ])
    ])


def wrap_ramsch_augen_div(augen_id: str, teilnehmer_name: str) -> html.Div:
    return html.Div([
        dbc.FormGroup([
            dbc.FormText(f'Augen von {teilnehmer_name}'),
            html.Div(
                [
                    dbc.Input(
                        id=augen_id,
                        type='number', min=0, max=120, step=1,
                        value=30
                    )
                ],
                id='styled-numeric-input',
            )
        ])
    ])


def wrap_tout(tout_id: str) -> html.Div:
    return html.Div([
        dbc.FormGroup([
            dbc.FormText('Tout'),
            dbc.Checklist(
                options=[
                    {'label': 'Tout gespielt und gewonnen', 'value': 0},
                    {'label': 'Tout gespielt und verloren', 'value': 1}
                ],
                value=[],
                id=tout_id,
                switch=True,
            )
        ])
    ])


def wrap_dataframe_table_div(dataframe: pd.DataFrame) -> html.Div:
    return html.Div([dbc.Table.from_dataframe(dataframe, striped=True, bordered=True, hover=True)])


def wrap_alert(messages: List[str]) -> dbc.Row:
    return dbc.Row([dbc.Col([html.Div(dbc.Alert(m, color='info'))], xl=6, xs=12) for m in messages])


def wrap_stats_by_teilnehmer_ids(teilnehmer_ids: Union[None, List[str]],
                                 details: bool = False) -> Tuple[html.Div, html.Div]:
    teilnehmer_ids = [int(t) for t in teilnehmer_ids if t is not None]
    einzelspiel_ids = [e.id for e in get_einzelspiele_by_teilnehmer_ids(teilnehmer_ids)]
    return _wrap_stats_by_einzelspiele_ids(einzelspiel_ids, details)


def _wrap_stats_by_einzelspiele_ids(einzelspiel_ids: Union[None, List[int]],
                                    details: bool = False) -> Tuple[html.Div, html.Div]:
    if len(einzelspiel_ids) == 0:
        header = html.Div()
        body = wrap_alert(['Keine Spiele vorhanden'])
    else:
        body = _build_body(einzelspiel_ids, details)
        header = html.Div([f'Statistiken'])
    return header, body


def wrap_stats_by_runde_ids(runde_ids: Union[None, List[str]], details: bool = False) -> Tuple[html.Div, html.Div]:
    runde_ids = [int(r) for r in runde_ids if r is not None]
    if len(runde_ids) == 0:
        header = html.Div()
        body = wrap_alert(['Keine Spiele vorhanden'])
    else:
        einzelspiel_ids = get_einzelspiel_ids_by_runde_ids(runde_ids=runde_ids)
        if len(einzelspiel_ids) == 0:
            header = html.Div()
            body = wrap_alert(['Keine Spiele in diesen Runden gespielt'])
        else:

            body = _build_body(einzelspiel_ids, details)
            header = html.Div([f'Statistiken'])
    return header, body


def wrap_rufspiel_card(ausspieler_id: str, mittelhand_id: str, hinterhand_id: str, geberhand_id: str) -> dbc.Card:
    teilnehmer_ids = [int(ausspieler_id), int(mittelhand_id), int(hinterhand_id), int(geberhand_id)]
    teilnehmers = [get_teilnehmers_by_ids([teilnehmer_id])[0] for teilnehmer_id in teilnehmer_ids]
    teilnehmers_options = [{'label': f'{t.vorname}', 'value': t.id} for t in teilnehmers]
    farb_options = []
    for f in Farbgebung:
        if f == Farbgebung.HERZ:
            farb_options.append({'label': f'{f.name.lower().capitalize()}', 'value': f'{f.name}', 'disabled': True})
        else:
            farb_options.append({'label': f'{f.name.lower().capitalize()}', 'value': f'{f.name}'})
    card = dbc.Card(dbc.CardBody([
        dbc.Row([
            dbc.Col([
                wrap_radioitem_div(form_text='Ansager', id='rufspiel_ansager_id', options=teilnehmers_options)
            ], xl=3, xs=6),
            dbc.Col([
                wrap_radioitem_div(form_text='Rufsau', id='rufspiel_rufsau', options=farb_options)
            ], xl=3, xs=6),
            dbc.Col([
                wrap_checklist_div(form_text='Kontriert', id='rufspiel_kontriert_id', options=teilnehmers_options)
            ], xl=3, xs=6),
            dbc.Col([
                wrap_checklist_div(form_text='Re', id='rufspiel_re_id', options=teilnehmers_options)
            ], xl=3, xs=6),
            dbc.Col([
                wrap_radioitem_div(form_text='Partner', id='rufspiel_partner_id', options=teilnehmers_options)
            ], xl=3, xs=6),
            dbc.Col([
                wrap_laufende_div(form_text='Laufende', laufende_id='rufspiel_laufende')],
                xl=3, xs=6),
            dbc.Col([
                wrap_augen_div(spieler_nichtspieler_id='rufspiel_spieler_nichtspieler_augen',
                               augen_id='rufspiel_augen', schwarz_id='rufspiel_schwarz')],
                xl=6, xs=12),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(id='rufspiel_validierung_content')
            ], xl=12, xs=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(
                    dbc.Button('Spiel eintragen', id='rufspiel_spielstand_eintragen_button',
                               color='primary', block=True)),
            ], xl=12, xs=12),
        ])
    ]))
    return card


def wrap_solo_card(ausspieler_id: str, mittelhand_id: str, hinterhand_id: str, geberhand_id: str) -> dbc.Card:
    teilnehmer_ids = [int(ausspieler_id), int(mittelhand_id), int(hinterhand_id), int(geberhand_id)]
    teilnehmers = [get_teilnehmers_by_ids([teilnehmer_id])[0] for teilnehmer_id in teilnehmer_ids]
    teilnehmers_options = [{'label': f'{t.vorname}', 'value': t.id} for t in teilnehmers]
    farb_options = [{'label': f'{f.name.lower().capitalize()}', 'value': f'{f.name}'} for f in Farbgebung]
    soli_options = [{'label': f'{f.name.lower().capitalize()}', 'value': f'{f.name}'} for f in Spielart if
                    f.value in [2, 3, 4]]
    card = dbc.Card(dbc.CardBody([
        dbc.Row([
            dbc.Col([
                wrap_radioitem_div(form_text='Ansager', id='solo_ansager_id', options=teilnehmers_options)
            ], xl=3, xs=6),
            dbc.Col([
                wrap_radioitem_div(form_text='Solo', id='solo_spielart', options=soli_options)
            ], xl=3, xs=6),
            dbc.Col([
                wrap_checklist_div(form_text='Farbe', id='solo_farbe', options=farb_options)
            ], xl=3, xs=6),
            dbc.Col([
                wrap_checklist_div(form_text='Kontriert', id='solo_kontriert_id', options=teilnehmers_options)
            ], xl=3, xs=6),
            dbc.Col([
                wrap_checklist_div(form_text='Re', id='solo_re_id', options=teilnehmers_options)
            ], xl=3, xs=6),
            dbc.Col([
                wrap_laufende_div(form_text='Laufende', laufende_id='solo_laufende')
            ], xl=3, xs=12),
            dbc.Col([
                wrap_tout(tout_id='solo_tout')
            ], xl=6, xs=6),
            dbc.Col([], xl=3, xs=0),
            dbc.Col([
                wrap_augen_div(spieler_nichtspieler_id='solo_spieler_nichtspieler_augen',
                               augen_id='solo_augen', schwarz_id='solo_schwarz')],
                xl=6, xs=12),
            dbc.Col([], xl=3, xs=0),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(id='solo_validierung_content')
            ], xl=12, xs=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(
                    dbc.Button('Spiel eintragen', id='solo_spielstand_eintragen_button',
                               color='primary', block=True)),
            ], xl=12, xs=12),
        ])
    ]))
    return card


def wrap_hochzeit_card(ausspieler_id: str, mittelhand_id: str, hinterhand_id: str, geberhand_id: str) -> dbc.Card:
    teilnehmer_ids = [int(ausspieler_id), int(mittelhand_id), int(hinterhand_id), int(geberhand_id)]
    teilnehmers = [get_teilnehmers_by_ids([teilnehmer_id])[0] for teilnehmer_id in teilnehmer_ids]
    teilnehmers_options = [{'label': f'{t.vorname}', 'value': t.id} for t in teilnehmers]
    farb_options = []
    for f in Farbgebung:
        if f == Farbgebung.HERZ:
            farb_options.append({'label': f'{f.name.lower().capitalize()}', 'value': f'{f.name}', 'disabled': True})
        else:
            farb_options.append({'label': f'{f.name.lower().capitalize()}', 'value': f'{f.name}'})
    card = dbc.Card(dbc.CardBody([
        dbc.Row([
            dbc.Col([
                wrap_radioitem_div(form_text='Hochzeitsanbieter', id='hochzeit_partner_id',
                                   options=teilnehmers_options)
            ], xl=3, xs=6),
            dbc.Col([
                wrap_radioitem_div(form_text='Hochzeitsannehmer', id='hochzeit_ansager_id',
                                   options=teilnehmers_options)
            ], xl=3, xs=6),
            dbc.Col([
                wrap_checklist_div(form_text='Kontriert', id='hochzeit_kontriert_id', options=teilnehmers_options)
            ], xl=3, xs=6),
            dbc.Col([
                wrap_checklist_div(form_text='Re', id='hochzeit_re_id', options=teilnehmers_options)
            ], xl=3, xs=6),
            dbc.Col([
                wrap_laufende_div(form_text='Laufende', laufende_id='hochzeit_laufende')
            ], xl=3, xs=12),
            dbc.Col([
                wrap_augen_div(spieler_nichtspieler_id='hochzeit_spieler_nichtspieler_augen',
                               augen_id='hochzeit_augen', schwarz_id='hochzeit_schwarz')
            ], xl=6, xs=12),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(id='hochzeit_validierung_content')
            ], xl=12, xs=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(
                    dbc.Button('Spiel eintragen', id='hochzeit_spielstand_eintragen_button',
                               color='primary', block=True)),
            ], xl=12, xs=12),
        ])
    ]))
    return card


def wrap_ramsch_card(ausspieler_id: str, mittelhand_id: str, hinterhand_id: str, geberhand_id: str) -> dbc.Card:
    teilnehmer_ids = [int(ausspieler_id), int(mittelhand_id), int(hinterhand_id), int(geberhand_id)]
    teilnehmers = [get_teilnehmers_by_ids([teilnehmer_id])[0] for teilnehmer_id in teilnehmer_ids]
    teilnehmers_options = [{'label': f'{t.vorname}', 'value': t.id} for t in teilnehmers]
    card = dbc.Card(dbc.CardBody([
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        wrap_checklist_div(form_text='Jungfrau', id='ramsch_jungfrau_ids', options=teilnehmers_options)
                    ], xl=6, xs=6),
                    dbc.Col([
                        wrap_checklist_div(form_text='Verlierer manuell angeben',
                                           id='ramsch_manuelle_verlierer_ids', options=teilnehmers_options)
                    ], xl=6, xs=6),
                ])], xl=6, xs=12),
            dbc.Col([
                dbc.Row([
                    dbc.Col(
                        [wrap_ramsch_augen_div(augen_id='ramsch_ausspieler_augen',
                                               teilnehmer_name=teilnehmers[0].vorname)
                         ], xl=6, xs=12),
                    dbc.Col(
                        [wrap_ramsch_augen_div(augen_id='ramsch_mittelhand_augen',
                                               teilnehmer_name=teilnehmers[1].vorname)
                         ], xl=6, xs=12),
                    dbc.Col(
                        [wrap_ramsch_augen_div(augen_id='ramsch_hinterhand_augen',
                                               teilnehmer_name=teilnehmers[2].vorname)
                         ], xl=6, xs=12),
                    dbc.Col(
                        [wrap_ramsch_augen_div(augen_id='ramsch_geberhand_augen',
                                               teilnehmer_name=teilnehmers[3].vorname)
                         ], xl=6, xs=12)
                ])
            ], xl=6, xs=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(id='ramsch_validierung_content')
            ], xl=12, xs=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(
                    dbc.Button('Spiel eintragen', id='ramsch_spielstand_eintragen_button',
                               color='primary', block=True)),
            ], xl=12, xs=12),
        ])
    ]))
    return card


def wrap_next_game_button() -> html.Div:
    txt = 'Zum nächsten Spiel'
    return html.Div(html.A(dbc.Button(txt, color='primary', id='close', className='ml-auto'), href='/'))


def _build_body(einzelspiele_ids: List[int], details: bool):
    ranking_dataframe = get_ranking_dataframe_by_runde_ids(einzelspiele_ids)
    list_dataframe = get_list_dataframe_by_einzelspiele_ids(einzelspiele_ids)
    ranking_div = wrap_dataframe_table_div(ranking_dataframe)
    ranking_div = html.Div([html.H5('Punktestand'), ranking_div])
    fig = px.line(list_dataframe, x='Einzelspiele', y='Punkte', color='Teilnehmer')
    graph_div = html.Div([html.H5('Verlauf des Punktestands'), html.Div(dbc.Row(dbc.Col(dcc.Graph(figure=fig))))])
    if details:
        spielstatistik, gewonnen, ansager, solo, partner, gegenspieler, ramschspieler, verdopplungen \
            = get_stats_by_einzelspiel_ids(einzelspiele_ids)
        spielstatistik_div = html.Div([html.H5('Statistiken der Spielarten'),
                                       wrap_dataframe_table_div(spielstatistik)])
        gewonnen_div = html.Div([html.H5('Teilnehmerstatistiken'),
                                 wrap_dataframe_table_div(gewonnen)])
        ansager_div = html.Div([html.H5('Teilnehmerstatistiken der Ansagen (Rufspiel, Hochzeit, Solo)'),
                                wrap_dataframe_table_div(ansager)])
        solo_div = html.Div([html.H5('Detailstatistik: Teilnehmerstatistiken der Solos (Farbsolo, Wenz, Geier)'),
                             wrap_dataframe_table_div(solo)])
        partner_div = html.Div([html.H5('Teilnehmerstatistiken der Partnerspiele (Rufspiel, Hochzeit)'),
                                wrap_dataframe_table_div(partner)])
        gegenspieler_div = html.Div([html.H5('Teilnehmerstatistiken der Gegenspiele (Rufspiel, Hochzeit, Solo)'),
                                     wrap_dataframe_table_div(gegenspieler)])
        ramschspieler_div = html.Div([html.H5('Teilnehmerstatistiken der Rämsche'),
                                      wrap_dataframe_table_div(ramschspieler)])
        verdopplungen_div = html.Div([html.H5('Teilnehmerstatistiken der Aggressivität'),
                                      wrap_dataframe_table_div(verdopplungen)])
        divs = [ranking_div, graph_div, spielstatistik_div, gewonnen_div, ansager_div, solo_div,
                partner_div, gegenspieler_div, ramschspieler_div, verdopplungen_div]
        return_divs = []
        for div in divs:
            return_divs.append(div)
            return_divs.append(wrap_empty_dbc_row())
        return html.Div(return_divs)
    return html.Div([ranking_div])


def wrap_footer_row():
    return dbc.Row([
        wrap_dbc_col([
            wrap_empty_dbc_row(),
            html.Div(
                html.Footer('\u00a9 2020 - Mathias Sirvent', style={'textAlign': 'center'})
            )])
    ])
