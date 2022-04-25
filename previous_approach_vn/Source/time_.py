def convert2timegap(duration):
    time_lap=duration.split('-')
    start_hour=time_lap[0]
    finish_hour=time_lap[1]
    starting_point=int(start_hour.split(':')[0])
    finishing_pont=int(finish_hour.split(':')[0])
    return starting_point,finishing_pont