import time
import datetime
 
def countdown(m, s):
 
    # Calculate the total number of seconds
    total_seconds = m * 60 + s
 
    while total_seconds > 0:

        timer = datetime.timedelta(seconds = total_seconds)
        time.sleep(1)
 
        # Reduces total time by one second
        total_seconds -= 1
 
    return 0
