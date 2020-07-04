class RufspielConfig2:

    def __init__(self,
                 runde_id: int,
                 punkteconfig: Punkteconfig,
                 teilnehmer_ids: List[int],
                 gelegt_ids: List[int],
                 ansager_id: int,
                 rufsau: Farbgebung,
                 kontriert_id: Union[None, int],
                 re_id: Union[None, int],
                 partner_id: int,
                 laufende: int,
                 spieler_augen: int,
                 nicht_spieler_augen: int):
        self._runde_id = runde_id
        self._punkteconfig = punkteconfig
        self._teilnehmer_ids = teilnehmer_ids
        self._gelegt_ids = gelegt_ids
        self._ansager_id = ansager_id
        self._rufsau = rufsau
        self._kontriert_id = kontriert_id
        self._re_id = re_id
        self._partner_id = partner_id
        self._laufende = laufende
        self._spieler_augen = spieler_augen
        self._nicht_spieler_augen = nicht_spieler_augen

    def get_spieler_ids(self) -> List[int]:
        return [t for t in self._teilnehmer_ids if t in [self.ansager_id, self.partner_id]]

    def get_nicht_spieler_ids(self) -> List[int]:
        return [t for t in self._teilnehmer_ids if t not in [self.ansager_id, self.partner_id]]

    @property
    def runde_id(self) -> int:
        return self._runde_id

    @property
    def punkteconfig(self) -> Punkteconfig:
        return self._punkteconfig

    @property
    def teilnehmer_ids(self) -> List[int]:
        return self._teilnehmer_ids

    @property
    def gelegt_ids(self) -> List[int]:
        return self._gelegt_ids

    @property
    def ansager_id(self) -> int:
        return self._ansager_id

    @property
    def rufsau(self) -> Farbgebung:
        return self._rufsau

    @property
    def kontriert_id(self) -> Union[None, int]:
        return self._kontriert_id

    @property
    def re_id(self) -> Union[None, int]:
        return self._re_id

    @property
    def partner_id(self) -> int:
        return self._partner_id

    @property
    def laufende(self) -> int:
        return self._laufende

    @property
    def spieler_augen(self) -> int:
        return self._spieler_augen

    @property
    def nicht_spieler_augen(self) -> int:
        return self._nicht_spieler_augen


class RufspielRawConfig2:

    def __init__(self,
                 runde_id: Union[None, int],
                 teilnehmer_ids: Union[None, List[int]],
                 gelegt_ids: Union[None, List[int]],
                 ansager_id: Union[None, int],
                 rufsau: Union[None, str],
                 kontriert_id: Union[None, List[int]],
                 re_id: Union[None, List[int]],
                 partner_id: Union[None, int],
                 laufende: Union[None, int],
                 spieler_nichtspieler_augen: Union[None, int],
                 augen: Union[None, int]):
        self._runde_id = runde_id
        self._teilnehmer_ids = teilnehmer_ids
        self._gelegt_ids = gelegt_ids
        self._ansager_id = ansager_id
        self._rufsau = rufsau
        self._kontriert_id = kontriert_id
        self._re_id = re_id
        self._partner_id = partner_id
        self._laufende = laufende
        self._spieler_nichtspieler_augen = spieler_nichtspieler_augen
        self._augen = augen

    @property
    def runde_id(self) -> Union[None, int]:
        return self._runde_id

    @property
    def teilnehmer_ids(self) -> Union[None, List[int]]:
        return self._teilnehmer_ids

    @property
    def gelegt_ids(self) -> Union[None, List[int]]:
        return self._gelegt_ids

    @property
    def ansager_id(self) -> Union[None, int]:
        return self._ansager_id

    @property
    def rufsau(self) -> Union[None, str]:
        return self._rufsau

    @property
    def kontriert_id(self) -> Union[None, List[int]]:
        return self._kontriert_id

    @property
    def re_id(self) -> Union[None, List[int]]:
        return self._re_id

    @property
    def partner_id(self) -> Union[None, int]:
        return self._partner_id

    @property
    def laufende(self) -> Union[None, int]:
        return self._laufende

    @property
    def spieler_nichtspieler_augen(self) -> Union[None, int]:
        return self._spieler_nichtspieler_augen

    @property
    def augen(self) -> Union[None, int]:
        return self._augen
