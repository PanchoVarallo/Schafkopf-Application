import datetime
from typing import Union, List

import pandas as pd
from sqlalchemy import literal
from sqlalchemy.orm import sessionmaker

from schafkopf.database.data_model import Teilnehmer, Runde, Punkteconfig, Einzelspiel, Resultat, Verdopplung
from schafkopf.database.session import Sessions


def get_teilnehmer(dataframe: bool = False, session: sessionmaker() = None) -> Union[List[Teilnehmer], pd.DataFrame]:
    actual_session = Sessions.get_session() if session is None else session
    query = actual_session.query(Teilnehmer).order_by(Teilnehmer.nachname.asc(), Teilnehmer.vorname.asc())
    teilnehmer = query.all() if not dataframe else pd.read_sql(query.statement, actual_session.bind)
    _close_session(actual_session, session)
    return teilnehmer


def get_teilnehmer_by_id(teilnehmer_id: Union[None, int], session: sessionmaker() = None) -> Union[None, Teilnehmer]:
    actual_session = _build_session(session)
    if teilnehmer_id is None:
        _close_session(actual_session, session)
        return None
    teilnehmer = actual_session.query(Teilnehmer).filter(Teilnehmer.id == teilnehmer_id).all()
    _close_session(actual_session, session)
    return teilnehmer[0]


def get_teilnehmers_by_ids(teilnehmer_ids: List[Union[None, int]],
                           session: sessionmaker() = None) -> List[Union[None, Teilnehmer]]:
    actual_session = _build_session(session)
    teilnehmers = actual_session.query(Teilnehmer).filter(Teilnehmer.id.in_(teilnehmer_ids)).all()
    _close_session(actual_session, session)
    return teilnehmers


def get_teilnehmer_name_by_id(teilnehmer_id: Union[None, int], session: sessionmaker() = None) -> Union[None, str]:
    actual_session = _build_session(session)
    teilnehmer = get_teilnehmer_by_id(teilnehmer_id, actual_session)
    _close_session(actual_session, session)
    if teilnehmer is None:
        return None
    return teilnehmer.name


def get_runden(active: bool = True, dataframe: bool = False,
               session: sessionmaker() = None) -> Union[List[Runde], pd.DataFrame]:
    actual_session = _build_session(session)
    if active:
        query = actual_session.query(Runde).filter(Runde.is_active == active).order_by(Runde.datum.asc())
    else:
        query = actual_session.query(Runde).order_by(Runde.created_on.asc())
    runden = query.all() if not dataframe else pd.read_sql(query.statement, actual_session.bind)
    _close_session(actual_session, session)
    return runden


def get_resultate(dataframe: bool = False,
                  session: sessionmaker() = None) -> Union[List[Resultat], pd.DataFrame]:
    actual_session = Sessions.get_session() if session is None else session
    query = actual_session.query(Resultat)
    resultate = query.all() if not dataframe else pd.read_sql(query.statement, actual_session.bind)
    _close_session(actual_session, session)
    return resultate


def get_resultate_by_runde_ids(runde_ids: List[int],
                               active: bool = True,
                               dataframe: bool = False,
                               session: sessionmaker() = None) -> Union[None, List[Resultat], pd.DataFrame]:
    actual_session = Sessions.get_session() if session is None else session
    einzelspiel_ids = get_einzelspiel_ids_by_runde_ids(runde_ids=runde_ids, active=active, session=actual_session)
    resultate = get_resultate_by_einzelspiele_ids(einzelspiel_ids=einzelspiel_ids, dataframe=dataframe,
                                                  session=actual_session)
    _close_session(actual_session, session)
    return resultate


def get_resultate_by_einzelspiele_ids(einzelspiel_ids: List[int],
                                      dataframe: bool = False,
                                      session: sessionmaker() = None) -> Union[None, List[Resultat], pd.DataFrame]:
    actual_session = Sessions.get_session() if session is None else session
    query = actual_session.query(Resultat).filter(Resultat.einzelspiel_id.in_(einzelspiel_ids))
    resultate = query.all() if not dataframe else pd.read_sql(query.statement, actual_session.bind)
    _close_session(actual_session, session)
    return resultate


