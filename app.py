# -*- coding: utf-8 -*-
import json
import locale
from typing import List, Union, Dict, Tuple

import dash
import dash_auth
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from schafkopf.frontend.start import wrap_start_layout

from schafkopf.backend.calculator import RufspielCalculator, SoloCalculator, HochzeitCalculator, RamschCalculator
from schafkopf.backend.configs import RufspielRawConfig, SoloRawConfig, HochzeitRawConfig, RamschRawConfig
from schafkopf.backend.validator import RufspielValidator, SoloValidator, HochzeitValidator, RamschValidator
from schafkopf.database.queries import get_runden
from schafkopf.database.writer import RufspielWriter, SoloWriter, HochzeitWriter, RamschWriter
from schafkopf.frontend.daten_anlegen import wrap_daten_layout
from schafkopf.frontend.generic_objects import wrap_alert, wrap_stats_by_runde_ids, wrap_rufspiel_card, \
    wrap_next_game_button, wrap_solo_card, wrap_hochzeit_card, \
    wrap_ramsch_card, wrap_stats_by_teilnehmer_ids
from schafkopf.frontend.presenter import RufspielPresenter, SoloPresenter, HochzeitPresenter, RamschPresenter
from schafkopf.frontend.spielen import wrap_spielen_layout
from schafkopf.frontend.statistiken import wrap_statistiken_layout

with open('schafkopf/auth.json') as json_file:
    data = json.load(json_file)
    users = data['USER']
VALID_USERNAME_PASSWORD_PAIRS = {user['username']: user['password'] for user in users}

external_stylesheets = [dbc.themes.DARKLY]
locale.setlocale(locale.LC_TIME, 'de_DE.utf8')
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
auth = dash_auth.BasicAuth(
    app, VALID_USERNAME_PASSWORD_PAIRS
)
app.config.suppress_callback_exceptions = True
app.title = 'Digitale Schafkopfliste'

app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Spielen", href="/spielen")),
            dbc.NavItem(dbc.NavLink("Statistiken", href="/statistiken")),
            dbc.NavItem(dbc.NavLink("Daten anlegen", href="/daten_anlegen")),
        ],
        brand="Digitale Schafkopfliste",
        brand_href="/start",
        color="primary",
        dark=True,
    ),

    # content will be rendered in this element
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname: str):
    if pathname == "/start":
        return wrap_start_layout()
    elif pathname == "/spielen":
        return wrap_spielen_layout()
    elif pathname == "/statistiken":
        return wrap_statistiken_layout()
    elif pathname == "/daten_anlegen":
        return wrap_daten_layout()
    else:
        return wrap_spielen_layout()


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
               Input('geberhand_id', 'value'),
               Input('gelegt_ausspieler_id', 'value'),
               Input('gelegt_mittelhand_id', 'value'),
               Input('gelegt_hinterhand_id', 'value'),
               Input('gelegt_geberhand_id', 'value')])
def switch_tab(active_tab: str,
               runde_id: Union[None, str],
               geber_id: Union[None, str],
               ausspieler_id: Union[None, str],
               mittelhand_id: Union[None, str],
               hinterhand_id: Union[None, str],
               geberhand_id: Union[None, str],
               gelegt_ausspieler_id: List[int],
               gelegt_mittelhand_id: List[int],
               gelegt_hinterhand_id: List[int],
               gelegt_geberhand_id: List[int]) -> Tuple[dbc.Card, html.Div, html.Div, html.Div, html.Div]:
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
        return wrap_hochzeit_card(ausspieler_id, mittelhand_id, hinterhand_id, geberhand_id), \
               wrap_next_game_button(), wrap_next_game_button(), wrap_next_game_button(), wrap_next_game_button()
    elif active_tab == 'ramsch_tab':
        return wrap_ramsch_card(ausspieler_id, mittelhand_id, hinterhand_id, geberhand_id), \
               wrap_next_game_button(), wrap_next_game_button(), wrap_next_game_button(), wrap_next_game_button()
    return html.P('This should not ever be displayed...')


