import common, os

PROVIDER_LOCATION_IDS = os.environ['PROVIDER_LOCATION_IDS'].split(',')
SMTP_HOST = os.environ['SMTP_HOST']
SMTP_PORT = os.environ['SMTP_PORT']
SENDER_USERNAME = os.environ['SENDER_USERNAME']
SENDER_PASSWORD = os.environ['SENDER_PASSWORD']
RECIPIENTS = os.environ['RECIPIENTS'].split(',')

CACHE_FILENAME = "valley_vaccine_cache.json"

# LOCATIONS = ['Paramus Vaccination Center (PFIZER)']

PROVIDER_LOCATION_IDS = ['pr_SFFOirUdmkObdq2f6L6k1B|lo_u78b6Fvwp0Ot7TW67q6qLx']
# PROVIDER_LOCATION_IDS = {'Ridgewood Vaccination Center at The Valley Hospital (J&J)': 'pr_uOYVNjhmlk-FBQbdY9Y0mx|lo_a1ZXOxJUPE2kpG_FWThIQB', 'Paramus Vaccination Center (PFIZER)': 'pr_SFFOirUdmkObdq2f6L6k1B|lo_u78b6Fvwp0Ot7TW67q6qLx'}

def inquire_availability(providerLocationIds):
    responses = map(get_request, providerLocationIds)

    timeslots = parse(responses)

    common.log(f"timeslots: {[common.format_datetime(ts) for ts in timeslots]}")

    return timeslots

def get_request(providerLocationId):
    import requests
    from requests.structures import CaseInsensitiveDict

    url = "https://api.zocdoc.com/directory/v2/gql"

    headers = CaseInsensitiveDict()
    headers["authority"] = "api.zocdoc.com"
    headers["sec-ch-ua"] = """Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"""
    headers["x-zd-url"] = "https://www.zocdoc.com/wl/valleycovid19vaccination/practice/64268?reason_visit=5243"
    headers["zd-application-name"] = "patient-web-app"
    headers["x-zdata"] = "eyJob3N0Ijoid3d3LnpvY2RvYy5jb20ifQ=="
    headers["zd-tracking-id"] = "051e8088-3bbc-42c0-8b75-490158fbfb40"
    headers["zd-session-id"] = "5c1e1fc108d8477dbef0eea391837e44"
    headers["x-zd-referer"] = "https://www.zocdoc.com/vaccine/screener?directoryId=1139"
    headers["x-zd-application"] = "patient-web-app"
    headers["zd-referer"] = "https://www.zocdoc.com/vaccine/screener?directoryId=1139"
    headers["zd-url"] = "https://www.zocdoc.com/wl/valleycovid19vaccination/practice/64268?reason_visit=5243"
    headers["sec-ch-ua-mobile"] = "?0"
    headers["user-agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
    headers["zd-pageview-id"] = "03e184b76759811446f089a81768dfbb"
    headers["accept"] = "*/*"
    headers["content-type"] = "application/json"
    headers["zd-user-agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
    headers["dnt"] = "1"
    headers["origin"] = "https://www.zocdoc.com"
    headers["sec-fetch-site"] = "same-site"
    headers["sec-fetch-mode"] = "cors"
    headers["sec-fetch-dest"] = "empty"
    headers["referer"] = "https://www.zocdoc.com/"
    headers["accept-language"] = "en-US,en;q=0.9"

    data = '{"operationName":"providerLocationsAvailability","variables":{"directoryId":"1139","insurancePlanId":"-1","isNewPatient":false,"numDays":7,"procedureId":"5243","widget":false,"providerLocationIds":["'+ providerLocationId + '"]},"query":"query providerLocationsAvailability($directoryId: String, $insurancePlanId: String, $isNewPatient: Boolean, $isReschedule: Boolean, $jumpAhead: Boolean, $firstAvailabilityMaxDays: Int, $numDays: Int, $procedureId: String, $providerLocationIds: [String], $searchRequestId: String, $startDate: String, $timeFilter: TimeFilter, $widget: Boolean) {  providerLocations(ids: $providerLocationIds) {    id,    ...availability,__typename  }}fragment availability on ProviderLocation {  id,  provider {    id,    monolithId,    __typename  },  location {    id,    monolithId,    state, phone,    __typename  }  availability(directoryId: $directoryId, insurancePlanId: $insurancePlanId, isNewPatient: $isNewPatient, isReschedule: $isReschedule, jumpAhead: $jumpAhead, firstAvailabilityMaxDays: $firstAvailabilityMaxDays, numDays: $numDays, procedureId: $procedureId, searchRequestId: $searchRequestId, startDate: $startDate, timeFilter: $timeFilter, widget: $widget) {    times {,      date,      timeslots {        isResource,        startTime,        __typename      },      __typename    },    firstAvailability {      startTime,      __typename,    },    showGovernmentInsuranceNotice,    timesgridId,    today,    __typename  },  __typename}"}'

    resp = requests.post(url, headers=headers, data=data)

    common.log(resp.status_code)

    return resp.text

def parse_response(resp):
    import sys, json

    json_response = json.loads(resp)

    timeslots_raw = [[timeslot.get('startTime') for timeslot in time.get('timeslots')] for time in json_response["data"]["providerLocations"][0]["availability"]["times"]]

    timeslots_by_day = list(filter(lambda ts: len(ts) > 0, list(timeslots_raw)))

    timeslots = common.flatten(timeslots_by_day)

    return timeslots

def parse(responses):
    timeslots_raw = common.flatten(list(map(parse_response, responses)))

    format = '%Y-%m-%dT%H:%M:%S%z'

    timeslots = [common.string_to_datetime(format, timeslot) for timeslot in timeslots_raw]

    return timeslots

def create_valley_vacine_message(userName, recipients, timeslots):
    from email.message import EmailMessage

    subject = 'Vaccine Appt Available'
    registrationUrl = 'zocdoc.com/wl/valleycovid19vaccination/patientvaccine'
    message = f"Valley Hospital has new vaccine spots available. New timeslots available are {', '.join(map(common.format_datetime, timeslots))}. {registrationUrl}"

    msg = EmailMessage()
    msg.set_content(message)

    msg['Subject'] = subject
    msg['From'] = userName
    msg['Bcc'] = recipients

    return msg

def notify_recipients(smtp_host, smtp_port, userName, password, recipients, timeslots):
    msg = create_valley_vacine_message(userName, recipients, timeslots)

    common.send_email(smtp_host, smtp_port, userName, password, msg)

def serialize_cache(timeslots):
        timestamped_timeslots = [ts.timestamp() for ts in timeslots]

        return timestamped_timeslots

def main():
    timeslots = inquire_availability(PROVIDER_LOCATION_IDS)

    new_timeslots = common.remove_old_timeslots(CACHE_FILENAME, timeslots) if common.is_file_exist(CACHE_FILENAME) else timeslots

    if len(new_timeslots) > 0:
        notify_recipients(SMTP_HOST, SMTP_PORT, SENDER_USERNAME, SENDER_PASSWORD, RECIPIENTS, new_timeslots)
    else:
        common.log("No new availability at this time")

    serialized_timeslots = serialize_cache(timeslots)

    common.write_cache(CACHE_FILENAME, serialized_timeslots)

main()
