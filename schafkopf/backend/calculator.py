from abc import abstractmethod
from typing import List, Dict

from schafkopf.backend.configs import RufspielConfig, SoloConfig, Config


class Calculator:
    def __init__(self, config: Config):
        self._config = config

    @abstractmethod
    def get_spielpunkte(self) -> int:
        pass

    @abstractmethod
    def get_gewinner_ids(self) -> List[int]:
        pass

    def get_verlierer_ids(self) -> List[int]:
        return [s for s in self._config.teilnehmer_ids if s not in self.get_gewinner_ids()]

    def is_schneider(self) -> bool:
        return True if self._config.spieler_augen >= 91 or self._config.spieler_augen <= 30 else False

    def is_schwarz(self) -> bool:
        return self._config.schwarz

    def get_punkte_laufende(self) -> int:
        return self._config.punkteconfig.laufende * self._config.laufende

    @abstractmethod
    def get_teilnehmer_id_to_punkte(self) -> Dict:
        pass

    @abstractmethod
    def _get_verdopplung(self) -> int:
        pass


class RufspielCalculator(Calculator):
    def __init__(self, config: RufspielConfig):
        super().__init__(config)
        self._config = config

    @property
    def config(self) -> RufspielConfig:
        return self._config

    def get_spielpunkte(self) -> int:
        punkteconfig = self._config.punkteconfig
        punkte = punkteconfig.rufspiel
        punkte = punkte + punkteconfig.schneider if self.is_schneider() else punkte
        punkte = punkte + punkteconfig.schwarz if self.is_schwarz() else punkte
        punkte += self.get_punkte_laufende()
        return punkte * self._get_verdopplung()

    def get_gewinner_ids(self) -> List[int]:
        spieler = [self._config.ansager_id, self._config.partner_id]
        if self._config.spieler_augen >= 61:
            return [s for s in self._config.teilnehmer_ids if s in spieler]
        else:
            return [s for s in self._config.teilnehmer_ids if s not in spieler]

    def get_teilnehmer_id_to_punkte(self) -> Dict:
        dc = {s: self.get_spielpunkte() for s in self._config.teilnehmer_ids if s in self.get_gewinner_ids()}
        dc.update({s: -self.get_spielpunkte() for s in self._config.teilnehmer_ids if s in self.get_verlierer_ids()})
        return dc

    def _get_verdopplung(self) -> int:
        kontriert_und_re = len(['_' for d in [self._config.kontriert_id, self._config.re_id] if d is not None])
        return 2 ** (len(self._config.gelegt_ids) + kontriert_und_re)


class SoloCalculator(Calculator):
    def __init__(self, config: SoloConfig):
        super().__init__(config)
        self._config = config

    @property
    def config(self) -> SoloConfig:
        return self._config

    def get_spielpunkte(self) -> int:
        punkteconfig = self._config.punkteconfig
        punkte = punkteconfig.solo
        punkte = punkte + punkteconfig.schneider if self.is_schneider() else punkte
        punkte = punkte + punkteconfig.schwarz if self.is_schwarz() else punkte
        punkte += self.get_punkte_laufende()
        return punkte * self._get_verdopplung()

    def is_schneider(self) -> bool:
        if self._config.tout_gespielt_gewonnen or self._config.tout_gespielt_verloren:
            return False
        return super().is_schneider()

    def get_gewinner_ids(self) -> List[int]:
        spieler = [self._config.ansager_id]
        if self._config.tout_gespielt_gewonnen:
            return [s for s in self._config.teilnehmer_ids if s in spieler]
        if self._config.tout_gespielt_verloren:
            return [s for s in self._config.teilnehmer_ids if s not in spieler]
        if self._config.spieler_augen >= 61:
            return [s for s in self._config.teilnehmer_ids if s in spieler]
        else:
            return [s for s in self._config.teilnehmer_ids if s not in spieler]

    def get_teilnehmer_id_to_punkte(self) -> Dict:
        spielpunkte = self.get_spielpunkte()
        if self._config.ansager_id in self.get_gewinner_ids():
            dc = {self._config.ansager_id: spielpunkte * 3.0}
            dc.update({s: -spielpunkte for s in self._config.teilnehmer_ids if s in self.get_verlierer_ids()})
        else:
            dc = {self._config.ansager_id: - self.get_spielpunkte() * 3.0}
            dc.update({s: spielpunkte for s in self._config.teilnehmer_ids if s in self.get_gewinner_ids()})
        return dc

    def _get_verdopplung(self) -> int:
        kontriert_und_re = len(['_' for d in [self._config.kontriert_id, self._config.re_id] if d is not None])
        tout = self._config.tout_gespielt_verloren + self._config.tout_gespielt_gewonnen
        return 2 ** (len(self._config.gelegt_ids) + kontriert_und_re + tout)
