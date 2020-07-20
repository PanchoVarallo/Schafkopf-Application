from typing import Dict, List, Tuple, Any, Union

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schafkopf.backend.calculator import RufspielCalculator, SoloCalculator, HochzeitCalculator, RamschCalculator
from schafkopf.backend.configs import RufspielConfig, SoloConfig, HochzeitConfig, RamschConfig
from schafkopf.database.data_model import Teilnehmer, Runde, Base, Punkteconfig, Farbgebung, Spielart

S1 = 'Spieler_1'
S2 = 'Spieler_2'
S3 = 'Spieler_3'
S4 = 'Spieler_4'

data_rufspiel_hochzeit = [
    ([], None, None, 0, 0, True, {S1: -40, S2: -40, S3: 40, S4: 40}),
    ([], None, None, 0, 0, False, {S1: -30, S2: -30, S3: 30, S4: 30}),
    ([], None, None, 0, 29, False, {S1: -30, S2: -30, S3: 30, S4: 30}),
    ([], None, None, 0, 30, False, {S1: -30, S2: -30, S3: 30, S4: 30}),
    ([], None, None, 0, 31, False, {S1: -20, S2: -20, S3: 20, S4: 20}),
    ([], None, None, 0, 59, False, {S1: -20, S2: -20, S3: 20, S4: 20}),
    ([], None, None, 0, 60, False, {S1: -20, S2: -20, S3: 20, S4: 20}),
    ([], None, None, 0, 61, False, {S1: 20, S2: 20, S3: -20, S4: -20}),
    ([], None, None, 0, 90, False, {S1: 20, S2: 20, S3: -20, S4: -20}),
    ([], None, None, 0, 91, False, {S1: 30, S2: 30, S3: -30, S4: -30}),
    ([], None, None, 0, 120, True, {S1: 40, S2: 40, S3: -40, S4: -40}),
    ([], None, None, 3, 0, True, {S1: -70, S2: -70, S3: 70, S4: 70}),
    ([], None, None, 3, 29, False, {S1: -60, S2: -60, S3: 60, S4: 60}),
    ([], None, None, 3, 30, False, {S1: -60, S2: -60, S3: 60, S4: 60}),
    ([], None, None, 3, 59, False, {S1: -50, S2: -50, S3: 50, S4: 50}),
    ([], None, None, 3, 60, False, {S1: -50, S2: -50, S3: 50, S4: 50}),
    ([], None, None, 3, 61, False, {S1: 50, S2: 50, S3: -50, S4: -50}),
    ([], None, None, 0, 89, False, {S1: 20, S2: 20, S3: -20, S4: -20}),
    ([], None, None, 0, 90, False, {S1: 20, S2: 20, S3: -20, S4: -20}),
    ([], None, None, 0, 91, False, {S1: 30, S2: 30, S3: -30, S4: -30}),
    ([], None, None, 6, 120, True, {S1: 100, S2: 100, S3: -100, S4: -100}),
    ([S1], None, None, 0, 0, True, {S1: -80, S2: -80, S3: 80, S4: 80}),
    ([S2], None, None, 0, 29, False, {S1: -60, S2: -60, S3: 60, S4: 60}),
    ([S3], None, None, 0, 30, False, {S1: -60, S2: -60, S3: 60, S4: 60}),
    ([S4], None, None, 0, 59, False, {S1: -40, S2: -40, S3: 40, S4: 40}),
    ([S1], S3, None, 0, 60, False, {S1: -80, S2: -80, S3: 80, S4: 80}),
    ([S1], S3, S2, 0, 61, False, {S1: 160, S2: 160, S3: -160, S4: -160}),
    ([S1, S2], None, None, 0, 0, True, {S1: -160, S2: -160, S3: 160, S4: 160}),
    ([S1, S2, S3, S4], None, None, 0, 0, True, {S1: -640, S2: -640, S3: 640, S4: 640}),
]


@pytest.mark.parametrize(
    ('gelegt_teilnehmer_names',
     'kontriert_teilnehmer_name',
     're_teilnehmer_name',
     'laufende',
     'spieler_augen',
     'schwarz',
     'expected'), data_rufspiel_hochzeit)
