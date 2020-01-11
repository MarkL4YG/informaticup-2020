from models.format_utils import strength_to_int

allpathogens = [
    "Coccus innocuus",
    "Phagum vidiianum",
    "Rhinonitis",
    "Moricillus ☠",
    "Shanty",
    "Saccharomyces cerevisiae mutans",
    "N5-10",
    "Methanobrevibacter colferi",
    "Xenomonocythemia",
    "Admiral Trips",
    "Procrastinalgia",
    "Endoictus",
    "Φthisis",
    "Influenza iutiubensis",
    "Hexapox",
    "Neurodermantotitis",
    "Plorps",
    "Azmodeus",
    "Bonulus eruptus"
]


def get_pathogen_id(pathogen_name) -> int:
    try:
        pathogen_index = allpathogens.index(pathogen_name)
    except ValueError:
        pathogen_index = len(allpathogens)
        print(f'NEW PATHOGEN DISCOVERED! {pathogen_name} -> {pathogen_index}')
        allpathogens.append(pathogen_name)
    return pathogen_index


def get_pathogen_name(pathogen_id) -> str:
    return allpathogens[pathogen_id]


class Pathogen:

    def __init__(self, pathogen_name):
        super().__init__()
        self._name = pathogen_name
        self._index = get_pathogen_id(pathogen_name)
        self._infectivity = 0
        self._mobility = 0
        self._duration = 0
        self._lethality = 0
        self._prevalence = 0

    def __hash__(self):
        return hash(self._index)

    def __eq__(self, other):
        if isinstance(other, Pathogen):
            return self._index == other._index
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_name(self):
        return self._name

    def get_id(self):
        return self._index

    def get_infectivity(self):
        return self._infectivity

    def get_mobility(self):
        return self._mobility

    def get_duration(self):
        return self._duration

    def get_lethality(self):
        return self._lethality

    def get_prevalence(self):
        return self._prevalence

    def set_prevalence(self, prevalence):
        self._prevalence = prevalence

    @staticmethod
    def from_json(pathogen_json):
        # remove U+200E LEFT-TO-RIGHT MARK character
        pathogen = Pathogen(pathogen_json['name'])
        pathogen._infectivity = strength_to_int(pathogen_json['infectivity'])
        pathogen._mobility = strength_to_int(pathogen_json['mobility'])
        pathogen._duration = strength_to_int(pathogen_json['duration'])
        pathogen._lethality = strength_to_int(pathogen_json['lethality'])
        return pathogen
