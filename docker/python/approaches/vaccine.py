from models.actions import end_round, develop_vaccine, deploy_vaccine
from models.gamestate import GameState


def outbreak_priority(outbreak_tuple):
    city = outbreak_tuple[0]
    outbreak_event = outbreak_tuple[1]

    return (1.0 - outbreak_event.get_prevalence()) * city.get_population()


def process_round(state: GameState):
    pathogens_without_vaccine = set(state.get_pathogens()).difference(state.get_pathogens_with_vaccination())
    pathogens_without_vaccine = list(
        pathogens_without_vaccine.difference(state.get_pathogens_with_vaccination_in_development()))
    if pathogens_without_vaccine:
        # develop all vaccines first
        if state.get_available_points() >= 40:
            return develop_vaccine(pathogens_without_vaccine[0].get_id())
        else:
            return end_round()
    else:
        pathogens_with_vaccine = state.get_pathogens_with_vaccination()
        if pathogens_with_vaccine:
            if state.get_available_points() >= 5:
                # collect all not vaccinated outbreaks
                outbreaks_to_vaccinate = []
                for city in state.get_cities():
                    events = city.get_events()
                    vaccinated_pathogens = list(map(lambda event: event.get_pathogen(),
                                                    filter(lambda event: event.get_event_type() == "vaccineDeployed",
                                                           events)))
                    outbreaks = list(filter(lambda event: event.get_event_type() == "outbreak", events))
                    outbreaks = list(
                        filter(lambda outbreak_event: outbreak_event.get_pathogen() in pathogens_with_vaccine,
                               outbreaks))
                    outbreaks = list(
                        filter(lambda outbreak_event: outbreak_event.get_pathogen() not in vaccinated_pathogens,
                               outbreaks))
                    outbreaks_to_vaccinate.extend(
                        list(map(lambda outbreak_event: (city, outbreak_event), outbreaks)))

                if outbreaks_to_vaccinate:
                    outbreaks_to_vaccinate.sort(key=outbreak_priority, reverse=True)
                    outbreak_to_vaccinate = outbreaks_to_vaccinate[0]
                    return deploy_vaccine(outbreak_to_vaccinate[1].get_pathogen().get_id(),
                                          outbreak_to_vaccinate[0].get_city_id())
                else:
                    return end_round()
            else:
                return end_round()
        else:
            return end_round()
