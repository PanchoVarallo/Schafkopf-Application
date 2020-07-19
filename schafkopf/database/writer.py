from abc import abstractmethod
from typing import Union

from schafkopf.backend.calculator import RufspielCalculator, SoloCalculator, NormalspielCalculator, \
    RufspielHochzeitCalculator, HochzeitCalculator, RamschCalculator
from schafkopf.backend.configs import RamschConfig
from schafkopf.database.data_model import Spielart, Doppler, Einzelspiel
from schafkopf.database.queries import insert_einzelspiel, insert_resultat, insert_verdopplung
from schafkopf.database.session import Sessions


class Writer:
    pass


class NormalspielWriter(Writer):
    def __init__(self, calculator: NormalspielCalculator):
        super().__init__()
        self._calculator = calculator

    @staticmethod
    def _eintrag(session, einzelspiel, config, calculator):
        teilnehmer_id_to_punkte = calculator.get_teilnehmer_id_to_punkte()
        for spieler in config.get_spieler_ids():
            insert_resultat(teilnehmer_id=spieler,
                            einzelspiel_id=einzelspiel.id,
                            augen=config.spieler_augen,
                            punkte=teilnehmer_id_to_punkte.get(spieler),
                            gewonnen=True if spieler in calculator.get_gewinner_ids() else False,
                            session=session)
        for nicht_spieler in config.get_nicht_spieler_ids():
            insert_resultat(teilnehmer_id=nicht_spieler,
                            einzelspiel_id=einzelspiel.id,
                            augen=config.nicht_spieler_augen,
                            punkte=teilnehmer_id_to_punkte.get(nicht_spieler),
                            gewonnen=True if nicht_spieler in calculator.get_gewinner_ids() else False,
                            session=session)
        for teilnehmer_gelegt in config.gelegt_ids:
            insert_verdopplung(teilnehmer_id=teilnehmer_gelegt,
                               einzelspiel_id=einzelspiel.id,
                               doppler=Doppler.GELEGT.name,
                               session=session)
        if config.kontriert_id is not None:
            insert_verdopplung(teilnehmer_id=config.kontriert_id,
                               einzelspiel_id=einzelspiel.id,
                               doppler=Doppler.KONTRIERT.name,
                               session=session)
        if config.re_id is not None:
            insert_verdopplung(teilnehmer_id=config.re_id,
                               einzelspiel_id=einzelspiel.id,
                               doppler=Doppler.RE.name,
                               session=session)


class RufspielHochzeitWriter(NormalspielWriter):
    def __init__(self, calculator: RufspielHochzeitCalculator):
        super().__init__(calculator)
        self._calculator = calculator

    def write(self):
        calculator = self._calculator
        config = calculator.config
        session = Sessions.get_session()
        einzelspiel = insert_einzelspiel(runde_id=config.runde_id,
                                         ansager_id=config.ansager_id,
                                         partner_id=config.partner_id,
                                         geber_id=config.geber_id,
                                         ausspieler_id=config.teilnehmer_ids[0],
                                         mittelhand_id=config.teilnehmer_ids[1],
                                         hinterhand_id=config.teilnehmer_ids[2],
                                         geberhand_id=config.teilnehmer_ids[3],
                                         farbe=self._get_farbe(),
                                         laufende=config.laufende,
                                         spielart=self._get_spielart(),
                                         schneider=calculator.is_schneider(),
                                         schwarz=calculator.is_schwarz(),
                                         spielpunkte=calculator.get_spielpunkte(),
                                         session=session)
        self._eintrag(session, einzelspiel, config, calculator)
        session.commit()
        session.close()

    @abstractmethod
    def _get_farbe(self) -> Union[None, str]:
        pass

    @abstractmethod
    def _get_spielart(self) -> str:
        pass


