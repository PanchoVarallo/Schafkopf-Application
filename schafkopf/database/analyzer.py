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
        runde_ids: List[int]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    resultate_df = pd.merge(left=get_resultate_by_runde_ids(runde_ids=runde_ids, dataframe=True),
                            right=get_einzelspiele_by_runde_id(runde_ids=runde_ids, dataframe=True),
                            how='left', left_on='einzelspiel_id', right_on='id')
    resultate_df['gewonnen'] = resultate_df['gewonnen'].astype(int)

    ansager_resultate_df = resultate_df.loc[resultate_df['teilnehmer_id'] == resultate_df['ansager_id']]
    partner_resultate_df = resultate_df.loc[resultate_df['teilnehmer_id'] == resultate_df['partner_id']]
    gegenspieler_resultate_df = resultate_df.loc[(resultate_df['teilnehmer_id'] != resultate_df['ansager_id'])
                                                 & ((resultate_df['teilnehmer_id'] != resultate_df['partner_id']) |
                                                    (resultate_df['teilnehmer_id'] is None))]

    einzelspiele = resultate_df.groupby('teilnehmer_id')['einzelspiel_id'].count().to_frame()
    einzelspiele.rename(columns={'einzelspiel_id': 'Einzelspiele'}, inplace=True)

    spieler = ansager_resultate_df.groupby('teilnehmer_id')['ansager_id'].count().to_frame()
    spieler.rename(columns={'ansager_id': 'Spieler'}, inplace=True)

    ansagen = ansager_resultate_df.groupby(['teilnehmer_id', 'spielart'])['ansager_id'].count().to_frame()
    ansagen = ansagen.unstack()
    ansagen.columns = ansagen.columns.droplevel()
    rename = {Spielart.WENZ.name: 'Wenz Ansage', Spielart.GEYER.name: 'Geyer Ansage',
              Spielart.FARBSOLO.name: 'Farbsolo Ansage', Spielart.RUFSPIEL.name: 'Rufspiel Ansage'}
    ansagen.rename(columns=rename, inplace=True)

    ansagen_gewonnen = ansager_resultate_df.groupby(['teilnehmer_id', 'spielart'])['gewonnen'].sum().to_frame()
    ansagen_gewonnen = ansagen_gewonnen.unstack()
    ansagen_gewonnen.columns = ansagen_gewonnen.columns.droplevel()
    rename = {Spielart.WENZ.name: 'Wenz Ansage gewonnen', Spielart.GEYER.name: 'Geyer Ansage gewonnen',
              Spielart.FARBSOLO.name: 'Farbsolo Ansage gewonnen', Spielart.RUFSPIEL.name: 'Rufspiel Ansage gewonnen'}
    ansagen_gewonnen.rename(columns=rename, inplace=True)

    partner = partner_resultate_df.groupby('teilnehmer_id')['partner_id'].count().to_frame()
    partner.rename(columns={'partner_id': 'Partner'}, inplace=True)

    partner_gewonnen = partner_resultate_df.groupby(['teilnehmer_id'])['gewonnen'].sum().to_frame()
    partner_gewonnen.rename(columns={'gewonnen': 'Partner gewonnen'}, inplace=True)

    gegenspieler = gegenspieler_resultate_df.groupby('teilnehmer_id').size().to_frame()
    gegenspieler.rename(columns={0: 'Gegenspieler'}, inplace=True)

    gegenspieler_gewonnen = gegenspieler_resultate_df.groupby(['teilnehmer_id'])['gewonnen'].sum().to_frame()
    gegenspieler_gewonnen.rename(columns={'gewonnen': 'Gegenspieler gewonnen'}, inplace=True)

    einzelspiel_ids = get_einzelspiel_ids_by_runde_id(runde_ids=runde_ids)
    verdopplungen = get_verdopplungen_by_einzelspiel_ids(einzelspiel_ids=einzelspiel_ids, dataframe=True)
    verdopplungen = verdopplungen.groupby(["teilnehmer_id", "doppler"])["doppler"].count().to_frame()
    verdopplungen = verdopplungen.unstack()
    verdopplungen.columns = verdopplungen.columns.droplevel()

    einzelspiele.reset_index(inplace=True)
    spieler.reset_index(inplace=True)
    partner.reset_index(inplace=True)
    gegenspieler.reset_index(inplace=True)
    partner_gewonnen.reset_index(inplace=True)
    gegenspieler_gewonnen.reset_index(inplace=True)
    ansagen.reset_index(inplace=True)
    ansagen_gewonnen.reset_index(inplace=True)
    verdopplungen.reset_index(inplace=True)

    res = einzelspiele.merge(right=spieler, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=ansagen, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=partner, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=gegenspieler, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=ansagen_gewonnen, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=partner_gewonnen, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=gegenspieler_gewonnen, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=verdopplungen, how='left', left_on='teilnehmer_id', right_on='teilnehmer_id')
    res = res.merge(right=get_teilnehmer(dataframe=True), how='left', left_on='teilnehmer_id', right_on='id')

    # Add columns if they are missing
    columns_to_add = ['Spieler', 'Rufspiel Ansage', 'Spieler', 'Rufspiel Ansage gewonnen', 'Einzelspiele', 'Partner',
                      'Partner gewonnen', 'Gegenspieler', 'Gegenspieler gewonnen', 'GELEGT', 'KONTRIERT', 'RE',
                      'Farbsolo Ansage', 'Farbsolo Ansage gewonnen', 'Wenz Ansage', 'Wenz Ansage gewonnen',
                      'Geyer Ansage', 'Geyer Ansage gewonnen']
    for col in columns_to_add:
        if col not in res.columns:
            res[col] = np.NaN

    res['% Spieler (von Einzelspiele)'] = (res['Spieler'] / res['Einzelspiele']) * 100.0
    res['% Rufspiel (von Spieler)'] = (res['Rufspiel Ansage'] / res['Spieler']) * 100.0
    res['% Rufspiel gewonnen (von Rufspiel)'] = (res['Rufspiel Ansage gewonnen'] / res['Rufspiel Ansage']) * 100.0
    res['% Solo (von Spieler)'] = ((res['Wenz Ansage'])
                                   / res['Spieler']) * 100.0
    res['% Solo gewonnen (von Solo)'] = ((res['Wenz Ansage gewonnen'])
                                         / (res['Wenz Ansage'])) * 100.0
    res['% Partner (von Einzelspiele)'] = (res['Partner'] / res['Einzelspiele']) * 100.0
    res['% Partner gewonnen (von Partner)'] = (res['Partner gewonnen'] / res['Partner']) * 100.0
    res['% Gegenspieler (von Einzelspiele)'] = (res['Gegenspieler'] / res['Einzelspiele']) * 100.0
    res['% Gegenspieler gewonnen (von Gegenspieler)'] = (res['Gegenspieler gewonnen'] / res['Gegenspieler']) * 100.0
    res['% Gelegt (von Einzelspiele)'] = (res['GELEGT'] / res['Einzelspiele']) * 100.0
    res['% Kontriert (von Einzelspiele)'] = (res['KONTRIERT'] / res['Einzelspiele']) * 100.0
    res['% Re (von Einzelspiele)'] = (res['RE'] / res['Einzelspiele']) * 100.0

    temp = ['% Spieler (von Einzelspiele)', '% Partner (von Einzelspiele)', '% Gegenspieler (von Einzelspiele)',
            '% Gelegt (von Einzelspiele)', '% Kontriert (von Einzelspiele)', '% Re (von Einzelspiele)']
    res[temp] = res[temp].fillna(value=0.0)
    res = res[['name',
               '% Spieler (von Einzelspiele)',
               '% Rufspiel (von Spieler)',
               '% Rufspiel gewonnen (von Rufspiel)',
               '% Solo (von Spieler)',
               '% Solo gewonnen (von Solo)',
               '% Partner (von Einzelspiele)',
               '% Partner gewonnen (von Partner)',
               '% Gegenspieler (von Einzelspiele)',
               '% Gegenspieler gewonnen (von Gegenspieler)',
               '% Gelegt (von Einzelspiele)',
               '% Kontriert (von Einzelspiele)',
               '% Re (von Einzelspiele)'
               ]]
    res.rename(columns={'name': 'Teilnehmer'}, inplace=True)

    spieler = res[['Teilnehmer',
                   '% Spieler (von Einzelspiele)',
                   '% Rufspiel (von Spieler)',
                   '% Rufspiel gewonnen (von Rufspiel)',
                   '% Solo (von Spieler)',
                   '% Solo gewonnen (von Solo)',
                   ]].copy()
    partner = res[['Teilnehmer',
                   '% Partner (von Einzelspiele)',
                   '% Partner gewonnen (von Partner)',
                   ]].copy()
    gegenspieler = res[['Teilnehmer',
                        '% Gegenspieler (von Einzelspiele)',
                        '% Gegenspieler gewonnen (von Gegenspieler)'
                        ]].copy()
    verdopplungen = res[['Teilnehmer',
                         '% Gelegt (von Einzelspiele)',
                         '% Kontriert (von Einzelspiele)',
                         '% Re (von Einzelspiele)',
                         ]].copy()
    spieler.sort_values('% Spieler (von Einzelspiele)', inplace=True, ascending=False)
    partner.sort_values('% Partner (von Einzelspiele)', inplace=True, ascending=False)
    gegenspieler.sort_values('% Gegenspieler (von Einzelspiele)', inplace=True, ascending=False)
    verdopplungen.sort_values('% Gelegt (von Einzelspiele)', inplace=True, ascending=False)
    return spieler.round(2), partner.round(2), gegenspieler.round(2), verdopplungen.round(2)
