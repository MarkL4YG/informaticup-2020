
allpathogens = [

]


def get_pathogen_id(pathogen_name) -> int:
    return allpathogens.index(pathogen_name)


def get_pathogen_name(pathogen_id) -> str:
    return allpathogens[pathogen_id]

