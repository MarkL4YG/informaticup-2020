MAX_CITIES = 10
END_ROUND_ACTION = 0
MAX_CONNECTIONS = 10

# Action-Space:
# do_nothing[1], [quarantine[2], close-airport[3], hygienic_measures [4], political-influence[5],
# call-for-elections[6], launch-campaign [7],
# vaccine[8], vaccine2[9], vaccine3[10], vaccine4[11], vaccine5[12],
# med1[13], med2[14], med3[15], med4[16], med5[17]]
BASE_ACTIONSPACE = 16
MAX_ACTIONSPACE = 1 + BASE_ACTIONSPACE * MAX_CITIES
MAX_CITY_ACTIONSPACE = MAX_ACTIONSPACE - 1
MAX_PATHOGENS = 5
END_EPISODE_RESPONSE = "END_EPISODE"
NEUTRAL_REWARD = 0
PATH_TO_IC20 = "ic20_linux"
