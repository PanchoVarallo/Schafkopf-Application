from schafkopf.backend.calculator import RufspielCalculator
from schafkopf.database.data_model import Spielart, Verdopplung, Doppler
from schafkopf.database.queries import insert_einzelspiel, insert_resultat, insert_verdopplung
from schafkopf.database.session import Sessions


class RufspielWriter:
    def __init__(self, rufspiel_calculator: RufspielCalculator):
        self._rufspiel_calculator = rufspiel_calculator

    def write(self):
        rufspiel_calculator = self._rufspiel_calculator
        config = rufspiel_calculator.config
        session = Sessions.get_session()
        einzelspiel = insert_einzelspiel(runde_id=config.runde_id,
                                         ansager_id=config.ansager_id,
                                         partner_id=config.partner_id,
                                         geber_id=config.teilnehmer_ids[0],
                                         ausspieler_id=config.teilnehmer_ids[1],
                                         mittelhand_id=config.teilnehmer_ids[2],
                                         hinterhand_id=config.teilnehmer_ids[3],
                                         farbe=config.rufsau.name,
                                         laufende=config.laufende,
                                         spielart=Spielart.RUFSPIEL.name,
                                         schneider=rufspiel_calculator.is_schneider(),
                                         schwarz=rufspiel_calculator.is_schwarz(),
                                         spielpunkte=rufspiel_calculator.get_spielpunkte(),
                                         session=session)
        teilnehmer_id_to_punkte = rufspiel_calculator.get_teilnehmer_id_to_punkte()
        for spieler in config.get_spieler_ids():
            insert_resultat(teilnehmer_id=spieler,
                            einzelspiel_id=einzelspiel.id,
                            augen=config.spieler_augen,
                            punkte=teilnehmer_id_to_punkte.get(spieler),
                            gewonnen= True if spieler in rufspiel_calculator.get_gewinner_ids() else False,
                            session=session)
        for nicht_spieler in config.get_nicht_spieler_ids():
            insert_resultat(teilnehmer_id=nicht_spieler,
                            einzelspiel_id=einzelspiel.id,
                            augen=config.nicht_spieler_augen,
                            punkte=teilnehmer_id_to_punkte.get(nicht_spieler),
                            gewonnen=True if nicht_spieler in rufspiel_calculator.get_gewinner_ids() else False,
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

        session.commit()
        session.close()
