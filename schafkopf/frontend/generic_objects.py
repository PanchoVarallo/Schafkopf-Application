from typing import List, Dict, Union, Tuple

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

from schafkopf.database.analyzer import get_ranking_dataframe_by_runde_ids, get_list_dataframe_by_einzelspiele_ids, \
    get_stats_by_einzelspiel_ids
from schafkopf.database.data_model import Farbgebung, Spielart
from schafkopf.database.queries import get_einzelspiel_ids_by_runde_ids, get_teilnehmers_by_ids, get_teilnehmer, \
    get_latest_einzelspiel_id, get_runde_id_by_einzelspiel_id, get_einzelspiele_by_einzelspiel_ids, get_runden, \
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


def wrap_alert(messages: List[str]) -> html.Div:
    return html.Div([dbc.Card(
        dbc.CardBody([dbc.Row([dbc.Col([html.Div(dbc.Alert(m, color='info'))])]) for m in messages]),
        className='mt-3')
    ])


def wrap_stats_by_teilnehmer_ids(teilnehmer_ids: Union[None, List[str]],
                                 details: bool = False) -> Tuple[html.Div, html.Div]:
    teilnehmer_ids = [int(t) for t in teilnehmer_ids if t is not None]
    einzelspiel_ids = [e.id for e in get_einzelspiele_by_teilnehmer_ids(teilnehmer_ids)]
    return _wrap_stats_by_einzelspiele_ids(einzelspiel_ids, details)


def _wrap_stats_by_einzelspiele_ids(einzelspiel_ids: Union[None, List[int]],
                                    details: bool = False) -> Tuple[html.Div, html.Div]:
    if len(einzelspiel_ids) == 0:
        header = html.Div()
        body = wrap_alert(['Keine Spiele gespielt'])
    else:
        body = _build_body(einzelspiel_ids, details)
        header = html.Div([f'Statistiken'])
    return header, body


def wrap_stats_by_runde_ids(runde_ids: Union[None, List[str]], details: bool = False) -> Tuple[html.Div, html.Div]:
    runde_ids = [int(r) for r in runde_ids if r is not None]
    if len(runde_ids) == 0:
        header = html.Div()
        body = wrap_alert(['Bitte wählen Sie mindestens eine Runde'])
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
    teilnehmers_options = [{'label': f'{t.name}', 'value': t.id} for t in teilnehmers]
    farb_options = []
    for f in Farbgebung:
        if f == Farbgebung.HERZ:
            farb_options.append({'label': f'{f.name.lower().capitalize()}', 'value': f'{f.name}', 'disabled': True})
        else:
            farb_options.append({'label': f'{f.name.lower().capitalize()}', 'value': f'{f.name}'})
    card = dbc.Card(dbc.CardBody([
        dbc.Row([
            wrap_dbc_col([
                wrap_radioitem_div(form_text='Ansager', id='rufspiel_ansager_id', options=teilnehmers_options)
            ]),
            wrap_dbc_col([
                wrap_radioitem_div(form_text='Rufsau', id='rufspiel_rufsau', options=farb_options)
            ]),
            wrap_dbc_col([
                wrap_checklist_div(form_text='Kontriert', id='rufspiel_kontriert_id', options=teilnehmers_options)
            ]),
            wrap_dbc_col([
                wrap_checklist_div(form_text='Re', id='rufspiel_re_id', options=teilnehmers_options)
            ]),
            wrap_dbc_col([
                wrap_radioitem_div(form_text='Partner', id='rufspiel_partner_id', options=teilnehmers_options)
            ]),
        ]),
        wrap_empty_dbc_row(),
        dbc.Row([
            dbc.Col([
                wrap_laufende_div(form_text='Laufende', laufende_id='rufspiel_laufende')],
                width={'size': 6, 'offset': 3})
        ]),
        wrap_empty_dbc_row(),
        dbc.Row([
            dbc.Col([
                wrap_augen_div(spieler_nichtspieler_id='rufspiel_spieler_nichtspieler_augen',
                               augen_id='rufspiel_augen', schwarz_id='rufspiel_schwarz')],
                width={'size': 6, 'offset': 3}),
        ]),
        wrap_empty_dbc_row(),
        dbc.Row([
            dbc.Col([
                html.Div(id='rufspiel_validierung_content'), ], width={'size': 6, 'offset': 3}),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(
                    dbc.Button('Spiel eintragen', id='rufspiel_spielstand_eintragen_button',
                               color='primary', block=True)),
            ], width={'size': 6, 'offset': 3}),
        ])
    ]), className='mt-3')
    return card


