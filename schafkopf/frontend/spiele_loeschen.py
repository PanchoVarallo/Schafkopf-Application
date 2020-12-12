import pathlib

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from schafkopf.database.queries import get_latest_einzelspiel_id, get_latest_result, \
    get_einzelspiele_by_einzelspiel_ids, get_runde_by_id
from schafkopf.frontend.generic_objects import wrap_empty_dbc_row, wrap_footer_row, wrap_alert
from schafkopf.frontend.presenter import Presenter


def wrap_letztes_spiel_loeschen_layout():
    current = pathlib.Path(__file__).name.split('.')[0]
    einzelspiel_id = get_latest_einzelspiel_id()
    if einzelspiel_id is not None:
        einzelspiel = get_einzelspiele_by_einzelspiel_ids([einzelspiel_id])[0]
        runde = get_runde_by_id(einzelspiel.runde_id)
        df = get_latest_result()
        dict = {entry['teilnehmer_id']: entry['punkte'] for entry in df.to_dict(orient='records')}
        tt = f"{einzelspiel.created_on.strftime('%d.%m.%Y')} - {einzelspiel.created_on.strftime('%H:%M:%S')}"
        return html.Div([
            dcc.Store(id='delete_einzelspiel_modal_open_n_clicks', data={'n_clicks': 0}),
            dcc.Store(id='delete_einzelspiel_modal_close_n_clicks', data={'n_clicks': 0}),
            dcc.Store(id='delete_einzelspiel_einzelspiel_id', data={'id': einzelspiel_id}),
            dbc.Modal([
                dbc.ModalHeader(id='delete_einzelspiel_modal_header'),
                dbc.ModalBody(html.Div(id='delete_einzelspiel_modal_body')),
                dbc.ModalFooter([
                    dbc.Button('Schließen', id='delete_einzelspiel_modal_close', color='primary', block=True),
                    dbc.Button('Schließen', id='delete_einzelspiel_modal_close_reload', color='primary', block=True,
                               href=f'/{current}', external_link=True)]
                ), ], id='delete_einzelspiel_modal', size='xl', scrollable=True),
            dbc.Container([
                wrap_empty_dbc_row(),
                dbc.Row([
                    dbc.Col([
                        dbc.ListGroup(
                            [
                                dbc.ListGroupItem(f'{runde.name}'),
                                dbc.ListGroupItem(tt),
                                dbc.ListGroupItem(f'{einzelspiel.spielart.capitalize()}'),

                            ]
                        )
                    ], xl=6, xs=12),
                ]),
                wrap_empty_dbc_row(),
                Presenter.get_result_message(dict, row_wise=True),
                wrap_empty_dbc_row(),
                dbc.Row([
                    dbc.Col([
                        dbc.FormGroup(
                            [
                                dbc.Button('Spiel löschen',
                                           id='delete_einzelspiel_modal_open',
                                           color='primary', block=True),
                            ]
                        )
                    ], xl=6, xs=12)
                ]),
                wrap_footer_row()
            ]),
        ])
    else:
        return html.Div([
            dbc.Container([
                wrap_empty_dbc_row(),
                wrap_alert(['Bisher wurden keine Spiele gespielt.']),
                wrap_footer_row()
            ])
        ])
