import time

def get_uptime(start_time):
    """Get the uptime of the bot."""
    uptime_seconds = int(time.time() - start_time)
    uptime_string = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
    return uptime_string