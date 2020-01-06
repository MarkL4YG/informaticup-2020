from models.actions import end_round, develop_medication, deploy_medication
from models.gamestate import GameState


def outbreak_priority(outbreak_tuple):
    city = outbreak_tuple[0]
    outbreak_event = outbreak_tuple[1]

    return outbreak_event.get_prevalence() * city.get_population()


def process_round(state: GameState):
    pathogens_without_medication = set(state.get_pathogens()).difference(state.get_pathogens_with_medication())
    pathogens_without_medication = list(
        pathogens_without_medication.difference(state.get_pathogens_with_medication_in_development()))
    if pathogens_without_medication:
        # develop all medications first
        if state.get_available_points() >= 20:
            return develop_medication(pathogens_without_medication[0].get_id())
        else:
            return end_round()
    else:
        pathogens_with_medication = state.get_pathogens_with_medication()
        if pathogens_with_medication:
            if state.get_available_points() >= 10:
                # collect all not medicated outbreaks
                outbreaks_to_medicate = []
                for city in state.get_cities():
                    events = city.get_events()
                    medicated_pathogens = list(map(lambda event: event.get_pathogen(),
                                                   filter(lambda event: event.get_event_type() == "medicationDeployed",
                                                          events)))
                    outbreaks = list(filter(lambda event: event.get_event_type() == "outbreak", events))
                    outbreaks = list(
                        filter(lambda outbreak_event: outbreak_event.get_pathogen() in pathogens_with_medication,
                               outbreaks))
                    outbreaks = list(
                        filter(lambda outbreak_event: outbreak_event.get_pathogen() not in medicated_pathogens,
                               outbreaks))
                    outbreaks_to_medicate.extend(
                        list(map(lambda outbreak_event: (city, outbreak_event), outbreaks)))

                if outbreaks_to_medicate:
                    outbreaks_to_medicate.sort(key=outbreak_priority, reverse=True)
                    outbreak_to_vaccinate = outbreaks_to_medicate[0]
                    return deploy_medication(outbreak_to_vaccinate[1].get_pathogen().get_id(),
                                             outbreak_to_vaccinate[0].get_city_id())
                else:
                    return end_round()
            else:
                return end_round()
        else:
            return end_round()
