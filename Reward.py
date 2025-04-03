from shared_data import king_state


# while running it needs to monitor the y value, it knows that it has found a platform if the vy is 0 and the y is above 0
# bottom of the level is at 570, the platform ys are at 510, 470, 430, 370, 310, 270, 190, 150, 130, 90
# the player starts at 500
# reward = 10(min_height_when_vy=0 - max_height_when_vy=0)
# the issue is at the apex of a jump it has vy of 0, but not on a platform
# instead it's going to record the end y value, and if the latest value is less than the highest one, then it'll take the latest one



def reward():
    while True:
        values = [king_state['y'], king_state['vy']]

        min_val = 0
        # This value is should be the lowest it starts, so on this level it will be 570
        max_val = 1000000
        # This value is how high it climbs, so it will start at 570, but it will be 510 if it reaches the first platform

        if values[1] == 0:
            min_val = max(min_val, values[0])
            max_val = min(max_val, values[0])