from models.event import Event
from models.format_utils import strength_to_int
from models.pathogen import Pathogen

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
    "ירושלים",
    "أبو ظبي",
    "أسمرة",
    "اسلام آباد",
    "الخرطوم",
    "الدوحة",
    "الرياض",
    "الرِّبَاط\u200e",
    "العيون",
    "المنامة",
    "اِنْجَمِينَا",
    "بغداد",
    "بيروت",
    "تهران",
    "تونس",
    "دمشق",
    "صنعاء\u200e",
    "طرابلس",
    "عمان",
    "كوالا لومڤور",
    "مدينة الجزائر",
    "مسقط",
    "نواكشوط",
    "کابل",
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
        self.name: str = name
        self.index = get_city_id(name)
        self.latitude: float = 0.0
        self.longitude: float = 0
        self.population: int = 0
        self.infected_population: int = 0
        self.connections: list = []
        self.economy_strength: int = 0
        self.government_stability: int = 0
        self.hygiene_standards: int = 0
        self.population_awareness: int = 0
        self.events: list = []
        self.pathogens: list = []
        self.under_quarantine: bool = False
        self.airport_closed: bool = False

    @staticmethod
    def from_json(city_json):
        # remove U+200E LEFT-TO-RIGHT MARK character
        city = City(city_json['name'])
        city.latitude = city_json['latitude']
        city.longitude = city_json['longitude']
        city.population = city_json['population']
        city.connections = city_json['connections']
        city.economy_strength = strength_to_int(city_json['economy'])
        city.government_stability = strength_to_int(city_json['government'])
        city.hygiene_standards = strength_to_int(city_json['hygiene'])
        city.population_awareness = strength_to_int(city_json['awareness'])

        if 'events' in city_json:
            for eventJson in city_json['events']:
                event = Event.from_json(eventJson)
                city.events.append(event)

                if event.event_type == 'outbreak':
                    event_pathogen: Pathogen = event.pathogen
                    event_pathogen.prevalence = event.prevalence
                    city.pathogens.append(event_pathogen)
                    city.infected_population += city.population * event_pathogen.prevalence
                elif event.event_type == 'quarantine':
                    city.under_quarantine = True
                elif event.event_type == 'airportClosed':
                    city.airport_closed = True
        return city
