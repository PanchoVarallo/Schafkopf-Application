from typing import List, Dict, Union, Tuple

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

from schafkopf.database.analyzer import get_ranking_dataframe_by_runde_ids, get_stats_dataframe_by_runde_ids, \
    get_list_dataframe_by_runde_ids
from schafkopf.database.data_model import Farbgebung, Spielart
from schafkopf.database.queries import get_einzelspiel_ids_by_runde_id, get_teilnehmers_by_ids


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


def wrap_punkte_div(spieler_nichtspieler_id: str,
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
        dbc.CardBody([dbc.Row([dbc.Col([html.Div(dbc.Alert(m, color='warning'))])]) for m in messages]),
        className='mt-3')
    ])


def wrap_stats(runde_ids: Union[None, List[str]]) -> Tuple[html.Div, html.Div]:
    runde_ids = [int(r) for r in runde_ids if r is not None]
    if len(runde_ids) == 0:
        header = html.Div()
        body = wrap_alert(['Bitte wählen Sie eine Runde'])
    else:
        anzahl_einzelspiele = len(get_einzelspiel_ids_by_runde_id(runde_ids))
        if anzahl_einzelspiele == 0:
            header = html.Div()
            body = wrap_alert(['Keine Spiele gespielt'])
        else:
            body = _build_body(runde_ids)
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
                wrap_checklist_div(form_text='Gelegt', id='rufspiel_gelegt_ids', options=teilnehmers_options)
            ]),
            wrap_dbc_col([
                wrap_checklist_div(form_text='Kontriert', id='rufspiel_kontriert_id', options=teilnehmers_options)
            ]),
            wrap_dbc_col([
                wrap_checklist_div(form_text='Re', id='rufspiel_re_id', options=teilnehmers_options)
            ]),
        ]),
        wrap_empty_dbc_row(),
        dbc.Row([
            wrap_dbc_col([
                wrap_radioitem_div(form_text='Ansager', id='rufspiel_ansager_id', options=teilnehmers_options)
            ]),
            wrap_dbc_col([
                wrap_radioitem_div(form_text='Rufsau', id='rufspiel_rufsau', options=farb_options)
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
                wrap_punkte_div(spieler_nichtspieler_id='rufspiel_spieler_nichtspieler_augen',
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
                wrap_checklist_div(form_text='Gelegt', id='solo_gelegt_ids', options=teilnehmers_options)
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
            wrap_dbc_col([
                wrap_radioitem_div(form_text='Ansager', id='solo_ansager_id', options=teilnehmers_options)
            ]),
            wrap_dbc_col([
                wrap_radioitem_div(form_text='Solo', id='solo_spielart', options=soli_options)
            ]),
            wrap_dbc_col([
                wrap_checklist_div(form_text='Farbe', id='solo_farbe', options=farb_options)
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
                wrap_punkte_div(spieler_nichtspieler_id='solo_spieler_nichtspieler_augen',
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


def wrap_next_game_button() -> html.Div:
    txt = 'Zum nächsten Spiel'
    return html.Div(html.A(dbc.Button(txt, color='primary', id='close', className='ml-auto'), href='/'))


def _build_body(runde_ids: List[int]):
    ranking_dataframe = get_ranking_dataframe_by_runde_ids(runde_ids)
    list_dataframe = get_list_dataframe_by_runde_ids(runde_ids)
    ranking_div = wrap_dataframe_table_div(ranking_dataframe)
    ranking_div = html.Div([html.H5('Punktestand'), ranking_div])
    spieler, partner, gegenspieler, verdopplungen = get_stats_dataframe_by_runde_ids(runde_ids)
    spieler_div = html.Div([html.H5('Statistiken als Spieler'), wrap_dataframe_table_div(spieler)])
    partner_div = html.Div([html.H5('Statistiken als Partner'), wrap_dataframe_table_div(partner)])
    gegenspieler_div = html.Div([html.H5('Statistiken als Gegenspieler'), wrap_dataframe_table_div(gegenspieler)])
    verdopplungen_div = html.Div([html.H5('Statistiken der Aggressivität'), wrap_dataframe_table_div(verdopplungen)])
    fig = px.line(list_dataframe, x='Einzelspiele', y='Punkte', color='Teilnehmer')
    graph_div = html.Div([html.H5('Verlauf des Punktestands'), html.Div(dbc.Row(dbc.Col(dcc.Graph(figure=fig))))])
    return html.Div([ranking_div, graph_div, spieler_div, partner_div, gegenspieler_div, verdopplungen_div])
