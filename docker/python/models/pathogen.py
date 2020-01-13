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
        self.name: str = pathogen_name
        self.index = get_pathogen_id(pathogen_name)
        self.infectivity: int = 0
        self.mobility: int = 0
        self.duration: int = 0
        self.lethality: int = 0
        self.prevalence: int = 0

    def __hash__(self):
        return hash(self.index)

    def __eq__(self, other):
        if isinstance(other, Pathogen):
            return self.index == other.index
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def from_json(pathogen_json):
        pathogen = Pathogen(pathogen_json['name'])
        pathogen.infectivity = strength_to_int(pathogen_json['infectivity'])
        pathogen.mobility = strength_to_int(pathogen_json['mobility'])
        pathogen.duration = strength_to_int(pathogen_json['duration'])
        pathogen.lethality = strength_to_int(pathogen_json['lethality'])
        return pathogen
