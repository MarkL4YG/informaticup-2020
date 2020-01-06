from models.event import Event
from models.format_utils import strength_to_int


all_cities = [
    "Abuja",
    "Accra",
    "Albuquerque",
    "Amsterdam",
    "Anchorage",
    "Andorra la Vella",
    "Ankara",
    "Antananarivo",
    "Asunción",
    "Atlanta",
    "Austin",
    "Aşgabat",
    "Bakı",
    "Bamako",
    "Bangî",
    "Banjul",
    "Barcelona",
    "Belfast",
    "Belmopan",
    "Bergen",
    "Berlin",
    "Bern",
    "Bissau",
    "Bloemfontein",
    "Bogotá",
    "Boston",
    "Brasília",
    "Bratislava",
    "Brazzaville",
    "Brisbane",
    "Bruxelles",
    "București",
    "Budapest",
    "Buenos Aires",
    "Bujumbura",
    "Cape Town",
    "Caracas",
    "Cayenne",
    "Charlotte",
    "Chicago",
    "Chișinău",
    "Christchurch",
    "Cincinnati",
    "Città del Vaticano",
    "Città di San Marino",
    "Ciudad de Córdoba",
    "Ciudad de Guatemala",
    "Ciudad de México",
    "Ciudad de Panamá",
    "Cleveland",
    "Cockburn Town",
    "Conakry",
    "Dakar",
    "Dallas",
    "Denver",
    "Detroit",
    "Dodoma",
    "Dublin",
    "Edinburgh",
    "Edmonton",
    "El Paso",
    "Freetown",
    "Gaborone",
    "Gdańsk",
    "Georgetown (Guyana)",
    "Göteborg",
    "Hamburg",
    "Harare",
    "Helsinki",
    "Honolulu",
    "Houston",
    "Hà Nội",
    "Jakarta",
    "Juba",
    "Kampala",
    "Kansas City",
    "Kigali",
    "Kingston",
    "Kinshasa",
    "Köln",
    "København",
    "La Habana",
    "La Paz",
    "Las Vegas",
    "Libreville",
    "Lilongwe",
    "Lima",
    "Lisboa",
    "Ljubljana",
    "Lomé",
    "London",
    "Los Angeles",
    "Luanda",
    "Lungsod ng Maynila",
    "Lusaka",
    "Lëtzebuerg",
    "Madrid",
    "Malabo",
    "Managua",
    "Manaus",
    "Maputo",
    "Maseru",
    "Mbabane",
    "Melbourne",
    "Miami",
    "Milano",
    "Milwaukee",
    "Minneapolis",
    "Monaco",
    "Monrovia",
    "Montevideo",
    "Montreal",
    "München",
    "Nairobi",
    "Nantes",
    "Nashville",
    "Nassau",
    "New Orleans",
    "New York City",
    "Niamey",
    "Nuuk",
    "Oslo",
    "Ottawa",
    "Ouagadougou",
    "Oulu",
    "Paramaribo",
    "Paris",
    "Perth",
    "Philadelphia",
    "Phoenix",
    "Pittsburgh",
    "Port of Spain",
    "Port-au-Prince",
    "Portland",
    "Porto Alegre",
    "Porto-Novo",
    "Pot Mosbi",
    "Praha",
    "Pretoria",
    "Prishtinë",
    "Quito",
    "Recife",
    "Reykjavík",
    "Riga",
    "Rio de Janeiro",
    "Roma",
    "Salt Lake City",
    "San Francisco",
    "San José",
    "San Juan",
    "San Salvador",
    "Santiago de Chile",
    "Santo Domingo",
    "Seattle",
    "Sevilla",
    "Springfield (Missouri)",
    "Stockholm",
    "Strasbourg",
    "Sydney",
    "Tallinn",
    "Tegucigalpa",
    "Tijuana",
    "Tirana",
    "Tolhuin",
    "Toronto",
    "Toulouse",
    "Tromsø",
    "Tórshavn",
    "Vaduz",
    "Vancouver",
    "Vilnius",
    "Warszawa",
    "Washington, D.C.",
    "Wellington",
    "Wien",
    "Windhoek",
    "Winnipeg",
    "Yamoussoukro",
    "Yaoundé",
    "Zagreb",
    "Αθήνα",
    "Λευκωσία",
    "Београд",
    "Бишкек",
    "Владивосток",
    "Донецьк",
    "Душанбе",
    "Київ",
    "Москва",
    "Мурманск",
    "Мінск",
    "Новосибирск",
    "Нұр-Сұлтан",
    "Пермь",
    "Петропавловск-Камчатский",
    "Подгорица",
    "Санкт-Петербург",
    "Сарајево",
    "Скопје",
    "София",
    "Тошкент",
    "Улаанбаатар",
    "Хатанга",
    "Якутск",
    "Երևան",
    "ירושלים\u200e",
    "أبو ظبي\u200e",
    "أسمرة\u200e",
    "اسلام آباد\u200e",
    "الخرطوم\u200e",
    "الدوحة\u200e",
    "الرياض\u200e",
    "الرِّبَاط\u200e",
    "العيون\u200e",
    "المنامة\u200e",
    "اِنْجَمِينَا\u200e",
    "بغداد\u200e",
    "بيروت\u200e",
    "تهران\u200e",
    "تونس\u200e",
    "دمشق\u200e",
    "صنعاء\u200e",
    "طرابلس\u200e",
    "عمان\u200e",
    "كوالا لومڤور\u200e",
    "مدينة الجزائر\u200e",
    "مسقط\u200e",
    "نواكشوط\u200e",
    "کابل\u200e",
    "काठमाडौँ",
    "नई दिल्ली",
    "मुंबई",
    "ঢাকা",
    "சிங்கப்பூர் குடியரசு",
    "කොළඹ",
    "กรุงเทพมหานคร",
    "ວຽງຈັນ",
    "ཐིམ་ཕུ་",
    "နေပြည်တော်",
    "თბილისი",
    "አዲስ አበባ",
    "រាជធានី​ភ្នំពេញ",
    "上海市",
    "临沂市",
    "乌鲁木齐市",
    "北京市",
    "厦门市",
    "台北",
    "広島市",
    "成都市",
    "昆明市",
    "東京",
    "武汉市",
    "澳門",
    "西安市",
    "重庆市",
    "长春市",
    "香港",
    "서울특별시",
    "평양",
]