@app.callback(
    [Output('rufspiel_validierung_content', 'children'),
     Output('rufspiel_spielstand_eintragen_button', 'style'),
     Output('rufspiel_stats_modal_header', 'children'),
     Output('rufspiel_stats_modal_body', 'children'),
     Output('rufspiel_spielstand_modal', 'is_open')],
    [Input('rufspiel_spielstand_eintragen_button', 'n_clicks'),
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
     State('geberhand_id', 'value'),
     State('gelegt_ausspieler_id', 'value'),
     State('gelegt_mittelhand_id', 'value'),
     State('gelegt_hinterhand_id', 'value'),
     State('gelegt_geberhand_id', 'value'),
     ])
def calculate_rufspiel(
        rufspiel_spielstand_eintragen_button_n_clicks: int,
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
        geberhand_id: Union[None, str],
        gelegt_ausspieler_id: List[int],
        gelegt_mittelhand_id: List[int],
        gelegt_hinterhand_id: List[int],
        gelegt_geberhand_id: List[int]) -> Tuple[Union[None, dbc.Row], Dict, html.Div, html.Div, bool]:
    teilnehmer_ids = [ausspieler_id, mittelhand_id, hinterhand_id, geberhand_id]
    if _validate_teilnehmer(runde_id, geber_id, teilnehmer_ids) is not None:
        return None, dict(), html.Div(), html.Div(), False
    gelegt_ids = _get_gelegt_ids(ausspieler_id, mittelhand_id, hinterhand_id, geberhand_id, gelegt_ausspieler_id,
                                 gelegt_mittelhand_id, gelegt_hinterhand_id, gelegt_geberhand_id)
    raw_config = RufspielRawConfig(runde_id=int(runde_id),
                                   geber_id=geber_id,
                                   teilnehmer_ids=[int(t) for t in teilnehmer_ids],
                                   gelegt_ids=gelegt_ids,
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
        header, body = wrap_stats_by_runde_ids([runde_id])
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
     State('geberhand_id', 'value'),
     State('gelegt_ausspieler_id', 'value'),
     State('gelegt_mittelhand_id', 'value'),
     State('gelegt_hinterhand_id', 'value'),
     State('gelegt_geberhand_id', 'value'),
     ])
