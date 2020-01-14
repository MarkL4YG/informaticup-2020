from models.actions import end_round, develop_medication, deploy_medication
from models.city import City
from models.event import Event
from models.gamestate import GameState


def outbreak_priority(outbreak_tuple):
    city: City = outbreak_tuple[0]
    outbreak_event: Event = outbreak_tuple[1]

    return outbreak_event.prevalence * city.population


def process_round(state: GameState):
    pathogens_without_medication = set(state.pathogens).difference(state.pathogens_with_medication)
    pathogens_without_medication = list(
        pathogens_without_medication.difference(state.pathogens_with_medication_in_development))
    if pathogens_without_medication:
        # develop all medications first
        if state.points >= 20:
            return develop_medication(pathogens_without_medication[0].index)
        else:
            return end_round()
    else:
        pathogens_with_medication = state.pathogens_with_medication
        if pathogens_with_medication:
            if state.points >= 10:
                # collect all not medicated outbreaks
                outbreaks_to_medicate = []
                for city in state.cities:
                    events = city.events
                    medicated_pathogens = list(map(lambda event: event.pathogen,
                                                   filter(lambda event: event.event_type == "medicationDeployed",
                                                          events)))
                    outbreaks = list(filter(lambda event: event.event_type == "outbreak", events))
                    outbreaks = list(
                        filter(lambda outbreak_event: outbreak_event.pathogen in pathogens_with_medication,
                               outbreaks))
                    outbreaks = list(
                        filter(lambda outbreak_event: outbreak_event.pathogen not in medicated_pathogens,
                               outbreaks))
                    outbreaks_to_medicate.extend(
                        list(map(lambda outbreak_event: (city, outbreak_event), outbreaks)))

                if outbreaks_to_medicate:
                    outbreaks_to_medicate.sort(key=outbreak_priority, reverse=True)
                    outbreak_to_vaccinate = outbreaks_to_medicate[0]
                    return deploy_medication(outbreak_to_vaccinate[1].pathogen.index,
                                             outbreak_to_vaccinate[0].city_id)
                else:
                    return end_round()
            else:
                return end_round()
        else:
            return end_round()
