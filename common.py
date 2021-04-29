def log(str):
    import datetime

    print(f"{datetime.datetime.now()}   {str}")

def flatten(arr):
    return [item for subl in arr for item in subl]

def string_to_datetime(format, dt_str):
    from datetime import datetime

    return datetime.strptime(dt_str, format)

def format_datetime(dt):
    from datetime import datetime

    format = '%Y-%m-%d %H:%M'
    
    return dt.strftime(format)

def is_file_exist(fileName):
    import os

    return os.path.isfile(fileName)

def write_cache(cacheFileName, timeslots):
    import json

    with open(cacheFileName, 'w') as cacheFile:
        json.dump(timeslots, cacheFile)

def read_cache(cacheFileName):
    import json
    from datetime import datetime

    cacheFile = open(cacheFileName)
    timeslots_raw = json.load(cacheFile)
    cacheFile.close

    timeslots = [datetime.utcfromtimestamp(ts) for ts in timeslots_raw]

    return timeslots

def remove_old_timeslots(cacheFileName, timeslots):
    cachedTimeslots = read_cache(cacheFileName)

    newTimeslots = [ts for ts in timeslots if ts not in cachedTimeslots]

    return newTimeslots

def send_email(smtp_host, smtp_port, userName, password, msg):
    import smtplib
    # import ssl

    server = smtplib.SMTP(smtp_host, smtp_port)
    # context = ssl.create_default_context()
    server.starttls()
    server.login(userName, password)

    server.send_message(msg)

    server.quit()

    log(f"Sent email to {msg['Bcc']}")