def calculate_solo(
        solo_spielstand_eintragen_button_n_clicks: int,
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
        geberhand_id: Union[None, str],
        gelegt_ausspieler_id: List[int],
        gelegt_mittelhand_id: List[int],
        gelegt_hinterhand_id: List[int],
        gelegt_geberhand_id: List[int]) -> Tuple[Union[None, dbc.Row], Dict, html.Div, html.Div, bool]:
    teilnehmer_ids = [ausspieler_id, mittelhand_id, hinterhand_id, geberhand_id]
    if _validate_teilnehmer(runde_id, geber_id, teilnehmer_ids) is not None:
        return None, dict(), html.Div(), html.Div(), False
    gelegt_ids = _get_gelegt_ids(ausspieler_id, mittelhand_id, hinterhand_id, geberhand_id, gelegt_ausspieler_id,
                                 gelegt_mittelhand_id, gelegt_hinterhand_id, gelegt_geberhand_id)
    raw_config = SoloRawConfig(runde_id=int(runde_id),
                               geber_id=geber_id,
                               teilnehmer_ids=[int(t) for t in teilnehmer_ids],
                               gelegt_ids=gelegt_ids,
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
    if solo_spielstand_eintragen_button_n_clicks is not None and solo_spielstand_eintragen_button_n_clicks >= 1:
        SoloWriter(solo_calculator).write()
        header, body = wrap_stats_by_runde_ids([runde_id])
        return result, dict(), header, body, True
    else:
        return result, dict(), html.Div(), html.Div(), False


@app.callback(
    [Output('hochzeit_validierung_content', 'children'),
     Output('hochzeit_spielstand_eintragen_button', 'style'),
     Output('hochzeit_stats_modal_header', 'children'),
     Output('hochzeit_stats_modal_body', 'children'),
     Output('hochzeit_spielstand_modal', 'is_open')],
    [Input('hochzeit_spielstand_eintragen_button', 'n_clicks'),
     Input('hochzeit_ansager_id', 'value'),
     Input('hochzeit_kontriert_id', 'value'),
     Input('hochzeit_re_id', 'value'),
     Input('hochzeit_partner_id', 'value'),
     Input('hochzeit_laufende', 'value'),
     Input('hochzeit_spieler_nichtspieler_augen', 'value'),
     Input('hochzeit_augen', 'value'),
     Input('hochzeit_schwarz', 'value')],
    [State('runde_id', 'value'),
     State('geber_id', 'value'),
     State('ausspieler_id', 'value'),
     State('mittelhand_id', 'value'),
     State('hinterhand_id', 'value'),
     State('geberhand_id', 'value'),
     State('gelegt_ausspieler_id', 'value'),
     State('gelegt_mittelhand_id', 'value'),
     State('gelegt_hinterhand_id', 'value'),
     State('gelegt_geberhand_id', 'value'),
     ])
def calculate_rufspiel(
        hochzeit_spielstand_eintragen_button_n_clicks: int,
        hochzeit_ansager_id: Union[None, int],
        hochzeit_kontriert_id: List[int],
        hochzeit_re_id: List[int],
        hochzeit_partner_id: Union[None, int],
        hochzeit_laufende: Union[None, int],
        hochzeit_spieler_nichtspieler_augen: Union[None, int],
        hochzeit_augen: Union[None, int],
        hochzeit_schwarz: Union[None, int],
        runde_id: Union[None, str],
        geber_id: Union[None, str],
        ausspieler_id: Union[None, str],
        mittelhand_id: Union[None, str],
        hinterhand_id: Union[None, str],
        geberhand_id: Union[None, str],
        gelegt_ausspieler_id: List[int],
        gelegt_mittelhand_id: List[int],
        gelegt_hinterhand_id: List[int],
        gelegt_geberhand_id: List[int]) -> Tuple[Union[None, dbc.Row], Dict, html.Div, html.Div, bool]:
    teilnehmer_ids = [ausspieler_id, mittelhand_id, hinterhand_id, geberhand_id]
    if _validate_teilnehmer(runde_id, geber_id, teilnehmer_ids) is not None:
        return None, dict(), html.Div(), html.Div(), False
    gelegt_ids = _get_gelegt_ids(ausspieler_id, mittelhand_id, hinterhand_id, geberhand_id, gelegt_ausspieler_id,
                                 gelegt_mittelhand_id, gelegt_hinterhand_id, gelegt_geberhand_id)
    raw_config = HochzeitRawConfig(runde_id=int(runde_id),
                                   geber_id=geber_id,
                                   teilnehmer_ids=[int(t) for t in teilnehmer_ids],
                                   gelegt_ids=gelegt_ids,
                                   ansager_id=hochzeit_ansager_id,
                                   kontriert_id=hochzeit_kontriert_id,
                                   re_id=hochzeit_re_id,
                                   partner_id=hochzeit_partner_id,
                                   laufende=hochzeit_laufende,
                                   spieler_nichtspieler_augen=hochzeit_spieler_nichtspieler_augen,
                                   augen=hochzeit_augen,
                                   schwarz=hochzeit_schwarz)
    hochzeit_validator = HochzeitValidator(raw_config)
    messages = hochzeit_validator.validation_messages
    if len(messages) > 0:
        return wrap_alert(messages), dict(display='none'), html.Div(), html.Div(), False
    hochzeit_calculator = HochzeitCalculator(hochzeit_validator.validated_config)
    result = HochzeitPresenter(hochzeit_calculator).get_result()
    if hochzeit_spielstand_eintragen_button_n_clicks is not None and hochzeit_spielstand_eintragen_button_n_clicks >= 1:
        HochzeitWriter(hochzeit_calculator).write()
        header, body = wrap_stats_by_runde_ids([runde_id])
        return result, dict(), header, body, True
    else:
        return result, dict(), html.Div(), html.Div(), False


@app.callback(
    [Output('ramsch_validierung_content', 'children'),
     Output('ramsch_spielstand_eintragen_button', 'style'),
     Output('ramsch_stats_modal_header', 'children'),
     Output('ramsch_stats_modal_body', 'children'),
     Output('ramsch_spielstand_modal', 'is_open')],
    [Input('ramsch_spielstand_eintragen_button', 'n_clicks'),
     Input('ramsch_jungfrau_ids', 'value'),
     Input('ramsch_ausspieler_augen', 'value'),
     Input('ramsch_mittelhand_augen', 'value'),
     Input('ramsch_hinterhand_augen', 'value'),
     Input('ramsch_geberhand_augen', 'value'),
     Input('ramsch_manuelle_verlierer_ids', 'value')],
    [State('runde_id', 'value'),
     State('geber_id', 'value'),
     State('ausspieler_id', 'value'),
     State('mittelhand_id', 'value'),
     State('hinterhand_id', 'value'),
     State('geberhand_id', 'value'),
     State('gelegt_ausspieler_id', 'value'),
     State('gelegt_mittelhand_id', 'value'),
     State('gelegt_hinterhand_id', 'value'),
     State('gelegt_geberhand_id', 'value'),
     ])
def calculate_ramsch(
        ramsch_spielstand_eintragen_button_n_clicks: int,
        ramsch_jungfrau_ids: List[int],
        ramsch_ausspieler_augen: Union[None, int],
        ramsch_mittelhand_augen: Union[None, int],
        ramsch_hinterhand_augen: Union[None, int],
        ramsch_geberhand_augen: Union[None, int],
        ramsch_manuelle_verlierer_ids: List[int],
        runde_id: Union[None, str],
        geber_id: Union[None, str],
        ausspieler_id: Union[None, str],
        mittelhand_id: Union[None, str],
        hinterhand_id: Union[None, str],
        geberhand_id: Union[None, str],
        gelegt_ausspieler_id: List[int],
        gelegt_mittelhand_id: List[int],
        gelegt_hinterhand_id: List[int],
        gelegt_geberhand_id: List[int]) -> Tuple[Union[None, dbc.Row], Dict, html.Div, html.Div, bool]:
    teilnehmer_ids = [ausspieler_id, mittelhand_id, hinterhand_id, geberhand_id]
    if _validate_teilnehmer(runde_id, geber_id, teilnehmer_ids) is not None:
        return None, dict(), html.Div(), html.Div(), False
    gelegt_ids = _get_gelegt_ids(ausspieler_id, mittelhand_id, hinterhand_id, geberhand_id, gelegt_ausspieler_id,
                                 gelegt_mittelhand_id, gelegt_hinterhand_id, gelegt_geberhand_id)
    raw_config = RamschRawConfig(runde_id=int(runde_id),
                                 geber_id=geber_id,
                                 teilnehmer_ids=[int(t) for t in teilnehmer_ids],
                                 gelegt_ids=gelegt_ids,
                                 jungfrau_ids=ramsch_jungfrau_ids,
                                 ausspieler_augen=ramsch_ausspieler_augen,
                                 mittelhand_augen=ramsch_mittelhand_augen,
                                 hinterhand_augen=ramsch_hinterhand_augen,
                                 geberhand_augen=ramsch_geberhand_augen,
                                 manuelle_verlierer_ids=ramsch_manuelle_verlierer_ids)
    ramsch_validator = RamschValidator(raw_config)
    messages = ramsch_validator.validation_messages
    if len(messages) > 0:
        return wrap_alert(messages), dict(display='none'), html.Div(), html.Div(), False
    ramsch_calculator = RamschCalculator(ramsch_validator.validated_config)
    result = RamschPresenter(ramsch_calculator).get_result()
    if ramsch_spielstand_eintragen_button_n_clicks is not None and ramsch_spielstand_eintragen_button_n_clicks >= 1:
        RamschWriter(ramsch_calculator).write()
        header, body = wrap_stats_by_runde_ids([runde_id])
        return result, dict(), header, body, True
    else:
        return result, dict(), html.Div(), html.Div(), False


def _get_gelegt_ids(ausspieler_id: Union[None, str], mittelhand_id: Union[None, str], hinterhand_id: Union[None, str],
                    geberhand_id: Union[None, str], gelegt_ausspieler_id: List[int], gelegt_mittelhand_id: List[int],
                    gelegt_hinterhand_id: List[int], gelegt_geberhand_id: List[int]) -> List[int]:
    gelegt_ids = []
    if len(gelegt_ausspieler_id) == 1:
        gelegt_ids.append(int(ausspieler_id))
    if len(gelegt_mittelhand_id) == 1:
        gelegt_ids.append(int(mittelhand_id))
    if len(gelegt_hinterhand_id) == 1:
        gelegt_ids.append(int(hinterhand_id))
    if len(gelegt_geberhand_id) == 1:
        gelegt_ids.append(int(geberhand_id))
    return gelegt_ids


@app.callback(
    [Output('stats_teilnehmer_modal_header', 'children'),
     Output('stats_teilnehmer_modal_body', 'children'),
     Output('stats_teilnehmer_modal', 'is_open'),
     Output('stats_teilnehmer_modal_open_n_clicks', 'data'),
     Output('stats_teilnehmer_modal_close_n_clicks', 'data')],
    [Input('stats_teilnehmer_modal_open', 'n_clicks'),
     Input('stats_teilnehmer_modal_close', 'n_clicks')],
    [State('stats_teilnehmer_modal_open_n_clicks', 'data'),
     State('stats_teilnehmer_modal_close_n_clicks', 'data'),
     State('stats_teilnehmer_modal', 'is_open'),
     State('selected_teilnehmer_ids', 'value')],
)
def show_stats_teilnehmer(stats_teilnehmer_modal_open: Union[None, int],
                          stats_teilnehmer_modal_close: Union[None, int],
                          stats_teilnehmer_modal_open_n_clicks: Dict,
                          stats_teilnehmer_modal_close_n_clicks: Dict,
                          stats_teilnehmer_modal: bool,
                          selected_teilnehmer_ids: Union[None, List[str]]) -> Tuple[html.Div, html.Div, bool, Dict,
                                                                                    Dict]:
    selected_teilnehmer_ids = [] if selected_teilnehmer_ids is None else selected_teilnehmer_ids
    stats_teilnehmer_modal_open = 0 if stats_teilnehmer_modal_open is None else stats_teilnehmer_modal_open
    stats_teilnehmer_modal_close = 0 if stats_teilnehmer_modal_close is None else stats_teilnehmer_modal_close
    if stats_teilnehmer_modal_open == 0 and stats_teilnehmer_modal_close == 0:
        return html.Div(), html.Div(), stats_teilnehmer_modal, {'clicks': stats_teilnehmer_modal_open}, \
               {'clicks': stats_teilnehmer_modal_close}
    if stats_teilnehmer_modal_open > stats_teilnehmer_modal_open_n_clicks['clicks']:
        header, body = wrap_stats_by_teilnehmer_ids(selected_teilnehmer_ids, True)
    elif stats_teilnehmer_modal_close > stats_teilnehmer_modal_close_n_clicks['clicks']:
        header, body = html.Div(), html.Div()
    else:
        header, body = html.Div(), html.Div()
    return header, body, not stats_teilnehmer_modal, {'clicks': stats_teilnehmer_modal_open}, \
           {'clicks': stats_teilnehmer_modal_close}


@app.callback(
    [Output('stats_runden_modal_header', 'children'),
     Output('stats_runden_modal_body', 'children'),
     Output('stats_runden_modal', 'is_open'),
     Output('stats_runden_modal_open_n_clicks', 'data'),
     Output('stats_runden_modal_close_n_clicks', 'data')],
    [Input('stats_runden_modal_open', 'n_clicks'),
     Input('stats_runden_modal_close', 'n_clicks')],
    [State('stats_runden_modal_open_n_clicks', 'data'),
     State('stats_runden_modal_close_n_clicks', 'data'),
     State('stats_runden_modal', 'is_open'),
     State('selected_runden_ids', 'value')],
)
def show_stats_runden(stats_runden_modal_open: Union[None, int],
                      stats_runden_modal_close: Union[None, int],
                      stats_runden_modal_open_n_clicks: Dict,
                      stats_runden_modal_close_n_clicks: Dict,
                      stats_runden_modal: bool,
                      selected_runden_ids: Union[None, List[str]]) -> Tuple[html.Div, html.Div, bool, Dict, Dict]:
    selected_runden_ids = [] if selected_runden_ids is None else selected_runden_ids
    stats_runden_modal_open = 0 if stats_runden_modal_open is None else stats_runden_modal_open
    stats_runden_modal_close = 0 if stats_runden_modal_close is None else stats_runden_modal_close
    if stats_runden_modal_open == 0 and stats_runden_modal_close == 0:
        return html.Div(), html.Div(), stats_runden_modal, {'clicks': stats_runden_modal_open}, \
               {'clicks': stats_runden_modal_close}
    if stats_runden_modal_open > stats_runden_modal_open_n_clicks['clicks']:
        header, body = wrap_stats_by_runde_ids(selected_runden_ids, True)
    elif stats_runden_modal_close > stats_runden_modal_close_n_clicks['clicks']:
        header, body = html.Div(), html.Div()
    else:
        header, body = html.Div(), html.Div()
    return header, body, not stats_runden_modal, {'clicks': stats_runden_modal_open}, \
           {'clicks': stats_runden_modal_close}


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
        header, body = wrap_stats_by_runde_ids([str(r.id) for r in get_runden()], True)
    elif stats_all_modal_close > stats_all_modal_close_n_clicks['clicks']:
        header, body = html.Div(), html.Div()
    else:
        header, body = html.Div(), html.Div()
    return header, body, not stats_all_modal, {'clicks': stats_all_modal_open}, {'clicks': stats_all_modal_close}


def _validate_teilnehmer(runde_id: Union[None, str], geber_id: Union[None, str],
                         teilnehmer_ids: List[str]) -> Union[html.Div, None]:
    m = []
    if runde_id is None:
        m.append(f'Bitte wählen Sie eine Runde.')
    if geber_id is None:
        m.append(f'Bitte wählen einen Geber.')
    if None in teilnehmer_ids:
        m.append(f'Bitte wählen Sie vier Teilnehmer.')
    teilnehmer_ids_without_none = [int(t) for t in teilnehmer_ids if t is not None]
    if len(teilnehmer_ids_without_none) != len(set(teilnehmer_ids_without_none)):
        m.append(f'Bitte wählen Sie eindeutige Teilnehmer.')
    teilnehmer_ids_without_none_and_geberhand = [int(t) for t in teilnehmer_ids[:-1] if t is not None]
    if geber_id is not None and int(geber_id) in teilnehmer_ids_without_none_and_geberhand:
        m.append(f'Bitte positionieren Sie den Geber eindeutig auf die Geberhand.')
    if len(m) == 0:
        return None
    return wrap_alert(m)


if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server()