def get_resultate_by_teilnehmer_ids(teilnehmer_ids: List[int],
                                    dataframe: bool = False,
                                    session: sessionmaker() = None) -> Union[None, List[Resultat], pd.DataFrame]:
    actual_session = Sessions.get_session() if session is None else session
    query = actual_session.query(Resultat).filter(Resultat.teilnehmer_id.in_(teilnehmer_ids))
    resultate = query.all() if not dataframe else pd.read_sql(query.statement, actual_session.bind)
    _close_session(actual_session, session)
    return resultate


def insert_resultat(teilnehmer_id: int,
                    einzelspiel_id: int,
                    augen: float,
                    punkte: float,
                    gewonnen: bool,
                    session: sessionmaker() = None) -> Resultat:
    actual_session = _build_session(session)
    resultat = Resultat(teilnehmer_id=teilnehmer_id, einzelspiel_id=einzelspiel_id, augen=augen,
                        punkte=punkte, gewonnen=gewonnen)
    actual_session.add(resultat)
    if session is None:
        actual_session.commit()
        actual_session.close()
    return resultat


def get_punkteconfigs(dataframe: bool = False,
                      session: sessionmaker() = None) -> Union[List[Punkteconfig], pd.DataFrame]:
    actual_session = Sessions.get_session() if session is None else session
    query = actual_session.query(Punkteconfig)
    punkteconfig = query.all() if not dataframe else pd.read_sql(query.statement, actual_session.bind)
    _close_session(actual_session, session)
    return punkteconfig


def get_punkteconfig_by_runde_id(runde_id: Union[None, int],
                                 session: sessionmaker() = None) -> Union[None, Punkteconfig]:
    actual_session = _build_session(session)
    if runde_id is None:
        _close_session(actual_session, session)
        return None
    runde = actual_session.query(Runde).filter(Runde.id == runde_id).all()
    punkteconfig = runde[0].punkteconfig
    _close_session(actual_session, session)
    return punkteconfig


def get_punkteconfig_by_name(name: Union[None, str],
                             session: sessionmaker() = None) -> Union[None, Punkteconfig]:
    actual_session = _build_session(session)
    if name is None:
        _close_session(actual_session, session)
        return None
    punkteconfig = actual_session.query(Punkteconfig).filter(Punkteconfig.name == name).all()
    _close_session(actual_session, session)
    return punkteconfig[0] if len(punkteconfig) == 1 else None


def get_einzelspiele(active: bool = True,
                     dataframe: bool = False,
                     session: sessionmaker() = None) -> Union[List[Einzelspiel], pd.DataFrame]:
    actual_session = Sessions.get_session() if session is None else session
    if active:
        query = actual_session.query(Einzelspiel).filter(Einzelspiel.is_active == active)
    else:
        query = actual_session.query(Einzelspiel)
    einzelspiele = query.all() if not dataframe else pd.read_sql(query.statement, actual_session.bind)
    _close_session(actual_session, session)
    return einzelspiele


def get_einzelspiele_by_runde_id(runde_ids: List[int],
                                 active: bool = True,
                                 dataframe: bool = False,
                                 session: sessionmaker() = None) -> Union[None, List[Einzelspiel], pd.DataFrame]:
    actual_session = Sessions.get_session() if session is None else session
    if active:
        query = actual_session.query(Einzelspiel).filter(Einzelspiel.is_active == active) \
            .filter(Einzelspiel.runde_id.in_(runde_ids))
    else:
        query = actual_session.query(Einzelspiel).filter(Einzelspiel.runde_id.in_(runde_ids))
    einzelspiele = query.all() if not dataframe else pd.read_sql(query.statement, actual_session.bind)
    _close_session(actual_session, session)
    return einzelspiele