def test_rufspiele(gelegt_teilnehmer_names: List[str],
                   kontriert_teilnehmer_name: Union[None, str],
                   re_teilnehmer_name: Union[None, str],
                   laufende: int,
                   spieler_augen: int,
                   schwarz: bool,
                   expected: Dict[str, int]):
    runde, ansager, partner, gegner1, gegner2 = init_in_memory_database()
    teilnehmers = [ansager, partner, gegner1, gegner2]

    kontriert_id = None if kontriert_teilnehmer_name is None else \
        transform_teilnehmer_names_to_teilnehmer_ids([kontriert_teilnehmer_name], teilnehmers)[0]
    re_id = None if re_teilnehmer_name is None else \
        transform_teilnehmer_names_to_teilnehmer_ids([re_teilnehmer_name], teilnehmers)[0]
    c = RufspielConfig(runde_id=runde.id,
                       punkteconfig=runde.punkteconfig,
                       geber_id=ansager.id,
                       teilnehmer_ids=[ansager.id, partner.id, gegner1.id, gegner2.id],
                       gelegt_ids=transform_teilnehmer_names_to_teilnehmer_ids(gelegt_teilnehmer_names, teilnehmers),
                       ansager_id=ansager.id,
                       rufsau=Farbgebung.BLATT,
                       kontriert_id=kontriert_id,
                       re_id=re_id,
                       partner_id=partner.id,
                       laufende=laufende,
                       spieler_augen=spieler_augen,
                       nicht_spieler_augen=120 - spieler_augen,
                       schwarz=schwarz)
    rufspiel = RufspielCalculator(c)
    result = rufspiel.get_teilnehmer_id_to_punkte()
    assert transform_dc_teilnehmer_id_to_teilnehmer_name(result, teilnehmers) == expected


data_solo = [
    ([], None, None, 0, False, False, Spielart.WENZ, None, 0, True, {S1: -210, S2: 70, S3: 70, S4: 70}),
    ([], None, None, 0, False, False, Spielart.WENZ, None, 0, False, {S1: -180, S2: 60, S3: 60, S4: 60}),
    ([], None, None, 0, False, False, Spielart.GEIER, None, 29, False, {S1: -180, S2: 60, S3: 60, S4: 60}),
    ([], None, None, 0, False, False, Spielart.FARBSOLO, Farbgebung.EICHEL, 30, False,
     {S1: -180, S2: 60, S3: 60, S4: 60}),
    ([], None, None, 0, False, False, Spielart.FARBSOLO, Farbgebung.BLATT, 31, False,
     {S1: -150, S2: 50, S3: 50, S4: 50}),
    (
        [], None, None, 0, False, False, Spielart.FARBSOLO, Farbgebung.HERZ, 59, False,
        {S1: -150, S2: 50, S3: 50, S4: 50}),
    ([], None, None, 0, False, False, Spielart.FARBSOLO, Farbgebung.SCHELLEN, 60, False,
     {S1: -150, S2: 50, S3: 50, S4: 50}),
    ([], None, None, 0, False, False, Spielart.WENZ, None, 61, False, {S1: 150, S2: -50, S3: -50, S4: -50}),
    ([], None, None, 0, False, False, Spielart.GEIER, None, 89, False, {S1: 150, S2: -50, S3: -50, S4: -50}),
    ([], None, None, 0, False, False, Spielart.FARBSOLO, Farbgebung.EICHEL, 90, False,
     {S1: 150, S2: -50, S3: -50, S4: -50}),
    ([], None, None, 0, False, False, Spielart.FARBSOLO, Farbgebung.BLATT, 91, False,
     {S1: 180, S2: -60, S3: -60, S4: -60}),
    ([], None, None, 0, False, False, Spielart.FARBSOLO, Farbgebung.HERZ, 120, True,
     {S1: 210, S2: -70, S3: -70, S4: -70}),
    ([], None, None, 2, False, False, Spielart.WENZ, None, 61, False, {S1: 210, S2: -70, S3: -70, S4: -70}),
    ([S1, S2], None, None, 4, False, False, Spielart.WENZ, None, 91, False, {S1: 1200, S2: -400, S3: -400, S4: -400}),
    # Tout Spiele
    ([], None, None, 0, True, False, Spielart.WENZ, None, 120, False, {S1: 300, S2: -100, S3: -100, S4: -100}),
    ([], None, None, 0, False, True, Spielart.WENZ, None, 120, False, {S1: -300, S2: 100, S3: 100, S4: 100}),
    ([], None, None, 0, False, True, Spielart.WENZ, None, 0, False, {S1: -300, S2: 100, S3: 100, S4: 100}),
    ([S1, S2], None, None, 0, False, True, Spielart.WENZ, None, 0, False, {S1: -1200, S2: 400, S3: 400, S4: 400}),
    ([], None, None, 2, True, False, Spielart.WENZ, None, 120, False, {S1: 420, S2: -140, S3: -140, S4: -140}),
    ([], None, None, 3, False, True, Spielart.WENZ, None, 98, False, {S1: -480, S2: 160, S3: 160, S4: 160}),
]