def wrap_solo_card(ausspieler_id: str, mittelhand_id: str, hinterhand_id: str, geberhand_id: str) -> dbc.Card:
    teilnehmer_ids = [int(ausspieler_id), int(mittelhand_id), int(hinterhand_id), int(geberhand_id)]
    teilnehmers = [get_teilnehmers_by_ids([teilnehmer_id])[0] for teilnehmer_id in teilnehmer_ids]
    teilnehmers_options = [{'label': f'{t.name}', 'value': t.id} for t in teilnehmers]
    farb_options = [{'label': f'{f.name.lower().capitalize()}', 'value': f'{f.name}'} for f in Farbgebung]
    soli_options = [{'label': f'{f.name.lower().capitalize()}', 'value': f'{f.name}'} for f in Spielart if
                    f.value in [2, 3, 4]]
    card = dbc.Card(dbc.CardBody([
        dbc.Row([
            wrap_dbc_col([
                wrap_radioitem_div(form_text='Ansager', id='solo_ansager_id', options=teilnehmers_options)
            ]),
            wrap_dbc_col([
                wrap_radioitem_div(form_text='Solo', id='solo_spielart', options=soli_options)
            ]),
            wrap_dbc_col([
                wrap_checklist_div(form_text='Farbe', id='solo_farbe', options=farb_options)
            ]),
            wrap_dbc_col([
                wrap_checklist_div(form_text='Kontriert', id='solo_kontriert_id', options=teilnehmers_options)
            ]),
            wrap_dbc_col([
                wrap_checklist_div(form_text='Re', id='solo_re_id', options=teilnehmers_options)
            ]),
        ]),
        wrap_empty_dbc_row(),
        dbc.Row([
            dbc.Col([
                wrap_tout(tout_id='solo_tout')], width={'size': 6, 'offset': 3})
        ]),
        wrap_empty_dbc_row(),
        dbc.Row([
            dbc.Col([
                wrap_laufende_div(form_text='Laufende', laufende_id='solo_laufende')],
                width={'size': 6, 'offset': 3})
        ]),
        wrap_empty_dbc_row(),
        dbc.Row([
            dbc.Col([
                wrap_augen_div(spieler_nichtspieler_id='solo_spieler_nichtspieler_augen',
                               augen_id='solo_augen', schwarz_id='solo_schwarz')],
                width={'size': 6, 'offset': 3}),
        ]),
        wrap_empty_dbc_row(),
        dbc.Row([
            dbc.Col([
                html.Div(id='solo_validierung_content'), ], width={'size': 6, 'offset': 3}),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(
                    dbc.Button('Spiel eintragen', id='solo_spielstand_eintragen_button',
                               color='primary', block=True)),
            ], width={'size': 6, 'offset': 3}),
        ])
    ]), className='mt-3')
    return card


