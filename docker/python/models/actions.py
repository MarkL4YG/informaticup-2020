from models.city import get_city_name
from models.pathogen import get_pathogen_name


class Actions:

    @staticmethod
    def end_round() -> dict:
        return {"type": "endRound"}

    @staticmethod
    def quarantine_city(city_id, number_of_rounds=1) -> dict:
        city_name = get_city_name(city_id)
        return {
            "type": "putUnderQuarantine",
            "city": city_name,
            "rounds": number_of_rounds
        }

    @staticmethod
    def close_airport(city_id, number_of_rounds=1) -> dict:
        city_name = get_city_name(city_id)
        return {
            "type": "closeAirport",
            "rounds": number_of_rounds,
            "city": city_name
        }

    @staticmethod
    def close_airway(from_city_id, to_city_id, number_of_rounds=1) -> dict:
        from_city_name = get_city_name(from_city_id)
        to_city_name = get_city_name(to_city_id)
        return {
            "type": "closeConnection",
            "fromCity": from_city_name,
            "toCity": to_city_name,
            "rounds": number_of_rounds
        }

    @staticmethod
    def develop_vaccine(pathogen_id) -> dict:
        pathogen_name = get_pathogen_name(pathogen_id)
        return {
            "type": "developVaccine",
            "pathogen": pathogen_name
        }

    @staticmethod
    def deploy_vaccine(pathogen_id, city_id) -> dict:
        pathogen_name = get_pathogen_name(pathogen_id)
        city_name = get_city_name(city_id)
        return {
            "type": "deployVaccine",
            "pathogen": pathogen_name,
            "city": city_name
        }

    @staticmethod
    def develop_medication(pathogen_id) -> dict:
        pathogen_name = get_pathogen_name(pathogen_id)
        return {
            "type": "developMedication",
            "pathogen": pathogen_name
        }

    @staticmethod
    def deploy_medication(pathogen_id, city_id) -> dict:
        pathogen_name = get_pathogen_name(pathogen_id)
        city_name = get_city_name(city_id)
        return {
            "type": "deployMedication",
            "pathogen": pathogen_name,
            "city": city_name
        }

    @staticmethod
    def use_political_influence(city_id) -> dict:
        city_name = get_city_name(city_id)
        return {
            "type": "exertInfluence",
            "city": city_name
        }

    @staticmethod
    def call_for_elections(city_id) -> dict:
        city_name = get_city_name(city_id)
        return {
            "type": "callElections",
            "city": city_name
        }

    @staticmethod
    def spread_information(city_id) -> dict:
        city_name = get_city_name(city_id)
        return {
            "type": "launchCampaign",
            "city": city_name
        }
