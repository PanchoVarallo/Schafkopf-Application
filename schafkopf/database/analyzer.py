from typing import List, Tuple

import numpy as np
import pandas as pd

from schafkopf.database.data_model import Spielart
from schafkopf.database.queries import get_resultate_by_runde_ids, get_teilnehmer, get_einzelspiele_by_runde_id, \
    get_teilnehmer_name_by_id, get_einzelspiel_ids_by_runde_id, get_verdopplungen_by_einzelspiel_ids


def get_list_dataframe_by_runde_ids(runde_ids: List[int]) -> pd.DataFrame:
    resultate = get_resultate_by_runde_ids(runde_ids=runde_ids, dataframe=True)
    resultate = resultate[['einzelspiel_id', 'teilnehmer_id', 'punkte']]
    resultate.set_index(['einzelspiel_id', 'teilnehmer_id'], inplace=True)
    resultate = resultate.unstack()
    resultate.sort_index(ascending=True, inplace=True)
    resultate.fillna(0.0, inplace=True)
    resultate = resultate.cumsum()
    columns = {col: get_teilnehmer_name_by_id(col) for col in resultate.columns.get_level_values(1)}
    resultate.rename(columns={'punkte': 'Punkte'}, level=0, inplace=True)
    resultate.rename(columns=columns, level=1, inplace=True)
    resultate['Einzelspiele'] = np.arange(len(resultate)) + 1
    resultate.set_index(['Einzelspiele'], inplace=True)
    resultate = resultate.stack()
    resultate.reset_index(inplace=True)
    resultate.rename(columns={'teilnehmer_id': 'Teilnehmer'}, inplace=True)
    unique_teilnehmer = resultate['Teilnehmer'].unique()
    append = pd.DataFrame({'Einzelspiele': [0] * len(unique_teilnehmer), 'Punkte': [0.0] * len(unique_teilnehmer),
                           'Teilnehmer': unique_teilnehmer})
    resultate = resultate.append(append, ignore_index=True)
    resultate.sort_values("Einzelspiele", inplace=True)
    return resultate


def get_ranking_dataframe_by_runde_ids(runde_ids: List[int]) -> pd.DataFrame:
    resultate = get_resultate_by_runde_ids(runde_ids=runde_ids, dataframe=True)
    grouped_einzelspiele = resultate.groupby('teilnehmer_id')["einzelspiel_id"].count().to_frame()
    grouped_resultate = resultate.groupby(["teilnehmer_id"])["punkte"].sum().to_frame()
    grouped = pd.concat([grouped_einzelspiele, grouped_resultate], axis=1, join='inner')
    teilnehmer = get_teilnehmer(dataframe=True)
    teilnehmer.set_index(["id"], inplace=True)
    result_df = pd.concat([teilnehmer, grouped], axis=1, join='inner')
    result_df.sort_values(["punkte"], ascending=False, inplace=True)
    result_df = result_df[["name", "einzelspiel_id", "punkte"]]
    result_df.rename(inplace=True, columns={"name": "Name", "punkte": "Punktestand", "einzelspiel_id": "Einzelspiele"})
    return result_df


