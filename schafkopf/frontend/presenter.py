from abc import abstractmethod
from typing import List, Dict

import dash_bootstrap_components as dbc
import dash_html_components as html

from schafkopf.backend.calculator import RufspielCalculator, SoloCalculator, Calculator
from schafkopf.backend.configs import Config
from schafkopf.database.queries import get_teilnehmer_name_by_id
from schafkopf.frontend.generic_objects import wrap_html_tr, wrap_html_tbody


class Presenter:
    def __init__(self, calculator: Calculator):
        self._calculator = calculator

    def get_result(self) -> List[html.Div]:
        result_div = []
        result_div.extend([html.Div(dbc.Table(self._get_result_body(), bordered=False, striped=True, hover=True))])
        result_div.extend(self._get_result_message(self._calculator.get_teilnehmer_id_to_punkte()))
        return result_div

    @staticmethod
    def _get_result_message(teilnehmer_id_to_punkte: Dict) -> List[html.Div]:
        gewinner = {key: value for key, value in teilnehmer_id_to_punkte.items() if value > 0}
        verlierer = {key: value for key, value in teilnehmer_id_to_punkte.items() if value < 0}
        result_div = []
        for key, value in gewinner.items():
            msg = [html.I(f'{get_teilnehmer_name_by_id(key)}'), f' gewinnt {value} Punkte!']
            result_div.append(html.Div(dbc.Alert(msg, color='success')))
        for key, value in verlierer.items():
            msg = [html.I(f'{get_teilnehmer_name_by_id(key)}'), f' verliert {-value} Punkte!']
            result_div.append(html.Div(dbc.Alert(msg, color='secondary')))
        return result_div

    @staticmethod
    def _add_result_points_details(calculator: Calculator, config: Config, r: List[html.Tr]):
        if calculator.is_schneider():
            r.append(wrap_html_tr(['Schneider', 'ja', f'+{config.punkteconfig.schneider}']))
        if calculator.is_schwarz():
            r.append(wrap_html_tr(['Schwarz', 'ja', f'+{config.punkteconfig.schwarz}']))
        if config.laufende > 0:
            r.append(wrap_html_tr(['Laufende', f'{config.laufende}', f'+{calculator.get_punkte_laufende()}']))
        if len(config.gelegt_ids) > 0:
            teilnehmer_gelegt_ids = [get_teilnehmer_name_by_id(s) for s in config.gelegt_ids]
            r.append(wrap_html_tr(['Gelegt', '; '.join(teilnehmer_gelegt_ids), f'x{2 ** len(config.gelegt_ids)}']))
        if config.kontriert_id is not None and config.kontriert_id > 0:
            r.append(wrap_html_tr(['Kontriert', get_teilnehmer_name_by_id(config.kontriert_id), f'x2']))
        if config.re_id is not None and config.re_id > 0:
            r.append(wrap_html_tr(['Re', get_teilnehmer_name_by_id(config.re_id), f'x2']))
        r.append(wrap_html_tr(["Summe", '', f'{calculator.get_spielpunkte()}']))

    @abstractmethod
    def _get_result_body(self) -> html.Tbody:
        pass


class RufspielPresenter(Presenter):
    def __init__(self, calculator: RufspielCalculator):
        super().__init__(calculator)
        self._calculator = calculator

    def _get_result_body(self) -> html.Tbody:
        calculator = self._calculator
        config = calculator.config
        result_points = [wrap_html_tr(["Grundpunkte", "", f'{config.punkteconfig.rufspiel}'])]
        self._add_result_points_details(calculator, config, result_points)
        return wrap_html_tbody(result_points)


class SoloPresenter(Presenter):
    def __init__(self, calculator: SoloCalculator):
        super().__init__(calculator)
        self._calculator = calculator

    def _get_result_body(self) -> html.Tbody:
        calculator = self._calculator
        config = calculator.config
        result_points = [wrap_html_tr(["Grundpunkte", "", f'{config.punkteconfig.solo}'])]
        self._add_result_points_details(calculator, config, result_points)
        # Add Tout Line
        if config.tout_gespielt_gewonnen or config.tout_gespielt_verloren:
            result_points.insert(-1, wrap_html_tr(['Tout', '', f'x2']))
        return wrap_html_tbody(result_points)
