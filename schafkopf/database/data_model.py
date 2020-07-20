import enum
from datetime import datetime

from sqlalchemy import Integer, String, \
    Column, DateTime, ForeignKey, Float, Boolean, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Doppler(enum.Enum):
    GELEGT = 1
    KONTRIERT = 2
    RE = 3
    JUNGFRAU = 4


class Farbgebung(enum.Enum):
    EICHEL = 1
    BLATT = 2
    HERZ = 3
    SCHELLEN = 4


class Spielart(enum.Enum):
    RUFSPIEL = 1
    FARBSOLO = 2
    WENZ = 3
    GEIER = 4
    RAMSCH = 5
    HOCHZEIT = 6


class Teilnehmer(Base):
    __tablename__ = 'teilnehmer'
    id = Column(Integer)
    name = Column(String(100), nullable=False)
    vorname = Column(String(100), nullable=False)
    nachname = Column(String(100), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    __table_args__ = (PrimaryKeyConstraint('id', name='teilnehmer_pk'),
                      UniqueConstraint('name'))


class Runde(Base):
    __tablename__ = 'runde'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    ort = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    punkteconfig_id = Column(Integer, ForeignKey('punkteconfig.id'), nullable=False)
    punkteconfig = relationship('Punkteconfig', backref='runde')
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)


class Punkteconfig(Base):
    __tablename__ = 'punkteconfig'
    id = Column(Integer, primary_key=True)
    name = Column(String, default="sauspiel_config_plus_hochzeit", nullable=False)
    ramsch = Column(Integer, default=20, nullable=False)
    rufspiel = Column(Integer, default=20, nullable=False)
    hochzeit = Column(Integer, default=30, nullable=False)
    laufende = Column(Float, default=10, nullable=False)
    schneider = Column(Float, default=10, nullable=False)
    schwarz = Column(Float, default=10, nullable=False)
    solo = Column(Integer, default=50, nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    __table_args__ = (PrimaryKeyConstraint('id', name='punkteconfig_id'),
                      UniqueConstraint('name'))


class Einzelspiel(Base):
    __tablename__ = 'einzelspiel'
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, nullable=False, default=True)
    runde_id = Column(Integer, ForeignKey('runde.id'), nullable=False)
    runde = relationship('Runde', backref='einzelspiele')
    ansager_id = Column(Integer, ForeignKey('teilnehmer.id'), nullable=True)
    ansager = relationship('Teilnehmer', foreign_keys=[ansager_id], backref='ansager')
    partner_id = Column(Integer, ForeignKey('teilnehmer.id'), nullable=True)
    partner = relationship('Teilnehmer', foreign_keys=[partner_id], backref='partner')
    geber_id = Column(Integer, ForeignKey('teilnehmer.id'), nullable=False)
    geber = relationship('Teilnehmer', foreign_keys=[geber_id], backref='geber')
    ausspieler_id = Column(Integer, ForeignKey('teilnehmer.id'), nullable=False)
    ausspieler = relationship('Teilnehmer', foreign_keys=[ausspieler_id], backref='ausspieler')
    mittelhand_id = Column(Integer, ForeignKey('teilnehmer.id'), nullable=False)
    mittelhand = relationship('Teilnehmer', foreign_keys=[mittelhand_id], backref='mittelhand')
    hinterhand_id = Column(Integer, ForeignKey('teilnehmer.id'), nullable=False)
    hinterhand = relationship('Teilnehmer', foreign_keys=[hinterhand_id], backref='hinterhand')
    geberhand_id = Column(Integer, ForeignKey('teilnehmer.id'), nullable=False)
    geberhand = relationship('Teilnehmer', foreign_keys=[geberhand_id], backref='geberhand')
    farbe = Column(String(20), nullable=True)
    laufende = Column(Integer, nullable=False, default=0)
    spielart = Column(String(20), default=Spielart.RUFSPIEL, nullable=False)
    schneider = Column(Boolean, nullable=False, default=False)
    schwarz = Column(Boolean, nullable=False, default=False)
    durchmarsch = Column(Boolean, nullable=False, default=False)
    tout = Column(Boolean, nullable=False, default=False)
    spielpunkte = Column(Float, nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)


class Resultat(Base):
    __tablename__ = 'resultat'
    id = Column(Integer)
    teilnehmer_id = Column(Integer, ForeignKey('teilnehmer.id'), nullable=False)
    teilnehmer = relationship('Teilnehmer', backref='resultate')
    einzelspiel_id = Column(Integer, ForeignKey('einzelspiel.id'), nullable=False)
    einzelspiel = relationship('Einzelspiel', backref='resultate')
    augen = Column(Float, nullable=False)
    punkte = Column(Float, nullable=False)
    gewonnen = Column(Boolean, nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    __table_args__ = (PrimaryKeyConstraint('id', name='resultat_pk'),
                      UniqueConstraint('teilnehmer_id', 'einzelspiel_id'))


class Verdopplung(Base):
    __tablename__ = 'verdopplung'
    id = Column(Integer)
    teilnehmer_id = Column(Integer, ForeignKey('teilnehmer.id'), nullable=False)
    teilnehmer = relationship('Teilnehmer', backref='verdopplungen')
    einzelspiel_id = Column(Integer, ForeignKey('einzelspiel.id'), nullable=False)
    einzelspiel = relationship('Einzelspiel', backref='verdopplungen')
    doppler = Column(String(20), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)
    __table_args__ = (PrimaryKeyConstraint('id', name='verdopplung_pk'),
                      UniqueConstraint('teilnehmer_id', 'einzelspiel_id', 'doppler'))
