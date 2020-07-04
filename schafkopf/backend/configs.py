from dataclasses import dataclass
from typing import List, Union

from schafkopf.database.data_model import Farbgebung, Punkteconfig, Spielart


@dataclass
class Config:
    runde_id: int
    punkteconfig: Punkteconfig
    teilnehmer_ids: List[int]
    gelegt_ids: List[int]
    ansager_id: int
    kontriert_id: Union[None, int]
    re_id: Union[None, int]
    laufende: int
    spieler_augen: int
    nicht_spieler_augen: int
    schwarz: bool


@dataclass
class RufspielConfig(Config):
    rufsau: Farbgebung
    partner_id: int

    def get_spieler_ids(self) -> List[int]:
        return [t for t in self.teilnehmer_ids if t in [self.ansager_id, self.partner_id]]

    def get_nicht_spieler_ids(self) -> List[int]:
        return [t for t in self.teilnehmer_ids if t not in [self.ansager_id, self.partner_id]]


@dataclass
class SoloConfig(Config):
    spielart: Spielart
    farbe: Union[None, Farbgebung]
    tout_gespielt_gewonnen: bool
    tout_gespielt_verloren: bool


@dataclass
class RawConfig:
    runde_id: Union[None, int]
    teilnehmer_ids: Union[None, List[int]]
    gelegt_ids: List[int]
    ansager_id: Union[None, int]
    kontriert_id: List[int]
    re_id: List[int]
    laufende: Union[None, int]
    spieler_nichtspieler_augen: Union[None, int]
    augen: Union[None, int]
    schwarz: Union[None, int]


@dataclass
class RufspielRawConfig(RawConfig):
    rufsau: Union[None, str]
    partner_id: Union[None, int]


@dataclass
class SoloRawConfig(RawConfig):
    spielart: Union[None, str]
    farbe: List[str]
    tout: List[int]
