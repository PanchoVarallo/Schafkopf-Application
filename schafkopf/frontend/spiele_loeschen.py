import dash_bootstrap_components as dbc
import dash_html_components as html

from schafkopf.frontend.generic_objects import wrap_empty_dbc_row, wrap_footer_row


def wrap_spiele_loeschen_layout():
    return html.Div([
        dbc.Container([
            wrap_empty_dbc_row(),
            wrap_footer_row()
        ]),
    ])
