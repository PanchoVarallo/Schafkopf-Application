from abc import abstractmethod
from typing import List, Dict

import dash_bootstrap_components as dbc
import dash_html_components as html

from schafkopf.backend.calculator import RufspielCalculator, SoloCalculator, Calculator, RufspielHochzeitCalculator, \
    NormalspielCalculator, HochzeitCalculator, RamschCalculator
from schafkopf.database.configs import Config, NormalspielConfig, RamschConfig
from schafkopf.database.queries import get_teilnehmer_name_by_id, get_teilnehmer_vorname_by_id
from schafkopf.frontend.generic_objects import wrap_html_tr, wrap_html_tbody


class Presenter:
    def __init__(self, calculator: Calculator):
        self._calculator = calculator

    def get_result(self) -> dbc.Row:
        result_div = []
        result_div.extend(
            [dbc.Col([dbc.Table(self._get_result_body(), bordered=False, striped=True, hover=True)], xl=6, xs=12)])
        result_div.extend(
            [dbc.Col(self.get_result_message(self._calculator.get_teilnehmer_id_to_punkte()), xl=6, xs=12)])
        return dbc.Row(result_div)

    @staticmethod
    def get_result_message(teilnehmer_id_to_punkte: Dict, row_wise: bool = False) -> dbc.Row:
        gewinner = {key: value for key, value in teilnehmer_id_to_punkte.items() if value > 0}
        verlierer = {key: value for key, value in teilnehmer_id_to_punkte.items() if value < 0}
        result_div = []
        for key, value in gewinner.items():
            msg = [html.B(f'{get_teilnehmer_vorname_by_id(key)}'), f' +', html.B(f'{int(value)}')]
            result_div.append(dbc.Col([dbc.Alert(msg, color='success')], xl=6, xs=12))
        for key, value in verlierer.items():
            msg = [html.B(f'{get_teilnehmer_vorname_by_id(key)}'), f' -', html.B(f'{-int(value)}')]
            result_div.append(dbc.Col([dbc.Alert(msg, color='danger')], xl=6, xs=12))
        if row_wise:
            row_wise_rows = []
            for col in result_div:
                row_wise_rows.append(dbc.Row([col]))
            return html.Div(row_wise_rows)
        return dbc.Row(result_div)

    @staticmethod
    @abstractmethod
    def _add_result_points_details(calculator: Calculator, config: Config, r: List[html.Tr]):
        pass

    @abstractmethod
    def _get_result_body(self) -> html.Tbody:
        pass


class NormalspielPresenter(Presenter):
    def __init__(self, calculator: NormalspielCalculator):
        super().__init__(calculator)
        self._calculator = calculator

    @staticmethod
    def _add_result_points_details(calculator: NormalspielCalculator, config: NormalspielConfig, r: List[html.Tr]):
        if calculator.is_schneider():
            r.append(wrap_html_tr(['Schneider', '', f'+{int(config.punkteconfig.schneider)}']))
        if calculator.is_schwarz():
            r.append(wrap_html_tr(['Schwarz', '', f'+{int(config.punkteconfig.schwarz)}']))
        if config.laufende > 0:
            r.append(wrap_html_tr(['Laufende', f'{config.laufende}', f'+{int(calculator.get_punkte_laufende())}']))
        if len(config.gelegt_ids) > 0:
            teilnehmer_gelegt_ids = [get_teilnehmer_name_by_id(s) for s in config.gelegt_ids]
            r.append(wrap_html_tr(['Gelegt', '; '.join(teilnehmer_gelegt_ids), f'x{2 ** len(config.gelegt_ids)}']))
        if config.kontriert_id is not None and config.kontriert_id > 0:
            r.append(wrap_html_tr(['Kontriert', get_teilnehmer_name_by_id(config.kontriert_id), f'x2']))
        if config.re_id is not None and config.re_id > 0:
            r.append(wrap_html_tr(['Re', get_teilnehmer_name_by_id(config.re_id), f'x2']))
        r.append(wrap_html_tr(['Summe', '', html.B(f'{int(calculator.get_spielpunkte())}')]))

    @abstractmethod
    def _get_result_body(self) -> html.Tbody:
        pass


class RufspielHochzeitPresenter(NormalspielPresenter):
    def __init__(self, calculator: RufspielHochzeitCalculator):
        super().__init__(calculator)
        self._calculator = calculator

    def _get_result_body(self) -> html.Tbody:
        calculator = self._calculator
        config = calculator.config
        result_points = [wrap_html_tr(['Grundpunkte', '', f'{self._get_punkte_from_punkteconfig()}'])]
        self._add_result_points_details(calculator, config, result_points)
        return wrap_html_tbody(result_points)

    @abstractmethod
    def _get_punkte_from_punkteconfig(self) -> int:
        pass


class RufspielPresenter(RufspielHochzeitPresenter):

    def __init__(self, calculator: RufspielCalculator):
        super().__init__(calculator)
        self._calculator = calculator

    def _get_punkte_from_punkteconfig(self) -> int:
        return self._calculator.config.punkteconfig.rufspiel


class SoloPresenter(NormalspielPresenter):
    def __init__(self, calculator: SoloCalculator):
        super().__init__(calculator)
        self._calculator = calculator

    def _get_result_body(self) -> html.Tbody:
        calculator = self._calculator
        config = calculator.config
        result_points = [wrap_html_tr(['Grundpunkte', '', f'{config.punkteconfig.solo}'])]
        self._add_result_points_details(calculator, config, result_points)
        # Add Tout Line
        if config.tout_gespielt_gewonnen or config.tout_gespielt_verloren:
            result_points.insert(-1, wrap_html_tr(['Tout', '', f'x2']))
        return wrap_html_tbody(result_points)


class HochzeitPresenter(RufspielHochzeitPresenter):

    def __init__(self, calculator: HochzeitCalculator):
        super().__init__(calculator)
        self._calculator = calculator

    def _get_punkte_from_punkteconfig(self) -> int:
        return self._calculator.config.punkteconfig.hochzeit


class RamschPresenter(Presenter):

    def __init__(self, calculator: RamschCalculator):
        super().__init__(calculator)
        self._calculator = calculator

    @staticmethod
    def _add_result_points_details(calculator: RamschCalculator, config: RamschConfig, r: List[html.Tr]):
        if len(config.gelegt_ids) > 0:
            teilnehmer_gelegt_ids = [get_teilnehmer_name_by_id(s) for s in config.gelegt_ids]
            r.append(wrap_html_tr(['Gelegt', '; '.join(teilnehmer_gelegt_ids), f'x{2 ** len(config.gelegt_ids)}']))
        if len(config.jungfrau_ids) > 0:
            teilnehmer_jungfrau_ids = [get_teilnehmer_name_by_id(s) for s in config.jungfrau_ids]
            r.append(wrap_html_tr(['Gelegt', '; '.join(teilnehmer_jungfrau_ids), f'x{2 ** len(config.jungfrau_ids)}']))
        r.append(wrap_html_tr(['Summe', '', html.B(f'{int(calculator.get_spielpunkte())}')]))

    def _get_result_body(self) -> html.Tbody:
        calculator = self._calculator
        config = calculator.config
        result_points = [wrap_html_tr(['Grundpunkte', '', f'{self._get_punkte_from_punkteconfig()}'])]
        self._add_result_points_details(calculator, config, result_points)
        return wrap_html_tbody(result_points)

    def _get_punkte_from_punkteconfig(self) -> int:
        if self._calculator.config.durchmarsch:
            return self._calculator.config.punkteconfig.solo
        return self._calculator.config.punkteconfig.rufspiel