def get_einzelspiele_by_einzelspiel_ids(einzelspiel_ids: List[int],
                                        active: bool = True,
                                        dataframe: bool = False,
                                        session: sessionmaker() = None) -> Union[None, List[Einzelspiel], pd.DataFrame]:
    actual_session = Sessions.get_session() if session is None else session
    if active:
        query = actual_session.query(Einzelspiel).filter(Einzelspiel.is_active == active) \
            .filter(Einzelspiel.id.in_(einzelspiel_ids))
    else:
        query = actual_session.query(Einzelspiel).filter(Einzelspiel.id.in_(einzelspiel_ids))
    einzelspiele = query.all() if not dataframe else pd.read_sql(query.statement, actual_session.bind)
    _close_session(actual_session, session)
    return einzelspiele


def get_einzelspiele_by_teilnehmer_ids(teilnehmer_ids: List[int],
                                       active: bool = True,
                                       dataframe: bool = False,
                                       session: sessionmaker() = None) -> Union[List[Einzelspiel], pd.DataFrame]:
    if len(teilnehmer_ids) == 0:
        if dataframe:
            return pd.DataFrame()
        else:
            return []
    actual_session = Sessions.get_session() if session is None else session
    query = actual_session.query(Einzelspiel)
    positionen = [Einzelspiel.geberhand_id, Einzelspiel.ausspieler_id,
                  Einzelspiel.mittelhand_id, Einzelspiel.hinterhand_id]
    if active:
        query = query.filter(Einzelspiel.is_active == active)
    if len(teilnehmer_ids) <= 4:
        for t in teilnehmer_ids:
            query = query.filter(literal(t).in_(positionen))
    else:
        query = query.filter(Einzelspiel.geberhand_id.in_(teilnehmer_ids)) \
            .filter(Einzelspiel.ausspieler_id.in_(teilnehmer_ids)) \
            .filter(Einzelspiel.mittelhand_id.in_(teilnehmer_ids)) \
            .filter(Einzelspiel.hinterhand_id.in_(teilnehmer_ids))
    einzelspiele = query.all() if not dataframe else pd.read_sql(query.statement, actual_session.bind)
    _close_session(actual_session, session)
    return einzelspiele


def get_verdopplungen(dataframe: bool = False,
                      session: sessionmaker() = None) -> Union[List[Verdopplung], pd.DataFrame]:
    actual_session = Sessions.get_session() if session is None else session
    query = actual_session.query(Verdopplung)
    verdopplungen = query.all() if not dataframe else pd.read_sql(query.statement, actual_session.bind)
    _close_session(actual_session, session)
    return verdopplungen


def get_verdopplungen_by_einzelspiel_ids(einzelspiel_ids: List[int],
                                         dataframe: bool = False,
                                         session: sessionmaker() = None) -> Union[List[Verdopplung], pd.DataFrame]:
    actual_session = Sessions.get_session() if session is None else session
    query = actual_session.query(Verdopplung).filter(Verdopplung.einzelspiel_id.in_(einzelspiel_ids))
    verdopplungen = query.all() if not dataframe else pd.read_sql(query.statement, actual_session.bind)
    _close_session(actual_session, session)
    return verdopplungen


def get_einzelspiel_ids_by_runde_ids(runde_ids: List[int],
                                     active: bool = True,
                                     session: sessionmaker() = None) -> List[int]:
    actual_session = _build_session(session)
    if active:
        einzelspiel_ids = [e[0] for e in
                           actual_session.query(Einzelspiel.id).filter(Einzelspiel.runde_id.in_(runde_ids)).filter(
                               Einzelspiel.is_active == active).all()]
    else:
        einzelspiel_ids = [e[0] for e in
                           actual_session.query(Einzelspiel.id).filter(Einzelspiel.runde_id.in_(runde_ids)).all()]
    _close_session(actual_session, session)
    return einzelspiel_ids


