from models.actions import end_round, develop_vaccine, deploy_vaccine, deploy_medication, develop_medication, Action
from models.city import City
from models.event import Event
from models.gamestate import GameState
from models.pathogen import Pathogen


class PossibleAction:

    priority: int = 0
    pathogen: Pathogen = None
    city_id: int = 0
    is_vaccine: bool = False

    def __init__(self, priority: int, pathogen: Pathogen, city_id: int, vaccine: bool):
        self.priority = priority
        self.pathogen = pathogen
        self.city_id = city_id
        self.is_vaccine = vaccine


def generate_possible_action(outbreak: Event, city: City, vaccine: bool, deployable: list) -> PossibleAction:
    pathogen = outbreak.pathogen
    if vaccine:
        percentage = (1 - outbreak.prevalence)
        cost_factor = 5
    else:
        percentage = outbreak.prevalence * 0.45
        cost_factor = 10
    if pathogen in deployable:
        deployable_factor = 1.3
    else:
        deployable_factor = 1
    priority = percentage * city.population / cost_factor * deployable_factor
    return PossibleAction(priority, pathogen, city.index, vaccine)


def is_action_executable(action: PossibleAction, state: GameState):
    if action.is_vaccine:
        return action.pathogen in state.pathogens_with_vaccination
    else:
        return action.pathogen in state.pathogens_with_medication


def generate_deployment_action(possible_actions: list, state: GameState):
    executable_actions = list(filter(lambda action: is_action_executable(action, state), possible_actions))
    if executable_actions:
        action = executable_actions[0]
        if action.is_vaccine:
            return deploy_vaccine(action.pathogen.index, action.city_id)
        else:
            return deploy_medication(action.pathogen.index, action.city_id)
    else:
        return end_round()


def get_not_vaccinated_outbreaks_for_city(city: City):
    events = city.events
    vaccinated_pathogens = list(map(lambda event: event.pathogen,
                                    filter(lambda event: event.event_type == "vaccineDeployed", events)))
    outbreaks = list(filter(lambda event: event.event_type == "outbreak", events))
    return list(filter(lambda outbreak_event: outbreak_event.pathogen not in vaccinated_pathogens, outbreaks))


def get_not_medicated_outbreaks_for_city(city: City):
    events = city.events
    medicated_pathogens = list(map(lambda event: event.pathogen,
                                   filter(lambda event: event.event_type == "medicationDeployed", events)))
    outbreaks = list(filter(lambda event: event.event_type == "outbreak", events))
    return list(filter(lambda outbreak_event: outbreak_event.pathogen not in medicated_pathogens, outbreaks))


def process_round(state: GameState):
    possible_actions = []
    points = state.points

    for city in state.cities:
        if points >= 5:
            not_vaccinated_outbreaks = get_not_vaccinated_outbreaks_for_city(city)
            actions = list(map(
                lambda outbreak: generate_possible_action(outbreak, city, True, state.pathogens_with_vaccination),
                not_vaccinated_outbreaks))
            possible_actions.extend(actions)

        if points >= 10:
            not_medicated_outbreaks = get_not_medicated_outbreaks_for_city(city)
            actions = list(map(
                lambda outbreak: generate_possible_action(outbreak, city, False, state.pathogens_with_medication),
                not_medicated_outbreaks))
            possible_actions.extend(actions)

    if possible_actions:
        possible_actions.sort(key=lambda action: action.priority, reverse=True)

        action = possible_actions[0]
        pathogen = action.pathogen
        if action.is_vaccine:
            if pathogen in state.pathogens_with_vaccination:
                return deploy_vaccine(pathogen.index, action.city_id)
            elif pathogen not in state.pathogens_with_vaccination_in_development:
                if points >= 40:
                    return develop_vaccine(pathogen.index)
                else:
                    return end_round()
            else:
                return generate_deployment_action(possible_actions, state)
        else:
            if pathogen in state.pathogens_with_medication:
                return deploy_medication(pathogen.index, action.city_id)
            elif pathogen not in state.pathogens_with_medication_in_development:
                if points >= 20:
                    return develop_medication(pathogen.index)
                else:
                    return end_round()
            else:
                return generate_deployment_action(possible_actions, state)
    else:
        return end_round()
