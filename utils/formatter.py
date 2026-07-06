def format_uptime(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h}h {m}m"