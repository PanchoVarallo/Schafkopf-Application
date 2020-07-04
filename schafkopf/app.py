# -*- coding: utf-8 -*-
import locale
from typing import List, Union, Dict, Tuple

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from schafkopf.backend.calculator import RufspielCalculator, SoloCalculator
from schafkopf.backend.configs import RufspielRawConfig, SoloRawConfig
from schafkopf.backend.validator import RufspielValidator, SoloValidator
from schafkopf.database.queries import get_runden, get_teilnehmer, get_latest_einzelspiel_id, \
    get_runde_id_by_einzelspiel_id, get_einzelspiele_by_einzelspiel_id
from schafkopf.database.writer import RufspielWriter
from schafkopf.frontend.generic_objects import wrap_alert, wrap_stats, wrap_rufspiel_card, \
    wrap_next_game_button, wrap_select_div, wrap_dbc_col, wrap_empty_dbc_row, wrap_solo_card
from schafkopf.frontend.presenter import RufspielPresenter, SoloPresenter


def wrap_initial_layout():
    teilnehmers_options = [{'label': f'{s.name}', 'value': f'{s.id}'} for s in get_teilnehmer()]
    einzelspiel_id = get_latest_einzelspiel_id()
    runde_id = get_runde_id_by_einzelspiel_id(einzelspiel_id)
    einzelspiel = get_einzelspiele_by_einzelspiel_id([einzelspiel_id])
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
            dcc.Store(id='stats_modal_open_n_clicks', data={'n_clicks': 0}),
            dcc.Store(id='stats_modal_close_n_clicks', data={'n_clicks': 0}),
            dcc.Store(id='stats_all_modal_open_n_clicks', data={'n_clicks': 0}),
            dcc.Store(id='stats_all_modal_close_n_clicks', data={'n_clicks': 0}),
            dbc.Modal([
                dbc.ModalHeader(id='rufspiel_stats_modal_header'),
                dbc.ModalBody(html.Div(id='rufspiel_stats_modal_body')),
                dbc.ModalFooter(
                    html.Div(id='rufspiel_stats_modal_close_button')
                ), ], id='rufspiel_spielstand_modal', size="xl"),
            dbc.Modal([
                dbc.ModalHeader(id='solo_stats_modal_header'),
                dbc.ModalBody(html.Div(id='solo_stats_modal_body')),
                dbc.ModalFooter(
                    html.Div(id='solo_stats_modal_close_button')
                ), ], id='solo_spielstand_modal', size="xl"),
            dbc.Modal([
                dbc.ModalHeader(id='hochzeit_stats_modal_header'),
                dbc.ModalBody(html.Div(id='hochzeit_stats_modal_body')),
                dbc.ModalFooter(
                    html.Div(id='hochzeit_stats_modal_close_button')
                ), ], id='hochzeit_spielstand_modal', size="xl"),
            dbc.Modal([
                dbc.ModalHeader(id='ramsch_stats_modal_header'),
                dbc.ModalBody(html.Div(id='ramsch_stats_modal_body')),
                dbc.ModalFooter(
                    html.Div(id='ramsch_stats_modal_close_button')
                ), ], id='ramsch_spielstand_modal', size="xl"),
            dbc.Modal([
                dbc.ModalHeader(id='stats_modal_header'),
                dbc.ModalBody(html.Div(id='stats_modal_body')),
                dbc.ModalFooter(
                    dbc.Button('Schließen', id='stats_modal_close', color='primary', block=True)
                ), ], id='stats_modal', size="xl"),
            dbc.Modal([
                dbc.ModalHeader(id='stats_all_modal_header'),
                dbc.ModalBody(html.Div(id='stats_all_modal_body')),
                dbc.ModalFooter(
                    dbc.Button('Schließen', id='stats_all_modal_close', color='primary', block=True)
                ), ], id='stats_all_modal', size="xl"),
        ]),
        dbc.Container([
            wrap_empty_dbc_row(),
            dbc.Row([html.Div(html.H1('Schafkopfliste'))], justify='center'),
            dbc.Row([
                wrap_dbc_col([wrap_select_div(form_text='Runde', id='runde_id',
                                              options=[{'label': f'{r.created_on.strftime("%d. %b %Y")} - {r.name} - '
                                                                 f'{r.ort}',
                                                        'value': f'{r.id}'} for r in get_runden()],
                                              value=runde_id),
                              html.Div(dbc.Button('Statistiken der Runde', id='stats_modal_open',
                                                  color='primary', block=True)),
                              html.Br(),
                              html.Div(dbc.Button('Statistiken aller Runden', id='stats_all_modal_open',
                                                  color='primary', block=True)),
                              ]),
                wrap_dbc_col([
                    wrap_select_div(form_text='Geber', id='geber_id',
                                    options=teilnehmers_options,
                                    value=geber_id
                                    ),
                    wrap_empty_dbc_row(),
                    wrap_select_div(form_text='Ausspieler', id='ausspieler_id',
                                    options=teilnehmers_options,
                                    value=ausspieler_id
                                    ),
                    wrap_select_div(form_text='Mittelhand', id='mittelhand_id',
                                    options=teilnehmers_options,
                                    value=mittelhand_id
                                    ),
                    wrap_select_div(form_text='Hinterhand', id='hinterhand_id',
                                    options=teilnehmers_options,
                                    value=hinterhand_id
                                    ),
                    wrap_select_div(form_text='Geberhand', id='geberhand_id',
                                    options=teilnehmers_options,
                                    value=geberhand_id
                                    ),
                ])
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


external_stylesheets = [dbc.themes.SANDSTONE]
locale.setlocale(locale.LC_TIME, 'de_DE.utf8')
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True
app.title = 'Schafkopfliste'
app.layout = wrap_initial_layout


@app.callback([Output('tab_content', 'children'),
               Output('rufspiel_stats_modal_close_button', 'children'),
               Output('solo_stats_modal_close_button', 'children'),
               Output('hochzeit_stats_modal_close_button', 'children'),
               Output('ramsch_stats_modal_close_button', 'children')],
              [Input('tabs', 'active_tab'),
               Input('runde_id', 'value'),
               Input('geber_id', 'value'),
               Input('ausspieler_id', 'value'),
               Input('mittelhand_id', 'value'),
               Input('hinterhand_id', 'value'),
               Input('geberhand_id', 'value')])
def switch_tab(active_tab: str,
               runde_id: Union[None, str],
               geber_id: Union[None, str],
               ausspieler_id: Union[None, str],
               mittelhand_id: Union[None, str],
               hinterhand_id: Union[None, str],
               geberhand_id: Union[None, str]) -> Tuple[dbc.Card, html.Div, html.Div, html.Div, html.Div]:
    validation_result = _validate_teilnehmer(runde_id, geber_id,
                                             [ausspieler_id, mittelhand_id, hinterhand_id, geberhand_id])
    if validation_result is not None:
        return validation_result, html.Div(), html.Div(), html.Div(), html.Div()
    if active_tab == 'rufspiel_tab':
        return wrap_rufspiel_card(ausspieler_id, mittelhand_id, hinterhand_id, geberhand_id), \
               wrap_next_game_button(), wrap_next_game_button(), wrap_next_game_button(), wrap_next_game_button()
    elif active_tab == 'solo_tab':
        return wrap_solo_card(ausspieler_id, mittelhand_id, hinterhand_id, geberhand_id), \
               wrap_next_game_button(), wrap_next_game_button(), wrap_next_game_button(), wrap_next_game_button()
    elif active_tab == 'hochzeit_tab':
        return dbc.Card(dbc.CardBody([
            html.P('This is Hochzeit!', className='card-text'),
            dbc.Button('Click here', color='success'),
        ]), className='mt-3'), html.Div(), html.Div(), html.Div(), html.Div()
    elif active_tab == 'ramsch_tab':
        return dbc.Card(dbc.CardBody([
            html.P('This is Ramsch!', className='card-text'),
            dbc.Button('Click here', color='success'),
        ]), className='mt-3'), html.Div(), html.Div(), html.Div(), html.Div()
    return html.P('This should not ever be displayed...')


@app.callback(
    [Output('rufspiel_validierung_content', 'children'),
     Output('rufspiel_spielstand_eintragen_button', 'style'),
     Output('rufspiel_stats_modal_header', 'children'),
     Output('rufspiel_stats_modal_body', 'children'),
     Output('rufspiel_spielstand_modal', 'is_open')],
    [Input('rufspiel_spielstand_eintragen_button', 'n_clicks'),
     Input('rufspiel_gelegt_ids', 'value'),
     Input('rufspiel_ansager_id', 'value'),
     Input('rufspiel_rufsau', 'value'),
     Input('rufspiel_kontriert_id', 'value'),
     Input('rufspiel_re_id', 'value'),
     Input('rufspiel_partner_id', 'value'),
     Input('rufspiel_laufende', 'value'),
     Input('rufspiel_spieler_nichtspieler_augen', 'value'),
     Input('rufspiel_augen', 'value'),
     Input('rufspiel_schwarz', 'value')],
    [State('runde_id', 'value'),
     State('geber_id', 'value'),
     State('ausspieler_id', 'value'),
     State('mittelhand_id', 'value'),
     State('hinterhand_id', 'value'),
     State('geberhand_id', 'value')])
def calculate_rufspiel(
        rufspiel_spielstand_eintragen_button_n_clicks: int,
        rufspiel_gelegt_ids: List[int],
        rufspiel_ansager_id: Union[None, int],
        rufspiel_rufsau: Union[None, str],
        rufspiel_kontriert_id: List[int],
        rufspiel_re_id: List[int],
        rufspiel_partner_id: Union[None, int],
        rufspiel_laufende: Union[None, int],
        rufspiel_spieler_nichtspieler_augen: Union[None, int],
        rufspiel_augen: Union[None, int],
        rufspiel_schwarz: Union[None, int],
        runde_id: Union[None, str],
        geber_id: Union[None, str],
        ausspieler_id: Union[None, str],
        mittelhand_id: Union[None, str],
        hinterhand_id: Union[None, str],
        geberhand_id: Union[None, str]) -> Tuple[Union[None, List[html.Div]], Dict, html.Div, html.Div, bool]:
    teilnehmer_ids = [ausspieler_id, mittelhand_id, hinterhand_id, geberhand_id]
    if _validate_teilnehmer(runde_id, geber_id, teilnehmer_ids) is not None:
        return None, dict(), html.Div(), html.Div(), False
    raw_config = RufspielRawConfig(runde_id=int(runde_id),
                                   geber_id=geber_id,
                                   teilnehmer_ids=[int(t) for t in teilnehmer_ids],
                                   gelegt_ids=rufspiel_gelegt_ids,
                                   ansager_id=rufspiel_ansager_id,
                                   rufsau=rufspiel_rufsau,
                                   kontriert_id=rufspiel_kontriert_id,
                                   re_id=rufspiel_re_id,
                                   partner_id=rufspiel_partner_id,
                                   laufende=rufspiel_laufende,
                                   spieler_nichtspieler_augen=rufspiel_spieler_nichtspieler_augen,
                                   augen=rufspiel_augen,
                                   schwarz=rufspiel_schwarz)
    rufspiel_validator = RufspielValidator(raw_config)
    messages = rufspiel_validator.validation_messages
    if len(messages) > 0:
        return wrap_alert(messages), dict(display='none'), html.Div(), html.Div(), False
    rufspiel_calculator = RufspielCalculator(rufspiel_validator.validated_config)
    result = RufspielPresenter(rufspiel_calculator).get_result()
    if rufspiel_spielstand_eintragen_button_n_clicks is not None and rufspiel_spielstand_eintragen_button_n_clicks >= 1:
        RufspielWriter(rufspiel_calculator).write()
        header, body = wrap_stats([runde_id])
        return result, dict(), header, body, True
    else:
        return result, dict(), html.Div(), html.Div(), False


@app.callback(
    [Output('solo_validierung_content', 'children'),
     Output('solo_spielstand_eintragen_button', 'style'),
     Output('solo_stats_modal_header', 'children'),
     Output('solo_stats_modal_body', 'children'),
     Output('solo_spielstand_modal', 'is_open')],
    [Input('solo_spielstand_eintragen_button', 'n_clicks'),
     Input('solo_gelegt_ids', 'value'),
     Input('solo_ansager_id', 'value'),
     Input('solo_spielart', 'value'),
     Input('solo_kontriert_id', 'value'),
     Input('solo_re_id', 'value'),
     Input('solo_farbe', 'value'),
     Input('solo_tout', 'value'),
     Input('solo_laufende', 'value'),
     Input('solo_spieler_nichtspieler_augen', 'value'),
     Input('solo_augen', 'value'),
     Input('solo_schwarz', 'value')],
    [State('runde_id', 'value'),
     State('geber_id', 'value'),
     State('ausspieler_id', 'value'),
     State('mittelhand_id', 'value'),
     State('hinterhand_id', 'value'),
     State('geberhand_id', 'value')])
def calculate_solo(
        solo_spielstand_eintragen_button_n_clicks: int,
        solo_gelegt_ids: List[int],
        solo_ansager_id: Union[None, int],
        solo_spielart: Union[None, str],
        solo_kontriert_id: List[int],
        solo_re_id: List[int],
        solo_farbe: List[str],
        solo_tout: List[int],
        solo_laufende: Union[None, int],
        solo_spieler_nichtspieler_augen: Union[None, int],
        solo_augen: Union[None, int],
        solo_schwarz: Union[None, int],
        runde_id: Union[None, str],
        geber_id: Union[None, str],
        ausspieler_id: Union[None, str],
        mittelhand_id: Union[None, str],
        hinterhand_id: Union[None, str],
        geberhand_id: Union[None, str]) -> Tuple[Union[None, List[html.Div]], Dict, html.Div, html.Div, bool]:
    teilnehmer_ids = [ausspieler_id, mittelhand_id, hinterhand_id, geberhand_id]
    if _validate_teilnehmer(runde_id, geber_id, teilnehmer_ids) is not None:
        return None, dict(), html.Div(), html.Div(), False
    raw_config = SoloRawConfig(runde_id=int(runde_id),
                               geber_id=geber_id,
                               teilnehmer_ids=[int(t) for t in teilnehmer_ids],
                               gelegt_ids=solo_gelegt_ids,
                               ansager_id=solo_ansager_id,
                               spielart=solo_spielart,
                               kontriert_id=solo_kontriert_id,
                               re_id=solo_re_id,
                               farbe=solo_farbe,
                               tout=solo_tout,
                               laufende=solo_laufende,
                               spieler_nichtspieler_augen=solo_spieler_nichtspieler_augen,
                               augen=solo_augen,
                               schwarz=solo_schwarz)
    solo_validator = SoloValidator(raw_config)
    messages = solo_validator.validation_messages
    if len(messages) > 0:
        return wrap_alert(messages), dict(display='none'), html.Div(), html.Div(), False
    solo_calculator = SoloCalculator(solo_validator.validated_config)
    result = SoloPresenter(solo_calculator).get_result()
    return result, dict(), html.Div(), html.Div(), False
    # if rufspiel_spielstand_eintragen_button_n_clicks is not None and rufspiel_spielstand_eintragen_button_n_clicks >= 1:
    #     RufspielWriter(rufspiel_calculator).write()
    #     header, body = wrap_stats([runde_id])
    #     return result, dict(), header, body, True
    # else:
    #     return result, dict(), html.Div(), html.Div(), False


@app.callback(
    [Output('stats_modal_header', 'children'),
     Output('stats_modal_body', 'children'),
     Output('stats_modal', 'is_open'),
     Output('stats_modal_open_n_clicks', 'data'),
     Output('stats_modal_close_n_clicks', 'data')],
    [Input('stats_modal_open', 'n_clicks'),
     Input('stats_modal_close', 'n_clicks')],
    [State('stats_modal_open_n_clicks', 'data'),
     State('stats_modal_close_n_clicks', 'data'),
     State('stats_modal', 'is_open'),
     State('runde_id', 'value')],
)
def show_stats(stats_modal_open: Union[None, int],
               stats_modal_close: Union[None, int],
               stats_modal_open_n_clicks: Dict,
               stats_modal_close_n_clicks: Dict,
               stats_modal: bool,
               runde_id: Union[None, str]) -> Tuple[html.Div, html.Div, bool, Dict, Dict]:
    stats_modal_open = 0 if stats_modal_open is None else stats_modal_open
    stats_modal_close = 0 if stats_modal_close is None else stats_modal_close
    if stats_modal_open == 0 and stats_modal_close == 0:
        return html.Div(), html.Div(), stats_modal, {'clicks': stats_modal_open}, {'clicks': stats_modal_close}
    if stats_modal_open > stats_modal_open_n_clicks['clicks']:
        header, body = wrap_stats([runde_id])
    elif stats_modal_close > stats_modal_close_n_clicks['clicks']:
        header, body = html.Div(), html.Div()
    else:
        header, body = html.Div(), html.Div()
    return header, body, not stats_modal, {'clicks': stats_modal_open}, {'clicks': stats_modal_close}


@app.callback(
    [Output('stats_all_modal_header', 'children'),
     Output('stats_all_modal_body', 'children'),
     Output('stats_all_modal', 'is_open'),
     Output('stats_all_modal_open_n_clicks', 'data'),
     Output('stats_all_modal_close_n_clicks', 'data')],
    [Input('stats_all_modal_open', 'n_clicks'),
     Input('stats_all_modal_close', 'n_clicks')],
    [State('stats_all_modal_open_n_clicks', 'data'),
     State('stats_all_modal_close_n_clicks', 'data'),
     State('stats_all_modal', 'is_open')],
)
def show_stats_all(stats_all_modal_open: Union[None, int],
                   stats_all_modal_close: Union[None, int],
                   stats_all_modal_open_n_clicks: Dict,
                   stats_all_modal_close_n_clicks: Dict,
                   stats_all_modal: bool) -> Tuple[html.Div, html.Div, bool, Dict, Dict]:
    stats_all_modal_open = 0 if stats_all_modal_open is None else stats_all_modal_open
    stats_all_modal_close = 0 if stats_all_modal_close is None else stats_all_modal_close
    if stats_all_modal_open == 0 and stats_all_modal_close == 0:
        return html.Div(), html.Div(), stats_all_modal, {'clicks': stats_all_modal_open}, {
            'clicks': stats_all_modal_close}
    if stats_all_modal_open > stats_all_modal_open_n_clicks['clicks']:
        header, body = wrap_stats([str(r.id) for r in get_runden()])
    elif stats_all_modal_close > stats_all_modal_close_n_clicks['clicks']:
        header, body = html.Div(), html.Div()
    else:
        header, body = html.Div(), html.Div()
    return header, body, not stats_all_modal, {'clicks': stats_all_modal_open}, {'clicks': stats_all_modal_close}


def _validate_teilnehmer(runde_id: str, geber_id: str, teilnehmer_ids: List[str]) -> Union[html.Div, None]:
    m = []
    if runde_id is None:
        m.append(f'Bitte wählen Sie eine Runde.')
    if None in teilnehmer_ids:
        m.append(f'Bitte wählen einen Geber und vier Teilnehmer.')
    teilnehmer_ids_without_none = [int(t) for t in teilnehmer_ids if t is not None]
    if len(teilnehmer_ids_without_none) != len(set(teilnehmer_ids_without_none)):
        m.append(f'Bitte wählen Sie eindeutige Teilnehmer.')
    teilnehmer_ids_without_none_and_geberhand = [int(t) for t in teilnehmer_ids[:-1] if t is not None]
    if geber_id is not None and int(geber_id) in teilnehmer_ids_without_none_and_geberhand:
        m.append(f'Bitte positionieren Sie den Geber auf die Geberhand.')
    if len(m) == 0:
        return None
    return wrap_alert(m)


if __name__ == '__main__':
    app.run_server(debug=True)