def wrap_hochzeit_card(ausspieler_id: str, mittelhand_id: str, hinterhand_id: str, geberhand_id: str) -> dbc.Card:
    teilnehmer_ids = [int(ausspieler_id), int(mittelhand_id), int(hinterhand_id), int(geberhand_id)]
    teilnehmers = [get_teilnehmers_by_ids([teilnehmer_id])[0] for teilnehmer_id in teilnehmer_ids]
    teilnehmers_options = [{'label': f'{t.name}', 'value': t.id} for t in teilnehmers]
    farb_options = []
    for f in Farbgebung:
        if f == Farbgebung.HERZ:
            farb_options.append({'label': f'{f.name.lower().capitalize()}', 'value': f'{f.name}', 'disabled': True})
        else:
            farb_options.append({'label': f'{f.name.lower().capitalize()}', 'value': f'{f.name}'})
    card = dbc.Card(dbc.CardBody([
        dbc.Row([
            wrap_dbc_col([
                wrap_radioitem_div(form_text='Hochzeitsanbieter', id='hochzeit_partner_id',
                                   options=teilnehmers_options)
            ]),
            wrap_dbc_col([
                wrap_radioitem_div(form_text='Hochzeitsannehmer', id='hochzeit_ansager_id',
                                   options=teilnehmers_options)
            ]),
            wrap_dbc_col([
                wrap_checklist_div(form_text='Kontriert', id='hochzeit_kontriert_id', options=teilnehmers_options)
            ]),
            wrap_dbc_col([
                wrap_checklist_div(form_text='Re', id='hochzeit_re_id', options=teilnehmers_options)
            ]),
        ]),
        wrap_empty_dbc_row(),
        dbc.Row([
            dbc.Col([
                wrap_laufende_div(form_text='Laufende', laufende_id='hochzeit_laufende')],
                width={'size': 6, 'offset': 3})
        ]),
        wrap_empty_dbc_row(),
        dbc.Row([
            dbc.Col([
                wrap_augen_div(spieler_nichtspieler_id='hochzeit_spieler_nichtspieler_augen',
                               augen_id='hochzeit_augen', schwarz_id='hochzeit_schwarz')],
                width={'size': 6, 'offset': 3}),
        ]),
        wrap_empty_dbc_row(),
        dbc.Row([
            dbc.Col([
                html.Div(id='hochzeit_validierung_content'), ], width={'size': 6, 'offset': 3}),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(
                    dbc.Button('Spiel eintragen', id='hochzeit_spielstand_eintragen_button',
                               color='primary', block=True)),
            ], width={'size': 6, 'offset': 3}),
        ])
    ]), className='mt-3')
    return card


def wrap_ramsch_card(ausspieler_id: str, mittelhand_id: str, hinterhand_id: str, geberhand_id: str) -> dbc.Card:
    teilnehmer_ids = [int(ausspieler_id), int(mittelhand_id), int(hinterhand_id), int(geberhand_id)]
    teilnehmers = [get_teilnehmers_by_ids([teilnehmer_id])[0] for teilnehmer_id in teilnehmer_ids]
    teilnehmers_options = [{'label': f'{t.name}', 'value': t.id} for t in teilnehmers]
    card = dbc.Card(dbc.CardBody([
        dbc.Row([
            wrap_dbc_col([
                wrap_checklist_div(form_text='Jungfrau', id='ramsch_jungfrau_ids', options=teilnehmers_options)
            ]),
            wrap_dbc_col([
                wrap_checklist_div(form_text='Bei Punktgleichheit Verlierer manuell angeben.',
                                   id='ramsch_manuelle_verlierer_ids', options=teilnehmers_options)
            ])
        ]),
        wrap_empty_dbc_row(),
        dbc.Row([
            dbc.Col([wrap_ramsch_augen_div(augen_id='ramsch_ausspieler_augen', teilnehmer_name=teilnehmers[0].name)],
                    width={'size': 6, 'offset': 3}),
        ]),
        dbc.Row([
            dbc.Col([wrap_ramsch_augen_div(augen_id='ramsch_mittelhand_augen', teilnehmer_name=teilnehmers[1].name)],
                    width={'size': 6, 'offset': 3}),
        ]),
        dbc.Row([
            dbc.Col([wrap_ramsch_augen_div(augen_id='ramsch_hinterhand_augen', teilnehmer_name=teilnehmers[2].name)],
                    width={'size': 6, 'offset': 3}),
        ]),
        dbc.Row([
            dbc.Col([wrap_ramsch_augen_div(augen_id='ramsch_geberhand_augen', teilnehmer_name=teilnehmers[3].name)],
                    width={'size': 6, 'offset': 3}),
        ]),
        wrap_empty_dbc_row(),
        dbc.Row([
            dbc.Col([
                html.Div(id='ramsch_validierung_content'), ], width={'size': 6, 'offset': 3}),
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(
                    dbc.Button('Spiel eintragen', id='ramsch_spielstand_eintragen_button',
                               color='primary', block=True)),
            ], width={'size': 6, 'offset': 3}),
        ])
    ]), className='mt-3')
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


