from models import actions

MAX_CITIES = 5
END_ROUND_ACTION = 0
MAX_CONNECTIONS = 10

# global action-space:
# [end_round[0],
# develop: vaccine[1], vaccine2[2], vaccine3[3], vaccine4[4], vaccine5[5],
# develop: med1[6], med2[7], med3[8], med4[9], med5[10]] -> 11 actions
# city action-space:
# [quarantine[11], close-airport[12], hygienic_measures [13], political-influence[14],
# call-for-elections[15], launch-campaign [16],
# deploy: vaccine[17], vaccine2[18], vaccine3[19], vaccine4[20], vaccine5[21],
# deploy: med1[22], med2[23], med3[24], med4[25], med5[26]] -> 16 actions => 27 Actions in total
GLOBAL_ACTIONSPACE = 11
CITY_ACTIONSPACE = 16
MAX_ACTIONSPACE = GLOBAL_ACTIONSPACE + CITY_ACTIONSPACE * MAX_CITIES
MAX_CITY_ACTIONSPACE = MAX_ACTIONSPACE - 1
MAX_PATHOGENS = 5
END_EPISODE_RESPONSE = "END_EPISODE"
NEUTRAL_REWARD = 0
PATH_TO_IC20 = "./ic20_linux"
INVALID_ACTION = actions.end_round()  # todo: check if this could be also a string, if so make this a string
