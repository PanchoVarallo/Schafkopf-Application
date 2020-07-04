from abc import abstractmethod
from typing import List, Union

from schafkopf.backend.configs import RufspielRawConfig, RufspielConfig, SoloRawConfig, SoloConfig
from schafkopf.database.data_model import Farbgebung, Spielart
from schafkopf.database.queries import get_teilnehmer_name_by_id, get_punkteconfig_by_runde_id


class Validator:
    def __init__(self):
        self._validated = False
        self._validation_messages = []
        self._validated_config = None
        self._validate()

    @property
    def validation_messages(self) -> List[str]:
        return self._validation_messages

    @abstractmethod
    def _validate(self):
        pass

    @staticmethod
    def _integer(var: Union[None, int]) -> int:
        return 0 if var is None else var

    @staticmethod
    def _boolean(var: Union[None, int]) -> Union[None, bool]:
        return None if var is None or var not in [0, 1] else True if var == 1 else False

    @staticmethod
    def _list(var: Union[None, List[int]]) -> List[int]:
        return [] if var in [None, []] else var

    @staticmethod
    def _validate_kontra_and_re(m: List[str], kontriert_id: Union[None, List[int]], re_id: Union[None, List[int]]):
        if len(kontriert_id) >= 2:
            m.append(f'Maximal ein Teilnehmer kann Kontra geben. Momentan: {len(kontriert_id)}.')
        if len(re_id) >= 2:
            m.append(f'Maximal ein Teilnehmer kann Re geben. Momentan: {len(re_id)}.')
        if len(kontriert_id) == 0 and len(re_id) == 1:
            teilnehmer_re = re_id[0]
            m.append(
                f'Re darf nicht ohne Kontra geben werden. Momentan Re: {get_teilnehmer_name_by_id(teilnehmer_re)}')


class RufspielValidator(Validator):
    def __init__(self, raw_config: RufspielRawConfig):
        self._raw_config = raw_config
        super().__init__()

    @property
    def validated_config(self) -> RufspielConfig:
        if self._validated:
            return self._validated_config
        else:
            raise Exception(f'Validation of Rufspiel not successful. Cannot return config.')

    def _validate(self):
        runde_id = self._raw_config.runde_id
        geber_id = self._raw_config.geber_id
        teilnehmer_ids = self._list(self._raw_config.teilnehmer_ids)
        gelegt_ids = self._list(self._raw_config.gelegt_ids)
        ansager_id = self._raw_config.ansager_id
        rufsau = None if self._raw_config.rufsau is None else Farbgebung[self._raw_config.rufsau]
        kontriert_id = self._raw_config.kontriert_id
        re_id = self._raw_config.re_id
        partner_id = self._raw_config.partner_id
        laufende = self._integer(self._raw_config.laufende)
        spieler_nichtspieler_augen = self._boolean(self._raw_config.spieler_nichtspieler_augen)
        augen = self._raw_config.augen
        schwarz = self._boolean(self._raw_config.schwarz)

        m = []
        pflichtfeld = [(runde_id, 'Runde'), (ansager_id, 'Ansager'), (rufsau, 'Rufsau'), (partner_id, 'Partner')]
        [m.append(f'Kein/e {pflicht[1]} gewählt.') for pflicht in pflichtfeld if pflicht[0] is None]
        self._validate_kontra_and_re(m, kontriert_id, re_id)
        if ansager_id is not None and partner_id is not None:
            if partner_id != ansager_id:
                if len(kontriert_id) == 1 and ansager_id is not None and partner_id is not None:
                    if kontriert_id[0] == ansager_id:
                        m.append(
                            f'Spieler darf nicht Kontra geben. Momentan: {get_teilnehmer_name_by_id(ansager_id)}.')
                    if kontriert_id[0] == partner_id:
                        m.append(
                            f'Spieler darf nicht Kontra geben. Momentan: {get_teilnehmer_name_by_id(partner_id)}.')
                if len(re_id) == 1 and ansager_id is not None and partner_id is not None:
                    nicht_spieler = [t for t in teilnehmer_ids if t not in [ansager_id, partner_id]]
                    if re_id[0] == nicht_spieler[0]:
                        m.append(f'Nicht-Spieler darf nicht Re geben. '
                                 f'Momentan: {get_teilnehmer_name_by_id(nicht_spieler[0])}.')
                    if re_id[0] == nicht_spieler[1]:
                        m.append(f'Nicht-Spieler darf nicht Re geben. '
                                 f'Momentan: {get_teilnehmer_name_by_id(nicht_spieler[1])}.')
            else:
                m.append(f'Ansager und Partner identisch: {get_teilnehmer_name_by_id(ansager_id)}.')
        if laufende not in [0, 3, 4, 5, 6, 7, 8] or laufende is None:
            m.append(f'Ungültige Anzahl an Laufenden. Bitte 0, 3, 4, 5, 6, 7 oder 8 wählen.')
        if augen is None:
            m.append(f'Ungültige Augen angegeben. Bitte eine Zahl von 0 - 120 angeben.')
        else:
            spieler_augen = augen if spieler_nichtspieler_augen == 1 else 120 - augen
            if schwarz and spieler_augen not in [0, 120]:
                m.append(f'Ein Spiel kann nur Schwarz sein, wenn 0 oder 120 Augen erreicht werden.')

        if len(m) == 0:
            spieler_augen = augen if spieler_nichtspieler_augen == 1 else 120 - augen
            kontriert_id = None if len(kontriert_id) == 0 else kontriert_id[0]
            re_id = None if len(re_id) == 0 else re_id[0]
            self._validated = True
            self._validated_config = RufspielConfig(runde_id=runde_id,
                                                    punkteconfig=get_punkteconfig_by_runde_id(runde_id),
                                                    geber_id=geber_id,
                                                    teilnehmer_ids=teilnehmer_ids,
                                                    gelegt_ids=gelegt_ids,
                                                    ansager_id=ansager_id,
                                                    rufsau=rufsau,
                                                    kontriert_id=kontriert_id,
                                                    re_id=re_id,
                                                    partner_id=partner_id,
                                                    laufende=laufende,
                                                    spieler_augen=spieler_augen,
                                                    nicht_spieler_augen=120 - spieler_augen,
                                                    schwarz=schwarz)
        else:
            self._validation_messages = m