def wrap_initial_layout():
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
                dbc.ModalHeader(id='rufspiel_stats_modal_header'),
                dbc.ModalBody(html.Div(id='rufspiel_stats_modal_body')),
                dbc.ModalFooter(
                    html.Div(id='rufspiel_stats_modal_close_button')
                ), ], id='rufspiel_spielstand_modal', size="xl", scrollable=True),
            dbc.Modal([
                dbc.ModalHeader(id='solo_stats_modal_header'),
                dbc.ModalBody(html.Div(id='solo_stats_modal_body')),
                dbc.ModalFooter(
                    html.Div(id='solo_stats_modal_close_button')
                ), ], id='solo_spielstand_modal', size="xl", scrollable=True),
            dbc.Modal([
                dbc.ModalHeader(id='hochzeit_stats_modal_header'),
                dbc.ModalBody(html.Div(id='hochzeit_stats_modal_body')),
                dbc.ModalFooter(
                    html.Div(id='hochzeit_stats_modal_close_button')
                ), ], id='hochzeit_spielstand_modal', size="xl", scrollable=True),
            dbc.Modal([
                dbc.ModalHeader(id='ramsch_stats_modal_header'),
                dbc.ModalBody(html.Div(id='ramsch_stats_modal_body')),
                dbc.ModalFooter(
                    html.Div(id='ramsch_stats_modal_close_button')
                ), ], id='ramsch_spielstand_modal', size="xl", scrollable=True),
            dbc.Modal([
                dbc.ModalHeader(id='stats_teilnehmer_modal_header'),
                dbc.ModalBody(html.Div(id='stats_teilnehmer_modal_body')),
                dbc.ModalFooter(
                    dbc.Button('Schließen', id='stats_teilnehmer_modal_close', color='primary', block=True)
                ), ], id='stats_teilnehmer_modal', size="xl", scrollable=True),
            dbc.Modal([
                dbc.ModalHeader(id='stats_runden_modal_header'),
                dbc.ModalBody(html.Div(id='stats_runden_modal_body')),
                dbc.ModalFooter(
                    dbc.Button('Schließen', id='stats_runden_modal_close', color='primary', block=True)
                ), ], id='stats_runden_modal', size="xl", scrollable=True),
            dbc.Modal([
                dbc.ModalHeader(id='stats_all_modal_header'),
                dbc.ModalBody(html.Div(id='stats_all_modal_body')),
                dbc.ModalFooter(
                    dbc.Button('Schließen', id='stats_all_modal_close', color='primary', block=True)
                ), ], id='stats_all_modal', size="xl", scrollable=True),
        ]),
        dbc.Container([
            wrap_empty_dbc_row(),
            dbc.Row([html.Div(html.H1('Digitale Schafkopfliste'))], justify='center'),

            dbc.Row([
                wrap_dbc_col([
                    dbc.Row([
                        dbc.Col([
                            wrap_select_div(form_text='Runde', id='runde_id',
                                            options=[{'label': f'{r.datum.strftime("%d. %b %Y")} - {r.name} - '
                                                               f'{r.ort}',
                                                      'value': f'{r.id}'} for r in get_runden()],
                                            value=runde_id),
                        ], width=9)]),
                    wrap_empty_dbc_row(),
                    dbc.Row([
                        dbc.Col([
                            wrap_select_div(form_text='Geber', id='geber_id',
                                            options=teilnehmers_options,
                                            value=geber_id
                                            ),
                        ], width=9)]),
                    wrap_empty_dbc_row(),
                    dbc.Row([
                        dbc.Col([
                            wrap_select_div(form_text='Ausspieler', id='ausspieler_id',
                                            options=teilnehmers_options,
                                            value=ausspieler_id
                                            ),
                        ], width=9),
                        dbc.Col([
                            wrap_checklist_div(form_text='Gelegt', id='gelegt_ausspieler_id',
                                               options=[{'label': '', 'value': 1}],
                                               value=[]),
                        ], width=3)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            wrap_select_div(form_text='Mittelhand', id='mittelhand_id',
                                            options=teilnehmers_options,
                                            value=mittelhand_id
                                            ),
                        ], width=9),
                        dbc.Col([
                            wrap_checklist_div(form_text='Gelegt', id='gelegt_mittelhand_id',
                                               options=[{'label': '', 'value': 1}],
                                               value=[]),
                        ], width=3)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            wrap_select_div(form_text='Hinterhand', id='hinterhand_id',
                                            options=teilnehmers_options,
                                            value=hinterhand_id
                                            ),
                        ], width=9),
                        dbc.Col([
                            wrap_checklist_div(form_text='Gelegt', id='gelegt_hinterhand_id',
                                               options=[{'label': '', 'value': 1}],
                                               value=[]),
                        ], width=3)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            wrap_select_div(form_text='Geberhand', id='geberhand_id',
                                            options=teilnehmers_options,
                                            value=geberhand_id
                                            ),
                        ], width=9),
                        dbc.Col([
                            wrap_checklist_div(form_text='Gelegt', id='gelegt_geberhand_id',
                                               options=[{'label': '', 'value': 1}],
                                               value=[]),
                        ], width=3)
                    ]),
                ]),
                wrap_dbc_col([wrap_dash_dropdown_div(form_text='Gewählte Spieler', id='selected_teilnehmer_ids',
                                                     options=teilnehmers_options,
                                                     value=list({geber_id, ausspieler_id, mittelhand_id, hinterhand_id,
                                                                 geberhand_id})),
                              html.Div(
                                  dbc.Row([
                                      dbc.Col([
                                          dbc.Button('Statistiken gewählter Spieler anzeigen',
                                                     id='stats_teilnehmer_modal_open',
                                                     color='primary', block=True),
                                      ]),
                                      dbc.Col([
                                          dbc.Button('Daten gewählter Spieler runterladen',
                                                     id='stats_teilnehmer_download',
                                                     color='primary', block=True, disabled=True),
                                      ]),
                                  ])),
                              html.Br(),
                              wrap_dash_dropdown_div(form_text='Gewählte Runden', id='selected_runden_ids',
                                                     options=[{'label': f'{r.datum.strftime("%d. %b %Y")} - {r.name} - '
                                                                        f'{r.ort}',
                                                               'value': f'{r.id}'} for r in get_runden()],
                                                     value=[runde_id]),
                              html.Div(
                                  dbc.Row([
                                      dbc.Col([
                                          dbc.Button('Statistiken gewählter Runden anzeigen',
                                                     id='stats_runden_modal_open',
                                                     color='primary', block=True),
                                      ]),
                                      dbc.Col([
                                          dbc.Button('Daten gewählter Runden runterladen', id='stats_runden_download',
                                                     color='primary', block=True, disabled=True),
                                      ]),
                                  ])),
                              html.Br(),
                              html.Br(),
                              html.Div(
                                  dbc.Row([
                                      dbc.Col([
                                          dbc.Button('Alle Statistiken anzeigen',
                                                     id='stats_all_modal_open',
                                                     color='primary', block=True),
                                      ]),
                                      dbc.Col([
                                          dbc.Button('Alle Daten runterladen', id='stats_all_download',
                                                     color='primary', block=True, disabled=True),
                                      ]),
                                  ])),
                              ]),
            ]),
            wrap_empty_dbc_row(),
            dbc.Row([
                wrap_dbc_col([html.Div([dbc.Tabs([
                    dbc.Tab(tab_id='rufspiel_tab', label='Rufspiel'),
                    dbc.Tab(tab_id='solo_tab', label='Solo'),
                    dbc.Tab(tab_id='hochzeit_tab', label='Hochzeit'),
                    dbc.Tab(tab_id='ramsch_tab', label='Ramsch')],
                    id='tabs', active_tab='rufspiel_tab'),
                    html.Div(id='tab_content')])])
            ]),
            dbc.Row([
                wrap_dbc_col([
                    html.Div(
                        html.Footer('\u00a9 2020 - Mathias Sirvent', style={'textAlign': 'center'})
                    )])
            ])
        ]),
    ])