def get_runde_id_by_einzelspiel_id(einzelspiel_id: int,
                                   session: sessionmaker() = None) -> Union[int, None]:
    actual_session = Sessions.get_session() if session is None else session
    runde_id = actual_session.query(Einzelspiel.runde_id).filter(Einzelspiel.id == einzelspiel_id).all()
    runde_id = runde_id[0][0] if len(runde_id) == 1 else None
    _close_session(actual_session, session)
    return runde_id


def get_latest_einzelspiel_id(session: sessionmaker() = None) -> Union[None, int]:
    actual_session = _build_session(session)
    einzelspiel_id = actual_session.query(Einzelspiel.id) \
        .filter(Einzelspiel.is_active == True) \
        .join(Einzelspiel.runde) \
        .filter(Runde.is_active == True) \
        .order_by(Einzelspiel.id.desc()).limit(1).all()
    einzelspiel_id = einzelspiel_id[0][0] if len(einzelspiel_id) == 1 else None
    _close_session(actual_session, session)
    return einzelspiel_id


def insert_einzelspiel(runde_id: int, ansager_id: Union[None, int], geber_id: int, ausspieler_id: int,
                       mittelhand_id: int, hinterhand_id: int, geberhand_id: int, spielpunkte: float,
                       spielart: str, farbe: Union[None, str] = None, laufende: Union[None, int] = None,
                       schneider: bool = False, schwarz: bool = False, partner_id: Union[None, int] = None,
                       durchmarsch: Union[None, bool] = False, tout: Union[None, bool] = False,
                       session: sessionmaker() = None) -> Einzelspiel:
    actual_session = _build_session(session)
    einzelspiel = Einzelspiel(runde_id=runde_id, ansager_id=ansager_id,
                              partner_id=partner_id, geber_id=geber_id, ausspieler_id=ausspieler_id,
                              mittelhand_id=mittelhand_id, hinterhand_id=hinterhand_id, geberhand_id=geberhand_id,
                              farbe=farbe, laufende=laufende, spielart=spielart, schneider=schneider, schwarz=schwarz,
                              durchmarsch=durchmarsch, tout=tout, spielpunkte=spielpunkte)
    actual_session.add(einzelspiel)
    actual_session.flush()
    if session is None:
        actual_session.commit()
        actual_session.close()
    return einzelspiel


def insert_teilnehmer(vorname: str, nachname: str, session: sessionmaker() = None) -> Teilnehmer:
    actual_session = _build_session(session)
    teilnehmer = Teilnehmer(name=f'{nachname}, {vorname}', vorname=vorname, nachname=nachname)
    actual_session.add(teilnehmer)
    actual_session.flush()
    if session is None:
        actual_session.commit()
        actual_session.close()
    return teilnehmer


def insert_runde(datum: datetime, name: str, ort: str, punkteconfig_id: int, session: sessionmaker() = None) -> Runde:
    actual_session = _build_session(session)
    runde = Runde(datum=datum, name=name, ort=ort, punkteconfig_id=punkteconfig_id)
    actual_session.add(runde)
    actual_session.flush()
    if session is None:
        actual_session.commit()
        actual_session.close()
    return runde


def insert_verdopplung(teilnehmer_id: int, einzelspiel_id: int, doppler: str,
                       session: sessionmaker() = None) -> Verdopplung:
    actual_session = _build_session(session)
    verdopplung = Verdopplung(teilnehmer_id=teilnehmer_id, einzelspiel_id=einzelspiel_id, doppler=doppler)
    actual_session.add(verdopplung)
    if session is None:
        actual_session.flush()
        actual_session.commit()
        actual_session.close()
    return verdopplung


def _close_session(actual_session: sessionmaker(), session: sessionmaker()):
    if session is None:
        actual_session.close()


def _build_session(session: sessionmaker()) -> sessionmaker():
    actual_session = Sessions.get_session() if session is None else session
    return actual_session
