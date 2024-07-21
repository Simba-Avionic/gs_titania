# import math

# SPEED_OF_LIGHT = 3e8  # Speed of light in m/s

def rssi2dbm(rssi_val):
    return rssi_val/1.9-127
def dbm2rssi(dbm_val):
    return (dbm_val+127)/1.9

# def estimate_distance(freq,rssi_local,rssi_remote):
#     fspl = abs(rssi2dbm(rssi_remote) - rssi2dbm(rssi_local)) # free space path loss
#     return 10**((fspl-20*math.log10(freq)-20*math.log10(4*math.pi/SPEED_OF_LIGHT))/20)