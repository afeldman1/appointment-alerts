import common, os

SMTP_HOST = os.environ['SMTP_HOST']
SMTP_PORT = os.environ['SMTP_PORT']
SENDER_USERNAME = os.environ['SENDER_USERNAME']
SENDER_PASSWORD = os.environ['SENDER_PASSWORD']
RECIPIENTS = os.environ['RECIPIENTS'].split(',')

CACHEFILENAME = "nj_mvc_real_id_cache.json"

def get_request(location_id):
    import requests
    from requests.structures import CaseInsensitiveDict
    import urllib.parse

    appt_type = 12 #Real-ID appointments
    base_url = "https://telegov.njportal.com/njmvc/AppointmentWizard"
    url = base_url + "/" + str(appt_type) + "/" + str(location_id)

    headers = CaseInsensitiveDict()
    headers["authority"] = "telegov.njportal.com"
    headers["cache-control"] = "max-age=0"
    headers["sec-ch-ua-mobile"] = "?0"
    headers["upgrade-insecure-requests"] = "1"
    headers["dnt"] = "1"
    headers["accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    headers["sec-fetch-site"] = "same-origin"
    headers["sec-fetch-mode"] = "navigate"
    headers["sec-fetch-user"] = "?1"
    headers["sec-fetch-dest"] = "document"
    headers["referer"] = "https://telegov.njportal.com/njmvc/AppointmentWizard/6"
    headers["accept-language"] = "en-US,en;q=0.9,ru-UA;q=0.8,ru;q=0.7"
    # headers["cookie"] = ".AspNetCore.Antiforgery.9fXoN5jHCXs=CfDJ8KLB7EApaiNLk8lH9KgP3x9HeIlTM5hDXFDgDIEn7DX22UzWPJKfAwR7yuk1VI1kXQ4wPCS3_ooR0ZHWdbrTI8QWcaHXNYuuEqyGED-F7rCS280R-zHhv1e7s3tbXz7xuwXIr3Tt7AlJWWs9SqYprWw; .AspNetCore.Session=CfDJ8KLB7EApaiNLk8lH9KgP3x99J49fdpo%2BmRYNpyaq9O0NIrg9L2yAd0263U7QtSuTVFRaRT4Z01%2BpQXYaK2xkbDlwqTd8pH10GlncpwbJR2H3LTibctP0GSpRoz0f8xPLp6eheq61ONFmcrsgWOmERfqSGls3ZllmlkzdP3kZ6A84; ARRAffinity=8d50cbedd4717d737dbd8ff85daddc7a1901ca485876687df9290e8c23a81d1a; ARRAffinitySameSite=8d50cbedd4717d737dbd8ff85daddc7a1901ca485876687df9290e8c23a81d1a; _ga=GA1.2.1961956974.1619647250; _gid=GA1.2.879471787.1619647250; ASLBSA=77872f3375735e7bfcbbe43fb5990ca4831c942e8b447c5abc892c7b8605eb57; ASLBSACORS=77872f3375735e7bfcbbe43fb5990ca4831c942e8b447c5abc892c7b8605eb57"
    headers["sec-gpc"] = "1"

    resp = requests.get(url, headers=headers)

    common.log(f"api response: {resp.status_code}")
    
    return resp.content

def inquire_availability(location_id):
    response = get_request(location_id)

    timeslots = parse_response(response)

    common.log(f"timeslots: {[common.format_datetime(ts) for ts in timeslots]}")

    return timeslots

def parse_response(resp):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp, 'html.parser')

    timeslots = list()

    for div in soup.find_all('div'):
        if div.get("id") == "timeslots":
            for anchor in div.find_all('a'):
                href = anchor.get("href").split('/')

                time = href[len(href)-1].zfill(4)
                date = href[len(href)-2]

                format = '%Y-%m-%d%H%M'

                date_time = common.string_to_datetime(format, date + time)
                timeslots.append(date_time)

    return timeslots

def create_mvc_real_id_message(userName, recipients, timeslots):
    from email.message import EmailMessage

    subject = 'MVC Appt Available'
    registrationUrl = f'https://telegov.njportal.com/njmvc/AppointmentWizard/12/{timeslots[0][1]}'
    message = f"MVC {timeslots[0][0]} has new appts available. New timeslots available are {', '.join(map(common.format_datetime, timeslots[1]))}. {registrationUrl}"

    msg = EmailMessage()
    msg.set_content(message)

    msg['Subject'] = subject
    msg['From'] = userName
    msg['Bcc'] = recipients

    return msg

def notify_recipients(smtp_host, smtp_port, userName, password, recipients, timeslots):
    msg = create_mvc_real_id_message(userName, recipients, timeslots)

    common.send_email(smtp_host, smtp_port, userName, password, msg)

def serialize_cache(timeslots):
        timestamped_timeslots = list(filter(lambda ts: len(ts) > 0, [[ts.timestamp() for ts in location[1]] for location in timeslots]))

        return timestamped_timeslots

def main():
    locations = [
        ("wayne", 24),
        ("oakland", 25),
        ("paterson", 26)
    ]

    timeslots = [(location_id, inquire_availability(location_id[1])) for location_id in locations]

    # new_timeslots = common.remove_old_timeslots(CACHEFILENAME, timeslots) if common.is_file_exist(CACHEFILENAME) else timeslots

    for new_ts in timeslots:
        if len(new_ts[1]) > 0:
            notify_recipients(SMTP_HOST, SMTP_PORT, SENDER_USERNAME, SENDER_PASSWORD, RECIPIENTS, new_ts)
        else:
            common.log("No new appts at this time")

    serialized_timeslots = serialize_cache(timeslots)

    if len(serialized_timeslots) > 0: common.write_cache(CACHEFILENAME, serialized_timeslots)

main()