class RufspielWriter(RufspielHochzeitWriter):
    def __init__(self, calculator: RufspielCalculator):
        super().__init__(calculator)
        self._calculator = calculator

    def _get_farbe(self) -> Union[None, str]:
        return self._calculator.config.rufsau.name

    def _get_spielart(self) -> str:
        return Spielart.RUFSPIEL.name


class SoloWriter(NormalspielWriter):
    def __init__(self, calculator: SoloCalculator):
        super().__init__(calculator)
        self._calculator = calculator

    def write(self):
        calculator = self._calculator
        config = calculator.config
        session = Sessions.get_session()
        einzelspiel = insert_einzelspiel(runde_id=config.runde_id,
                                         ansager_id=config.ansager_id,
                                         geber_id=config.geber_id,
                                         ausspieler_id=config.teilnehmer_ids[0],
                                         mittelhand_id=config.teilnehmer_ids[1],
                                         hinterhand_id=config.teilnehmer_ids[2],
                                         geberhand_id=config.teilnehmer_ids[3],
                                         farbe=None if config.farbe is None else config.farbe.name,
                                         laufende=config.laufende,
                                         spielart=config.spielart.name,
                                         schneider=calculator.is_schneider(),
                                         schwarz=calculator.is_schwarz(),
                                         tout=config.tout_gespielt_verloren or config.tout_gespielt_gewonnen,
                                         spielpunkte=calculator.get_spielpunkte(),
                                         session=session)
        self._eintrag(session, einzelspiel, config, calculator)
        session.commit()
        session.close()


class HochzeitWriter(RufspielHochzeitWriter):
    def __init__(self, calculator: HochzeitCalculator):
        super().__init__(calculator)
        self._calculator = calculator

    def _get_farbe(self) -> Union[None, str]:
        return None

    def _get_spielart(self) -> str:
        return Spielart.HOCHZEIT.name


class RamschWriter(Writer):
    def __init__(self, calculator: RamschCalculator):
        super().__init__()
        self._calculator = calculator

    def write(self):
        calculator = self._calculator
        config = calculator.config
        session = Sessions.get_session()
        einzelspiel = insert_einzelspiel(runde_id=config.runde_id,
                                         ansager_id=None,
                                         geber_id=config.geber_id,
                                         ausspieler_id=config.teilnehmer_ids[0],
                                         mittelhand_id=config.teilnehmer_ids[1],
                                         hinterhand_id=config.teilnehmer_ids[2],
                                         geberhand_id=config.teilnehmer_ids[3],
                                         spielart=Spielart.RAMSCH.name,
                                         spielpunkte=calculator.get_spielpunkte(),
                                         durchmarsch=config.durchmarsch,
                                         session=session)
        self._eintrag(session, einzelspiel, config, calculator)
        session.commit()
        session.close()

    @staticmethod
    def _eintrag(session, einzelspiel: Einzelspiel, config: RamschConfig, calculator: RamschCalculator):
        for teilnehmer, augen in zip(config.teilnehmer_ids, [config.ausspieler_augen,
                                                             config.mittelhand_augen,
                                                             config.hinterhand_augen,
                                                             config.geberhand_augen]):
            insert_resultat(teilnehmer_id=teilnehmer,
                            einzelspiel_id=einzelspiel.id,
                            augen=augen,
                            punkte=calculator.get_teilnehmer_id_to_punkte().get(teilnehmer),
                            gewonnen=True if teilnehmer in calculator.get_gewinner_ids() else False,
                            session=session)
        for teilnehmer_gelegt in config.gelegt_ids:
            insert_verdopplung(teilnehmer_id=teilnehmer_gelegt,
                               einzelspiel_id=einzelspiel.id,
                               doppler=Doppler.GELEGT.name,
                               session=session)
        for teilnehmer_jungfrau in config.jungfrau_ids:
            insert_verdopplung(teilnehmer_id=teilnehmer_jungfrau,
                               einzelspiel_id=einzelspiel.id,
                               doppler=Doppler.JUNGFRAU.name,
                               session=session)
