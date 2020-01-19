from typing import Tuple

from approaches.approach import Approach
from models.actions import end_round, develop_vaccine, deploy_vaccine
from models.city import City
from models.event import Event
from models.gamestate import GameState


# noinspection PyPep8Naming
class vaccine(Approach):

    def process_round(self, state: GameState):
        pathogens_without_vaccine = set(state.pathogens).difference(state.pathogens_with_vaccination)
        pathogens_without_vaccine = list(
            pathogens_without_vaccine.difference(state.pathogens_with_vaccination_in_development))
        if pathogens_without_vaccine:
            # develop all vaccines first
            if state.points >= 40:
                return develop_vaccine(pathogens_without_vaccine[0].index)
            else:
                return end_round()
        else:
            pathogens_with_vaccine = state.pathogens_with_vaccination
            if pathogens_with_vaccine:
                if state.points >= 5:
                    # collect all not vaccinated outbreaks
                    outbreaks_to_vaccinate = []
                    for city in state.cities:
                        events: list = city.events
                        vaccinated_pathogens = list(map(lambda event: event.pathogen,
                                                        filter(lambda event: event.event_type == "vaccineDeployed",
                                                               events)))
                        outbreaks = list(filter(lambda event: event.event_type == "outbreak", events))
                        outbreaks = list(
                            filter(lambda outbreak_event: outbreak_event.pathogen in pathogens_with_vaccine,
                                   outbreaks))
                        outbreaks = list(
                            filter(lambda outbreak_event: outbreak_event.pathogen not in vaccinated_pathogens,
                                   outbreaks))
                        outbreaks_to_vaccinate.extend(
                            list(map(lambda outbreak_event: (city, outbreak_event), outbreaks)))

                    if outbreaks_to_vaccinate:
                        outbreaks_to_vaccinate.sort(key=self.outbreak_priority, reverse=True)
                        outbreak_to_vaccinate = outbreaks_to_vaccinate[0]
                        return deploy_vaccine(outbreak_to_vaccinate[1].pathogen.index,
                                              outbreak_to_vaccinate[0].index)
                    else:
                        return end_round()
                else:
                    return end_round()
            else:
                return end_round()

    @classmethod
    def outbreak_priority(cls, outbreak_tuple: Tuple):
        city: City = outbreak_tuple[0]
        outbreak_event: Event = outbreak_tuple[1]

        return (1.0 - outbreak_event.prevalence) * city.population