def get_stats_dataframe_by_runde_ids(
        runde_ids: List[int]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    resultate_df = pd.merge(left=get_resultate_by_runde_ids(runde_ids=runde_ids, dataframe=True),
                            right=get_einzelspiele_by_runde_id(runde_ids=runde_ids, dataframe=True),
                            how='left', left_on='einzelspiel_id', right_on='id')
    resultate_df['gewonnen'] = resultate_df['gewonnen'].astype(int)
    resultate_df['verloren'] = 1 - resultate_df['gewonnen']

    ansager_resultate_df = resultate_df.loc[resultate_df['teilnehmer_id'] == resultate_df['ansager_id']]
    partner_resultate_df = resultate_df.loc[resultate_df['teilnehmer_id'] == resultate_df['partner_id']]
    gegenspieler_resultate_df = resultate_df.loc[(resultate_df['teilnehmer_id'] != resultate_df['ansager_id'])
                                                 & ((resultate_df['teilnehmer_id'] != resultate_df['partner_id']) |
                                                    (resultate_df['teilnehmer_id'] is None))
                                                 & (resultate_df['spielart'] != Spielart.RAMSCH.name)]
    ramsch_resultate_df = resultate_df.loc[resultate_df['spielart'] == Spielart.RAMSCH.name]

    einzelspiele = resultate_df.groupby('teilnehmer_id')['einzelspiel_id'].count().to_frame()
    einzelspiele.rename(columns={'einzelspiel_id': 'Einzelspiele'}, inplace=True)

    ansager = ansager_resultate_df.groupby('teilnehmer_id')['ansager_id'].count().to_frame()
    ansager.rename(columns={'ansager_id': 'Ansager'}, inplace=True)

    partner = partner_resultate_df.groupby('teilnehmer_id')['partner_id'].count().to_frame()
    partner.rename(columns={'partner_id': 'Partner'}, inplace=True)

    ansagespieler = ansager_resultate_df.groupby(['teilnehmer_id', 'spielart'])['ansager_id'].count().to_frame()
    ansagespieler = ansagespieler.unstack()
    ansagespieler.columns = ansagespieler.columns.droplevel()
    rename = {Spielart.WENZ.name: 'Wenz Ansage', Spielart.GEYER.name: 'Geyer Ansage',
              Spielart.FARBSOLO.name: 'Farbsolo Ansage', Spielart.RUFSPIEL.name: 'Rufspiel Ansage',
              Spielart.HOCHZEIT.name: 'Hochzeit Ansage'}
    ansagespieler.rename(columns=rename, inplace=True)

    ansagespieler_gewonnen = ansager_resultate_df.groupby(['teilnehmer_id', 'spielart'])['gewonnen'].sum().to_frame()
    ansagespieler_gewonnen = ansagespieler_gewonnen.unstack()
    ansagespieler_gewonnen.columns = ansagespieler_gewonnen.columns.droplevel()
    rename = {Spielart.WENZ.name: 'Wenz Ansage gew.', Spielart.GEYER.name: 'Geyer Ansage gew.',
              Spielart.FARBSOLO.name: 'Farbsolo Ansage gew.', Spielart.HOCHZEIT.name: 'Hochzeit Ansage gew.',
              Spielart.RUFSPIEL.name: 'Rufspiel Ansage gew.'}
    ansagespieler_gewonnen.rename(columns=rename, inplace=True)

    partnerspieler = partner_resultate_df.groupby(['teilnehmer_id', 'spielart'])['partner_id'].count().to_frame()
    partnerspieler = partnerspieler.unstack()
    partnerspieler.columns = partnerspieler.columns.droplevel()
    rename = {Spielart.RUFSPIEL.name: 'Rufspiel Partner', Spielart.HOCHZEIT.name: 'Hochzeit Partner'}
    partnerspieler.rename(columns=rename, inplace=True)

    partnerspieler_gewonnen = partner_resultate_df.groupby(['teilnehmer_id', 'spielart'])['gewonnen'].sum().to_frame()
    partnerspieler_gewonnen = partnerspieler_gewonnen.unstack()
    partnerspieler_gewonnen.columns = partnerspieler_gewonnen.columns.droplevel()
    rename = {Spielart.HOCHZEIT.name: 'Hochzeit Partner gew.', Spielart.RUFSPIEL.name: 'Rufspiel Partner gew.'}
    partnerspieler_gewonnen.rename(columns=rename, inplace=True)

    gegenspieler = gegenspieler_resultate_df.groupby('teilnehmer_id').size().to_frame()
    gegenspieler.rename(columns={0: 'Gegenspieler'}, inplace=True)

    gegenspieler_gewonnen = gegenspieler_resultate_df.groupby(['teilnehmer_id'])['gewonnen'].sum().to_frame()
    gegenspieler_gewonnen.rename(columns={'gewonnen': 'Gegenspieler gew.'}, inplace=True)

    ramschspieler = ramsch_resultate_df.groupby('teilnehmer_id').size().to_frame()
    ramschspieler.rename(columns={0: 'Ramsch'}, inplace=True)

    ramschspieler_gewonnen = ramsch_resultate_df.groupby(['teilnehmer_id'])['gewonnen'].sum().to_frame()
    ramschspieler_gewonnen.rename(columns={'gewonnen': 'Ramsch gew.'}, inplace=True)
    ramschspieler_verloren = ramsch_resultate_df.groupby(['teilnehmer_id'])['verloren'].sum().to_frame()
    ramschspieler_verloren.rename(columns={'verloren': 'Ramsch verl.'}, inplace=True)

    einzelspiel_ids = get_einzelspiel_ids_by_runde_id(runde_ids=runde_ids)
    verdopplungen = get_verdopplungen_by_einzelspiel_ids(einzelspiel_ids=einzelspiel_ids, dataframe=True)
    verdopplungen = verdopplungen.groupby(["teilnehmer_id", "doppler"])["doppler"].count().to_frame()
    verdopplungen = verdopplungen.unstack()
    verdopplungen.columns = verdopplungen.columns.droplevel()

    einzelspiele.reset_index(inplace=True)
    ansager.reset_index(inplace=True)
    partner.reset_index(inplace=True)
    ansagespieler.reset_index(inplace=True)
    ansagespieler_gewonnen.reset_index(inplace=True)
    partnerspieler.reset_index(inplace=True)
    partnerspieler_gewonnen.reset_index(inplace=True)
    gegenspieler.reset_index(inplace=True)
    gegenspieler_gewonnen.reset_index(inplace=True)
    ramschspieler.reset_index(inplace=True)
    ramschspieler_gewonnen.reset_index(inplace=True)
    ramschspieler_verloren.reset_index(inplace=True)
    verdopplungen.reset_index(inplace=True)

    res = einzelspiele.merge(right=ansager, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=partner, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=ansagespieler, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=partnerspieler, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=gegenspieler, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=ramschspieler, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=ansagespieler_gewonnen, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=partnerspieler_gewonnen, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=gegenspieler_gewonnen, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=ramschspieler_gewonnen, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=ramschspieler_verloren, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=verdopplungen, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=get_teilnehmer(dataframe=True), how='left', left_on='teilnehmer_id', right_on='id')

    # Add columns if they are missing
    columns_to_add = ['Ansager', 'Partner', 'Rufspiel Ansage', 'Rufspiel Ansage gew.', 'Hochzeit Ansage',
                      'Hochzeit Ansage gew.', 'Rufspiel Partner', 'Rufspiel Partner gew.', 'Hochzeit Partner',
                      'Hochzeit Partner gew.', 'Einzelspiele', 'Gegenspieler', 'Gegenspieler gew.', 'Ramsch',
                      'Ramsch gew.', 'Ramsch verl.', 'JUNGFRAU', 'GELEGT', 'KONTRIERT', 'RE', 'Farbsolo Ansage',
                      'Farbsolo Ansage gew.', 'Wenz Ansage', 'Wenz Ansage gew.', 'Geyer Ansage', 'Geyer Ansage gew.']
    for col in columns_to_add:
        if col not in res.columns:
            res[col] = np.NaN
    res.fillna(0.0, inplace=True)
    res['% Ansager (von Einzelspiele)'] = (res['Ansager'] / res['Einzelspiele']) * 100.0
    res['% Rufspiel (von Ansager)'] = (res['Rufspiel Ansage'] / res['Ansager']) * 100.0
    res['% Rufspiel gew. (von Rufspiel)'] = (res['Rufspiel Ansage gew.'] / res['Rufspiel Ansage']) * 100.0
    res['% Hochzeit (von Ansager)'] = (res['Hochzeit Ansage'] / res['Ansager']) * 100.0
    res['% Hochzeit gew. (von Hochzeit)'] = (res['Hochzeit Ansage gew.'] / res['Hochzeit Ansage']) * 100.0
    res['Solo Ansage'] = res['Wenz Ansage'] + res['Geyer Ansage'] + res['Farbsolo Ansage']
    res['Solo Ansage gew.'] = res['Wenz Ansage gew.'] + res['Geyer Ansage gew.'] + res[
        'Farbsolo Ansage gew.']
    res['% Solo (von Ansager)'] = (res['Solo Ansage'] / res['Ansager']) * 100.0
    res['% Solo gew. (von Solo)'] = (res['Solo Ansage gew.'] / res['Solo Ansage']) * 100.0
    res['% Partner (von Einzelspiele)'] = (res['Partner'] / res['Einzelspiele']) * 100.0
    res['% Rufspiel Partner (von Partner)'] = (res['Rufspiel Partner'] / res['Partner']) * 100.0
    res['% Rufspiel Partner gew. (von Rufspiel Partner)'] = (res['Rufspiel Partner gew.'] / res[
        'Rufspiel Partner']) * 100.0
    res['% Hochzeit Partner (von Partner)'] = (res['Hochzeit Partner'] / res['Partner']) * 100.0
    res['% Hochzeit Partner gew. (von Hochzeit Partner)'] = (res['Hochzeit Partner gew.'] / res[
        'Hochzeit Partner']) * 100.0
    res['% Gegenspieler (von Einzelspiele)'] = (res['Gegenspieler'] / res['Einzelspiele']) * 100.0
    res['% Gegenspieler gew. (von Gegenspieler)'] = (res['Gegenspieler gew.'] / res['Gegenspieler']) * 100.0
    res['% Ramsch (von Einzelspiele)'] = (res['Ramsch'] / res['Einzelspiele']) * 100.0
    res['% Ramsch gew. (von Ramsch)'] = (res['Ramsch gew.'] / res['Ramsch']) * 100.0
    res['% Ramsch verl. (von Ramsch)'] = (res['Ramsch verl.'] / res['Ramsch']) * 100.0
    res['% Jungfrau (von Ramsch gew.)'] = (res['JUNGFRAU'] / res['Ramsch gew.']) * 100.0
    res['% Gelegt (von Einzelspiele)'] = (res['GELEGT'] / res['Einzelspiele']) * 100.0
    res['% Kontriert (von Einzelspiele)'] = (res['KONTRIERT'] / res['Einzelspiele']) * 100.0
    res['% Re (von Einzelspiele)'] = (res['RE'] / res['Einzelspiele']) * 100.0

    temp = ['% Ansager (von Einzelspiele)', '% Partner (von Einzelspiele)', '% Gegenspieler (von Einzelspiele)',
            '% Gelegt (von Einzelspiele)', '% Kontriert (von Einzelspiele)', '% Re (von Einzelspiele)']
    res[temp] = res[temp].fillna(value=0.0)
    res = res[['name',
               '% Ansager (von Einzelspiele)',
               '% Partner (von Einzelspiele)',
               '% Rufspiel (von Ansager)',
               '% Rufspiel gew. (von Rufspiel)',
               '% Hochzeit (von Ansager)',
               '% Hochzeit gew. (von Hochzeit)',
               '% Solo (von Ansager)',
               '% Solo gew. (von Solo)',
               '% Rufspiel Partner (von Partner)',
               '% Rufspiel Partner gew. (von Rufspiel Partner)',
               '% Hochzeit Partner (von Partner)',
               '% Hochzeit Partner gew. (von Hochzeit Partner)',
               '% Gegenspieler (von Einzelspiele)',
               '% Gegenspieler gew. (von Gegenspieler)',
               '% Ramsch (von Einzelspiele)',
               '% Ramsch gew. (von Ramsch)',
               '% Ramsch verl. (von Ramsch)',
               '% Jungfrau (von Ramsch gew.)',
               '% Gelegt (von Einzelspiele)',
               '% Kontriert (von Einzelspiele)',
               '% Re (von Einzelspiele)'
               ]]
    res.rename(columns={'name': 'Teilnehmer'}, inplace=True)

    ansager = res[['Teilnehmer',
                   '% Ansager (von Einzelspiele)',
                   '% Rufspiel (von Ansager)',
                   '% Rufspiel gew. (von Rufspiel)',
                   '% Hochzeit (von Ansager)',
                   '% Hochzeit gew. (von Hochzeit)',
                   '% Solo (von Ansager)',
                   '% Solo gew. (von Solo)',
                   ]].copy()
    partner = res[['Teilnehmer',
                   '% Partner (von Einzelspiele)',
                   '% Rufspiel Partner (von Partner)',
                   '% Rufspiel Partner gew. (von Rufspiel Partner)',
                   '% Hochzeit Partner (von Partner)',
                   '% Hochzeit Partner gew. (von Hochzeit Partner)',
                   ]].copy()
    gegenspieler = res[['Teilnehmer',
                        '% Gegenspieler (von Einzelspiele)',
                        '% Gegenspieler gew. (von Gegenspieler)'
                        ]].copy()
    ramschspieler = res[['Teilnehmer',
                         '% Ramsch (von Einzelspiele)',
                         '% Ramsch verl. (von Ramsch)',
                         '% Ramsch gew. (von Ramsch)',
                         '% Jungfrau (von Ramsch gew.)'
                         ]].copy()
    verdopplungen = res[['Teilnehmer',
                         '% Gelegt (von Einzelspiele)',
                         '% Kontriert (von Einzelspiele)',
                         '% Re (von Einzelspiele)',
                         ]].copy()
    ansager.sort_values('% Ansager (von Einzelspiele)', inplace=True, ascending=False)
    partner.sort_values('% Partner (von Einzelspiele)', inplace=True, ascending=False)
    gegenspieler.sort_values('% Gegenspieler (von Einzelspiele)', inplace=True, ascending=False)
    ramschspieler.sort_values(['% Ramsch (von Einzelspiele)', '% Ramsch verl. (von Ramsch)'],
                              inplace=True, ascending=False)
    verdopplungen.sort_values('% Gelegt (von Einzelspiele)', inplace=True, ascending=False)
    return ansager.round(2), partner.round(2), gegenspieler.round(2), ramschspieler.round(2), verdopplungen.round(2)
