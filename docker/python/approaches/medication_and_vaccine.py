from models.actions import end_round, develop_vaccine, deploy_vaccine, deploy_medication, develop_medication
from models.gamestate import GameState


class PossibleAction:
    def __init__(self, priority, pathogen, city_id, vaccine):
        self._priority = priority
        self._pathogen = pathogen
        self._city_id = city_id
        self._vaccine = vaccine

    def get_priority(self):
        return self._priority

    def get_pathogen(self):
        return self._pathogen

    def get_city_id(self):
        return self._city_id

    def is_vaccine(self):
        return self._vaccine


def generate_possible_action(outbreak, city, vaccine, deployable) -> PossibleAction:
    pathogen = outbreak.get_pathogen()
    if vaccine:
        percentage = (1 - outbreak.get_prevalence())
        cost_factor = 5
    else:
        percentage = outbreak.get_prevalence() * 0.45
        cost_factor = 10
    if pathogen in deployable:
        deployable_factor = 1.3
    else:
        deployable_factor = 1
    priority = percentage * city.get_population() / cost_factor * deployable_factor
    return PossibleAction(priority, pathogen, city.get_city_id(), vaccine)


def is_action_executable(action, state):
    if action.is_vaccine():
        return action.get_pathogen() in state.get_pathogens_with_vaccination()
    else:
        return action.get_pathogen() in state.get_pathogens_with_medication()


def generate_deployment_action(possible_actions, state):
    executable_actions = list(filter(lambda action: is_action_executable(action, state), possible_actions))
    if executable_actions:
        action = executable_actions[0]
        if action.is_vaccine():
            return deploy_vaccine(action.get_pathogen().get_id(), action.get_city_id())
        else:
            return deploy_medication(action.get_pathogen().get_id(), action.get_city_id())
    else:
        return end_round()


def get_not_vaccinated_outbreaks_for_city(city):
    events = city.get_events()
    vaccinated_pathogens = list(map(lambda event: event.get_pathogen(),
                                    filter(lambda event: event.get_event_type() == "vaccineDeployed", events)))
    outbreaks = list(filter(lambda event: event.get_event_type() == "outbreak", events))
    return list(filter(lambda outbreak_event: outbreak_event.get_pathogen() not in vaccinated_pathogens, outbreaks))


def get_not_medicated_outbreaks_for_city(city):
    events = city.get_events()
    medicated_pathogens = list(map(lambda event: event.get_pathogen(),
                                   filter(lambda event: event.get_event_type() == "medicationDeployed", events)))
    outbreaks = list(filter(lambda event: event.get_event_type() == "outbreak", events))
    return list(filter(lambda outbreak_event: outbreak_event.get_pathogen() not in medicated_pathogens, outbreaks))


def process_round(state: GameState):
    possible_actions = []
    points = state.get_available_points()

    for city in state.get_cities():
        if points >= 5:
            not_vaccinated_outbreaks = get_not_vaccinated_outbreaks_for_city(city)
            actions = list(map(
                lambda outbreak: generate_possible_action(outbreak, city, True, state.get_pathogens_with_vaccination()),
                not_vaccinated_outbreaks))
            possible_actions.extend(actions)

        if points >= 10:
            not_medicated_outbreaks = get_not_medicated_outbreaks_for_city(city)
            actions = list(map(
                lambda outbreak: generate_possible_action(outbreak, city, False, state.get_pathogens_with_medication()),
                not_medicated_outbreaks))
            possible_actions.extend(actions)

    if possible_actions:
        possible_actions.sort(key=lambda action: action.get_priority(), reverse=True)

        action = possible_actions[0]
        pathogen = action.get_pathogen()
        if action.is_vaccine():
            if pathogen in state.get_pathogens_with_vaccination():
                return deploy_vaccine(pathogen.get_id(), action.get_city_id())
            elif pathogen not in state.get_pathogens_with_vaccination_in_development():
                if points >= 40:
                    return develop_vaccine(pathogen.get_id())
                else:
                    return end_round()
            else:
                return generate_deployment_action(possible_actions, state)
        else:
            if pathogen in state.get_pathogens_with_medication():
                return deploy_medication(pathogen.get_id(), action.get_city_id())
            elif pathogen not in state.get_pathogens_with_medication_in_development():
                if points >= 20:
                    return develop_medication(pathogen.get_id())
                else:
                    return end_round()
            else:
                return generate_deployment_action(possible_actions, state)
    else:
        return end_round()