def get_city_id(city_name) -> int:
    return all_cities.index(city_name)


def get_city_name(city_id) -> str:
    return all_cities[city_id]


class City:

    def __init__(self, name) -> None:
        super().__init__()
        self._name = name
        self._index = get_city_id(name)
        self._latitude = 0.0
        self._longitude = 0.0
        self._population = 0
        self._connections = []
        self._economyStrength = 0
        self._governmentStability = 0
        self._hygieneStandards = 0
        self._populationAwareness = 0
        self._events = []
        self._pathogens = []

    def get_name(self):
        return self._name

    def get_city_id(self):
        return self._index

    def get_latitude(self):
        return self._latitude

    def get_longitude(self):
        return self._longitude

    def get_population(self):
        return self._population

    def get_connections(self):
        return self._connections

    def get_economy_strength(self):
        return self._economyStrength

    def get_government_stability(self):
        return self._governmentStability

    def get_hygiene_standards(self):
        return self._hygieneStandards

    def get_population_awareness(self):
        return self._populationAwareness

    def get_events(self):
        return self._events

    def get_pathogens(self):
        return self._pathogens

    @staticmethod
    def from_json(city_json):
        # remove U+200E LEFT-TO-RIGHT MARK character
        city = City(city_json['name'])
        city._latitude = city_json['latitude']
        city._longitude = city_json['longitude']
        city._population = city_json['population']
        city._connections = city_json['connections']
        city._economyStrength = strength_to_int(city_json['economy'])
        city._governmentStability = strength_to_int(city_json['government'])
        city._hygieneStandards = strength_to_int(city_json['hygiene'])
        city._populationAwareness = strength_to_int(city_json['awareness'])

        if 'events' in city_json:
            for eventJson in city_json['events']:
                event = Event.from_json(eventJson)
                city._events.append(event)

                if event.get_event_type() == 'outbreak':
                    city._pathogens.append(event.get_pathogen())

        return city