class SoloValidator(Validator):
    def __init__(self, raw_config: SoloRawConfig):
        self._raw_config = raw_config
        super().__init__()

    @property
    def validated_config(self) -> SoloConfig:
        if self._validated:
            return self._validated_config
        else:
            raise Exception(f'Validation of Solo not successful. Cannot return config.')

    def _validate(self):
        runde_id = self._raw_config.runde_id
        geber_id = self._raw_config.geber_id
        teilnehmer_ids = self._list(self._raw_config.teilnehmer_ids)
        gelegt_ids = self._list(self._raw_config.gelegt_ids)
        ansager_id = self._raw_config.ansager_id
        spielart = None if self._raw_config.spielart is None else Spielart[self._raw_config.spielart]
        kontriert_id = self._raw_config.kontriert_id
        re_id = self._raw_config.re_id
        farbe = self._raw_config.farbe
        tout_gespielt_gewonnen = False if 0 not in self._raw_config.tout else True
        tout_gespielt_verloren = False if 1 not in self._raw_config.tout else True
        laufende = self._integer(self._raw_config.laufende)
        spieler_nichtspieler_augen = self._boolean(self._raw_config.spieler_nichtspieler_augen)
        augen = self._raw_config.augen
        schwarz = self._boolean(self._raw_config.schwarz)

        m = []
        pflichtfeld = [(runde_id, 'Runde'), (ansager_id, 'Ansager'), (spielart, 'Solo')]
        [m.append(f'Kein/e {pflicht[1]} gewählt.') for pflicht in pflichtfeld if
         pflicht[0] is None]
        self._validate_kontra_and_re(m, kontriert_id, re_id)
        if len(farbe) > 1:
            m.append(f'Es darf maximal eine Farbe gewählt werden. Momentan: {len(farbe)}')
        elif len(farbe) == 1 and spielart in [Spielart.WENZ, Spielart.GEYER]:
            m.append(f'Bei {spielart.name.lower().capitalize()} darf keine Farbe gewählt werden.')
        elif len(farbe) == 0 and spielart in [Spielart.FARBSOLO]:
            m.append(f'Bei Farbsolo muss eine Farbe gewählt werden.')
        if spielart in [Spielart.FARBSOLO] and laufende not in [0, 3, 4, 5, 6, 7, 8]:
            m.append(f'Ungültige Anzahl an Laufenden für Farbsolo. Bitte 0, 3, 4, 5, 6, 7 oder 8 wählen.')
        if spielart in [Spielart.GEYER, Spielart.WENZ] and laufende not in [0, 2, 3, 4]:
            m.append(f'Ungültige Anzahl an Laufenden für {spielart.name.lower().capitalize()}. '
                     f'Bitte 0, 2, 3 oder 4 wählen.')
        if ansager_id is not None and len(kontriert_id) == 1 and kontriert_id[0] == ansager_id:
            m.append(f'Spieler darf nicht Kontra geben. Momentan: {get_teilnehmer_name_by_id(ansager_id)}.')
        if len(re_id) == 1 and ansager_id is not None:
            nicht_spieler = [t for t in teilnehmer_ids if t not in [ansager_id]]
            for single_re_id in re_id:
                if single_re_id in nicht_spieler:
                    m.append(f'Nicht-Spieler darf nicht Re geben. Momentan: '
                             f'{get_teilnehmer_name_by_id(nicht_spieler[0])}.')
        if tout_gespielt_gewonnen and tout_gespielt_verloren:
            m.append("Ein Tout kann nur gewonnen oder verloren werden. Bitte maximal einen Ausgang des Touts auswählen")

        tout_gespielt = True if ((tout_gespielt_gewonnen is True and tout_gespielt_verloren is False) or (
                tout_gespielt_gewonnen is False and tout_gespielt_verloren is True)) else False
        if tout_gespielt and schwarz:
            m.append("Ein Tout Spiel kann nicht mit Schwarz gekennzeichnet werden.")

        if augen is None:
            m.append(f'Ungültige Augen angegeben. Bitte eine Zahl von 0 - 120 angeben.')
        else:
            spieler_augen = augen if spieler_nichtspieler_augen == 1 else 120 - augen
            if tout_gespielt and tout_gespielt_gewonnen and spieler_augen < 120:
                m.append('Ein vom Spieler gewonnenes Tout-Spiel impliziert 120 Augen für den Spieler und 0 Augen '
                         'für die Nicht-Spieler. Bitte Augenzahl korrigieren.')
            if not tout_gespielt and spieler_augen not in [0, 120] and schwarz:
                m.append(f'Ein Spiel kann nur Schwarz sein, wenn 0 oder 120 Augen erreicht werden.')
        if len(m) == 0:
            spieler_augen = augen if spieler_nichtspieler_augen == 1 else 120 - augen
            kontriert_id = None if len(kontriert_id) == 0 else kontriert_id[0]
            re_id = None if len(re_id) == 0 else re_id[0]
            farbe = None if len(farbe) == 0 else Farbgebung[self._raw_config.farbe[0]]
            self._validated = True
            self._validated_config = SoloConfig(runde_id=runde_id,
                                                punkteconfig=get_punkteconfig_by_runde_id(runde_id),
                                                geber_id=geber_id,
                                                teilnehmer_ids=teilnehmer_ids,
                                                gelegt_ids=gelegt_ids,
                                                ansager_id=ansager_id,
                                                spielart=spielart,
                                                kontriert_id=kontriert_id,
                                                re_id=re_id,
                                                farbe=farbe,
                                                tout_gespielt_gewonnen=tout_gespielt_gewonnen,
                                                tout_gespielt_verloren=tout_gespielt_verloren,
                                                laufende=laufende,
                                                spieler_augen=spieler_augen,
                                                nicht_spieler_augen=120 - spieler_augen,
                                                schwarz=schwarz)
        else:
            self._validation_messages = m