@pytest.mark.parametrize(
    ('gelegt_teilnehmer_names',
     'kontriert_teilnehmer_name',
     're_teilnehmer_name',
     'laufende',
     'tout_gespielt_gewonnen',
     'tout_gespielt_verloren',
     'spielart',
     'farbe',
     'spieler_augen',
     'schwarz',
     'expected'), data_solo)
def test_solo(gelegt_teilnehmer_names: List[str],
              kontriert_teilnehmer_name: Union[None, str],
              re_teilnehmer_name: Union[None, str],
              laufende: int,
              tout_gespielt_gewonnen: bool,
              tout_gespielt_verloren: bool,
              spielart: Spielart,
              farbe: Union[None, Farbgebung],
              spieler_augen: int,
              schwarz: bool,
              expected: Dict[str, int]):
    runde, spieler_1, gegner_1, gegner_2, gegner3 = init_in_memory_database()
    teilnehmers = [spieler_1, gegner_1, gegner_2, gegner3]

    kontriert_id = None if kontriert_teilnehmer_name is None else \
        transform_teilnehmer_names_to_teilnehmer_ids([kontriert_teilnehmer_name], teilnehmers)[0]
    re_id = None if re_teilnehmer_name is None else \
        transform_teilnehmer_names_to_teilnehmer_ids([re_teilnehmer_name], teilnehmers)[0]
    c = SoloConfig(runde_id=runde.id,
                   punkteconfig=runde.punkteconfig,
                   geber_id=spieler_1.id,
                   teilnehmer_ids=[spieler_1.id, gegner_1.id, gegner_2.id, gegner3.id],
                   gelegt_ids=transform_teilnehmer_names_to_teilnehmer_ids(gelegt_teilnehmer_names, teilnehmers),
                   ansager_id=spieler_1.id,
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
    solo = SoloCalculator(c)
    result = solo.get_teilnehmer_id_to_punkte()
    assert transform_dc_teilnehmer_id_to_teilnehmer_name(result, teilnehmers) == expected


@pytest.mark.parametrize(
    ('gelegt_teilnehmer_names',
     'kontriert_teilnehmer_name',
     're_teilnehmer_name',
     'laufende',
     'spieler_augen',
     'schwarz',
     'expected'), data_rufspiel_hochzeit)
def test_hochzeit(gelegt_teilnehmer_names: List[str],
                  kontriert_teilnehmer_name: Union[None, str],
                  re_teilnehmer_name: Union[None, str],
                  laufende: int,
                  spieler_augen: int,
                  schwarz: bool,
                  expected: Dict[str, int]):
    runde, ansager, partner, gegner1, gegner2 = init_in_memory_database()
    teilnehmers = [ansager, partner, gegner1, gegner2]

    kontriert_id = None if kontriert_teilnehmer_name is None else \
        transform_teilnehmer_names_to_teilnehmer_ids([kontriert_teilnehmer_name], teilnehmers)[0]
    re_id = None if re_teilnehmer_name is None else \
        transform_teilnehmer_names_to_teilnehmer_ids([re_teilnehmer_name], teilnehmers)[0]
    c = HochzeitConfig(runde_id=runde.id,
                       punkteconfig=runde.punkteconfig,
                       geber_id=ansager.id,
                       teilnehmer_ids=[ansager.id, partner.id, gegner1.id, gegner2.id],
                       gelegt_ids=transform_teilnehmer_names_to_teilnehmer_ids(gelegt_teilnehmer_names, teilnehmers),
                       ansager_id=ansager.id,
                       kontriert_id=kontriert_id,
                       re_id=re_id,
                       partner_id=partner.id,
                       laufende=laufende,
                       spieler_augen=spieler_augen,
                       nicht_spieler_augen=120 - spieler_augen,
                       schwarz=schwarz)
    hochzeit = HochzeitCalculator(c)
    result = hochzeit.get_teilnehmer_id_to_punkte()
    assert transform_dc_teilnehmer_id_to_teilnehmer_name(result, teilnehmers) == expected


data_ramsch = [
    ([], [], None, S1, {S1: -60, S2: 20, S3: 20, S4: 20}),
    ([], [], None, S2, {S1: 20, S2: -60, S3: 20, S4: 20}),
    ([], [], None, S3, {S1: 20, S2: 20, S3: -60, S4: 20}),
    ([], [], None, S4, {S1: 20, S2: 20, S3: 20, S4: -60}),
    ([S1], [], None, S1, {S1: -120, S2: 40, S3: 40, S4: 40}),
    ([S1, S2], [S3], None, S1, {S1: -480, S2: 160, S3: 160, S4: 160}),
    ([], [], S1, None, {S1: 150, S2: -50, S3: -50, S4: -50}),
    ([S2], [], S1, None, {S1: 300, S2: -100, S3: -100, S4: -100}),
    ([S1, S3], [], S1, None, {S1: 600, S2: -200, S3: -200, S4: -200}),
]


@pytest.mark.parametrize(
    ('gelegt_teilnehmer_names',
     'jungfrau_teilnehmer_names',
     'durchmarsch_name',
     'verlierer_name',
     'expected'), data_ramsch)
def test_ramsch(gelegt_teilnehmer_names: List[str],
                jungfrau_teilnehmer_names: List[str],
                durchmarsch_name: Union[None, str],
                verlierer_name: Union[None, str],
                expected: Dict[str, int]):
    runde, ansager, partner, gegner1, gegner2 = init_in_memory_database()
    teilnehmers = [ansager, partner, gegner1, gegner2]

    verlierer_id = None if verlierer_name is None else \
        transform_teilnehmer_names_to_teilnehmer_ids([verlierer_name], teilnehmers)[0]
    durchmarsch_id = None if durchmarsch_name is None else \
        transform_teilnehmer_names_to_teilnehmer_ids([durchmarsch_name], teilnehmers)[0]
    c = RamschConfig(runde_id=runde.id,
                     punkteconfig=runde.punkteconfig,
                     geber_id=ansager.id,
                     teilnehmer_ids=[ansager.id, partner.id, gegner1.id, gegner2.id],
                     gelegt_ids=transform_teilnehmer_names_to_teilnehmer_ids(gelegt_teilnehmer_names, teilnehmers),
                     jungfrau_ids=transform_teilnehmer_names_to_teilnehmer_ids(jungfrau_teilnehmer_names, teilnehmers),
                     ausspieler_augen=30,
                     mittelhand_augen=30,
                     hinterhand_augen=30,
                     geberhand_augen=30,
                     verlierer_id=verlierer_id,
                     durchmarsch_id=durchmarsch_id,
                     durchmarsch=True if durchmarsch_id is not None else False)
    ramsch = RamschCalculator(c)
    result = ramsch.get_teilnehmer_id_to_punkte()
    assert transform_dc_teilnehmer_id_to_teilnehmer_name(result, teilnehmers) == expected


def transform_teilnehmer_names_to_teilnehmer_ids(inputs: List[str], teilnehmer: List[Teilnehmer]) -> List[int]:
    return [{s.name: s.id for s in teilnehmer}[i] for i in inputs]


def transform_dc_teilnehmer_id_to_teilnehmer_name(inputs: Dict[int, Any], teilnehmer: List[Teilnehmer]) -> Dict[
    str, Any]:
    return {{s.id: s.name for s in teilnehmer}[i]: inputs[i] for i in inputs}


def init_in_memory_database() -> Tuple[Runde, Teilnehmer, Teilnehmer, Teilnehmer, Teilnehmer]:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    my_session = sessionmaker(bind=engine)
    session = my_session()

    # After this setting, Hochzeit should return the same results as rufspiel
    punkteconfig = Punkteconfig(hochzeit=20.0)
    session.add(punkteconfig)
    session.commit()
    runde = Runde(name="Sonntagsspiel", punkteconfig_id=punkteconfig.id, ort='Nürnberg')

    spieler_1 = Teilnehmer(vorname='ansager_vorname', nachname='ansager_nachname', name=S1)
    spieler_2 = Teilnehmer(vorname='partner_vorname', nachname='partner_nachname', name=S2)
    spieler_3 = Teilnehmer(vorname='erster_geg_vorname', nachname='erster_geg_nachname', name=S3)
    spieler_4 = Teilnehmer(vorname='zweiter_geg_vorname', nachname='zweiter_geg_nachname', name=S4)
    session.add_all([spieler_1, spieler_2, spieler_3, spieler_4] + [runde])
    session.commit()
    return runde, spieler_1, spieler_2, spieler_3, spieler_4
