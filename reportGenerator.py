import json
import requests
import os
import sys
import argparse
import urllib
import time
import getpass
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import configparser
#--------------------------------------------------------------------------------------------------------------------------------------------------
#Python version check
if sys.version_info < (3, 0):
    sys.stdout.write("Requires Python 3.x\n")
    sys.exit(1)

FIELD_CUSTNAME = "custName"
FIELD_DEPTNAME = "deptName"
FIELD_CUST_ID = "custId"
FIELD_DEPT_ID = "deptId"

FIELD_TOTALROWS = "totalRows"
PAGE_SIZE = 10000

token_expire_time = 0
access_token_from_orch = ''

REPORT_GENERATION_STATUS_SUCCESS = "Success"
REPORT_GENERATION_STATUS_FAILED = "Failed"
REPORT_GENERATION_STATUS_INPROGRESS = "Inprogress"
REPORT_GENERATION_STATUS_NO_DATA_FOUND = "NoData"

REPORT_GENERATION_STATUS_CHECK_INTERVAL = 10

DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

FILE_DATE_TIME_FORMAT = "%Y%m%d-%I%M%S"
LOG_FILE_PREFIX = "reportGenerator_"
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')

parser = argparse.ArgumentParser(
 description='Start report generation at Orchestrator and download report after successful generation' ,
 epilog="Start report generation at Orchestrator and download report after successful generation"
 )
parser.add_argument('--username', help='(Optional) Orchestrator user username')
parser.add_argument('--password', help='(Optional) Orchestrator user password')
parser.add_argument('--fromdate',
					help="Filter out records from the date. The expected Date format is 'yyyy-mm-dd HH:MM:SS'. (Optional for version_information_master report) ")
parser.add_argument('--todate',
					help="(Optional) Filter out records to date. The expected Date format is 'yyyy-mm-dd HH:MM:SS'.")
parser.add_argument('--domain', help='Filter out records with the domain name.(Optional for version_information_master report)')
parser.add_argument('--subdomain', help='Filter out records with the subdomain name. (Optional for version_information_master report)')
parser.add_argument('--format', help='(Optional) Set report format CSV or PDF. This option is applicable only for vulnerabilities_stride type reports. The default is CSV.')
parser.add_argument('--reportType', help='(Mandatory) Set required report type value from application_details, application_forensic, secure_application_policy_details, attacked_applications_details, discovered_application_details, owasp_top_10_report, vulnerabilities_stride_short, vulnerabilities_stride_long, application_forensic_session_details, pcre_policy_details, application_model, application_model_default, application_model_threat_dragon, application_model_threat_dragon_plus, application_model_microsoft_tmt, application_model_architecture, application_model_architecture_and_threat, application_version_information, version_information_master.')
parser.add_argument('--templateName', help='(Optional) Set the template name to integrate the Threat Dragon model with the provided template. Applicable only with reportType application_model_threat_dragon and application_model_threat_dragon_plus.')
parser.add_argument('--metadataFilter', help='(Optional) Set the comma seperated metadata attribute key and value pairs to filter out processes. example srnumber:4582,srName:sampleService')
args = parser.parse_args()

class Arg:
    report_type = args.reportType
    if report_type is None:
        print("argument --reportType is missing")
        parser.print_help()
        exit()

    fromdate = args.fromdate
    if report_type != 'version_information_master' and fromdate is None:
        print("argument --fromdate is missing")
        parser.print_help()
        exit()

    todate = args.todate

    start_timestamp = None
    end_timestamp = None
    if fromdate:
        try:
            timestamp = time.time()
            utcOffset = (datetime.fromtimestamp(timestamp) - datetime.utcfromtimestamp(
                timestamp)).total_seconds()

            start_timestamp = datetime.strptime(fromdate, DATE_TIME_FORMAT)
            start_timestamp = int(start_timestamp.timestamp() + utcOffset)

            if todate:
                end_timestamp = datetime.strptime(todate, DATE_TIME_FORMAT)
                end_timestamp = int(end_timestamp.timestamp() + utcOffset)

            if not end_timestamp:
                end_timestamp = int(timestamp + utcOffset)

        except ValueError as e:
            print("Error while parsing data : ", e)
            print(e)
            exit()


    domain = args.domain
    if report_type != 'version_information_master' and domain is None:
        print("argument --domain is missing")
        parser.print_help()
        exit()

    subDomain = args.subdomain
    if report_type != 'version_information_master' and subDomain is None:
        print("argument --subdomain is missing")
        parser.print_help()
        exit()

    format = args.format
    if format and (str(format).lower() != 'pdf' and str(format).lower() != 'csv'):
        print("Invalid value for --format. Please set it to pdf or csv")
        parser.print_help()
        exit()

    templateName = args.templateName
    metadataFilter = args.metadataFilter


execution_date_time_str = datetime.now().strftime(FILE_DATE_TIME_FORMAT)

log_file = LOG_FILE_PREFIX + execution_date_time_str + ".log"

log_handler = RotatingFileHandler(log_file, mode='a', maxBytes=10 * 1024 * 1024,
								  backupCount=1, encoding=None, delay=0)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.DEBUG)
app_log = logging.getLogger()
app_log.setLevel(logging.DEBUG)
app_log.addHandler(log_handler)


def print_info(message):
	print(message)
	logging.info(message)


def print_error(message, e, data):
    print(message)
    logging.error(message)
    if e:
        print(e)
        logging.error(e)
    if data:
        print(data)
        logging.error(data)


def print_warning(message):
	print(message)
	logging.warning(message)

CONFIG_FILE_NAME = 'commonConfig.cnf'
common_file_locations = ["./", '../common/']
CONFIG_FILE = None

for config_path in common_file_locations:
	config_file_path = os.path.join(config_path, CONFIG_FILE_NAME)
	if os.path.exists(config_file_path):
		CONFIG_FILE = config_file_path

if not CONFIG_FILE:
	print_error("Config file " +  CONFIG_FILE_NAME + " not found.", None, None)
	exit()

config = configparser.RawConfigParser()
config.read(CONFIG_FILE)
if not config.has_section('Orchestrator'):
    print_error("Invalid config file, Section 'Orchestrator' is not found in the config file.", None, None)
    exit()

if not config.has_option('Orchestrator', 'ORCH_URL'):
    print_error("ORCH_URL is not set, please set it in the config file.", None, None)
    exit()

if not config.has_option('Orchestrator', 'CA_FILE'):
    print_error("CA_FILE is not set, please set it in the config file.", None, None)
    exit()

ORCH_URL = config.get('Orchestrator', 'ORCH_URL')
ca_file_Path = config.get('Orchestrator', 'CA_FILE')

CA_FILE = None
ca_file_name = None

if not ca_file_Path:
	print_error("CA file not found. Please configure the 'CA_FILE' property in " + CONFIG_FILE_NAME, None, None)
	exit()

if os.path.exists(ca_file_Path):
	CA_FILE = ca_file_Path
else:
	print_warning("Configured CA file " + ca_file_Path + " not found. Searching for common locations.")
	ca_file_name = os.path.basename(ca_file_Path)

if not CA_FILE:
	for config_path in common_file_locations:
		config_file_path = os.path.join(config_path, ca_file_name)
		if os.path.exists(config_file_path):
			CA_FILE = config_file_path
			print_info("Using CA file at location " + CA_FILE)

if not CA_FILE:
	print_error("CA file not found. Please configure the 'CA_FILE' property in " + CONFIG_FILE_NAME, None, None)
	exit()

USERNAME = None
if config.has_option('Orchestrator', 'USERNAME'):
    USERNAME = config.get('Orchestrator', 'USERNAME')

PASSWORD = None
if config.has_option('Orchestrator', 'PASSWORD'):
    PASSWORD = config.get('Orchestrator', 'PASSWORD')


def validate_and_get_username(username):
    # Validate Orchestrator user username argument
    if username is None:
        username = USERNAME
    if username is None or len(username.strip()) == 0:
        username = str(input("Enter Orchestrator username:"))
        if username is None or len(username.strip()) == 0:
            print("Invalid or empty Orchestrator username")
            validate_and_get_username(username)
    return username


def validate_and_get_password(password):
    # Validate Orchestrator user password argument
    if password is None:
        password = PASSWORD
    if password is None or len(password.strip()) == 0:
        password = getpass.getpass(prompt="Enter Orchestrator user password:")
        if password is None or len(password.strip()) == 0:
            print("Invalid or empty Orchestrator user password")
            validate_and_get_password(password)
    return password


username = validate_and_get_username(args.username)
password = validate_and_get_password(args.password)


def get_access_token_from_orch(username, password):
    # -----Getting access token from Orchestrator BEGIN-----
    print_info("Getting access token from orchestrator")
    oauth_url = ORCH_URL + "/oauth/token"
    data = dict(
        username=username,
        password=password,
        grant_type='password',
    )

    headers = {}
    try:
        response = requests.post(oauth_url, data=data, headers=headers, verify=False)
        if response.status_code == 200:
            jsonResponse = response.json()
            return jsonResponse
        elif response.status_code == 401 or response.status_code == 403:
            print_error("Invalid user credentials", None, None)
            exit()
        elif response.status_code == 400:
            print_error("Bad Request or Invalid user credentials", None, None)
            exit()
        else:
            print_error("Cannot get accessToken from Orchestrator", None, None)
            exit()
    except requests.exceptions.ConnectionError as e:  # quests.packages.urllib3.exceptions.NewConnectionError :
        print_error("Cannot connect to Orchestrator", e, None)
        print(e)
        exit()


def get_access_token():
    seconds = int(round(time.time()))
    global access_token_from_orch
    global token_expire_time
    if seconds < token_expire_time:
        return access_token_from_orch
    else:
        token_response = get_access_token_from_orch(username, password)
        #token_response = json.loads(token_response)
        access_token_from_orch = token_response["access_token"]
        expires_in = token_response["access_token_expires_in"]
        seconds = int(round(time.time()))

        token_expire_time = seconds + expires_in - 10
        return access_token_from_orch


def get_customer_information(access_token, customer_name):
    # -----Getting customer information from Orchestrator BEGIN-----
    print_info("Getting Customer information from the Orchestrator")
    url_params = {'custName': customer_name}
    encoded_url_params = urllib.parse.urlencode(url_params)
    request_url = ORCH_URL + "/api/customer/views.ws?" + encoded_url_params
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }
    try:
        response = requests.get(request_url, headers=headers, verify=False)
        if response.status_code == 200:
            customer_response = response.json()
            customers = customer_response["listCustomers"]
            if len(customers) > 0:
                customer_json = customers[0]
                return customer_json
            else:
                print_error("No Customer with the name " + customer_name + " found for user.", None, None)
                return None
        else:
            print_error("Error while getting customer details: " + response.text, None, None)
            return None
    except requests.exceptions.RequestException as e:
        print_error("Error occurred while getting Customer information from the Orchestrator: ", e, None)
        exit()


def get_department_information(access_token, department_name, customer_id):
    # -----Getting department information from Orchestrator BEGIN-----
    print_info("Getting Department information from the Orchestrator")
    url_params = {'custId': str(customer_id), 'deptName': department_name}
    encoded_url_params = urllib.parse.urlencode(url_params)
    request_url = ORCH_URL + "/api/department/views.ws?" + encoded_url_params

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }
    try:
        response = requests.get(request_url, headers=headers, verify=False)
        if response.status_code == 200:
            department_response = response.json()
            departments = department_response["listDepartments"]
            if len(departments) > 0:
                department_json = departments[0]
                return department_json
            else:
                print_error("No Department with the name " + department_name + " found for user.", None, None)
                return None
        else:
            print_error("Error while getting Department details: " + response.text, None, None)
            return None
    except requests.exceptions.RequestException as e:
        print_error("Error occurred while getting Department information from the Orchestrator: ", e, None)
        exit()


def generate_report(access_token, customer_id, department_id, start_timestamp, end_timestamp, report_format, report_type, template_name, metadata_filter):
    # -----Generating report at Orchestrator BEGIN-----
    print_info("Sending report generation request to Orchestrator")
    url_params = {'reportType':report_type}
    if customer_id:
        url_params['domainId'] = customer_id

    if department_id:
        url_params['subDomainId'] = department_id

    if start_timestamp:
        url_params['startTimestamp'] = start_timestamp*1000

    if end_timestamp:
        url_params['endTimestamp'] = end_timestamp*1000

    if report_format:
        url_params["reportFormat"] = report_format

    if template_name:
        url_params["templateName"] = template_name

    if metadata_filter:
        url_params["metadataFilter"] = metadata_filter

    encoded_url_params = urllib.parse.urlencode(url_params)
    request_url = ORCH_URL + "/api/report/generate?" + encoded_url_params

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }
    try:
        response = requests.get(request_url, headers=headers, verify=False)
        if response.status_code == 200:
            json_response = response.json()
            return json_response["uniqueId"]
        else:
            print_error("Error while generating report with type " + report_type + ": " + response.text, None, None)
            return None
    except requests.exceptions.RequestException as e:
        print_error("Error occurred while generating report from the Orchestrator: ", e, None)
        exit()


def get_report_status(access_token, report_unique_id):
    # -----Getting report status from Orchestrator BEGIN-----
    print_info("Getting report generation status from Orchestrator")
    url_params = {'uniqueId': report_unique_id}

    encoded_url_params = urllib.parse.urlencode(url_params)
    request_url = ORCH_URL + "/api/report/status?" + encoded_url_params

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }
    try:
        response = requests.get(request_url, headers=headers, verify=False)
        if response.status_code == 200:
            json_response = response.json()
            return json_response["status"]
        else:
            print_error("Error while getting report status for report uniqueId " + report_unique_id + ": " + response.text, None, None)
            return None
    except requests.exceptions.RequestException as e:
        print_error("Error while getting report status for report uniqueId: ", e, None)
        exit()


def check_template_at_orchestraotr(access_token, domain_id, template_name):
    # -----Getting report status from Orchestrator BEGIN-----
    print_info("Getting report generation status from Orchestrator")
    url_params = {'templateName': template_name}
    url_params['domainId'] = domain_id

    encoded_url_params = urllib.parse.urlencode(url_params)
    request_url = ORCH_URL + "/api/td-template-info?" + encoded_url_params

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }
    try:
        response = requests.get(request_url, headers=headers, verify=False)
        if response.status_code == 200:
            json_response = response.json()
            total_rows = json_response["totalRows"]
            if total_rows > 0:
                return True
            else:
                return False
        else:
            print_error("Error while verifying Threat Dragon template at Orchestrator with template name " + template_name + ": " + response.text, None, None)
            return None
    except requests.exceptions.RequestException as e:
        print_error("Error while verifying Threat Dragon template at Orchestrator with template name " + template_name, e, None)
        exit()


def download_report_file(access_token, report_unique_id):
    # -----Getting report status from Orchestrator BEGIN-----
    print_info("Downloading report from Orchestrator")
    url_params = {'uniqueId': report_unique_id}

    encoded_url_params = urllib.parse.urlencode(url_params)
    request_url = ORCH_URL + "/api/report/download?" + encoded_url_params

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + access_token
    }
    try:
        response = requests.get(request_url, headers=headers, verify=False)
        if response.status_code == 200:
            content_disposition = response.headers.get("Content-Disposition")
            file_name = content_disposition.split("filename=")[1]
            open(file_name, 'wb').write(response.content)
            return file_name
        else:
            print_error("Error while getting report status for report uniqueId " + report_unique_id + ": " + response.text, None, None)
            return None
    except requests.exceptions.RequestException as e:
        print_error("Error while getting report status for report uniqueId: ", e, None)
        exit()


def execute():
    print("----------------------------------------------------------------------------")
    if Arg.domain:
        customer_json = get_customer_information(get_access_token(), Arg.domain)
        if customer_json is None:
            print_warning("Domain " + Arg.domain + " not found for the user")
            return None

        customer_id = customer_json[FIELD_CUST_ID]

        department_json = get_department_information(get_access_token(), Arg.subDomain, customer_id)
        if department_json is None:
            print_warning("Subdomain  " + Arg.subDomain + " with domain " + Arg.domain + " not found for the user")
            return None

        department_id = department_json[FIELD_DEPT_ID]

        template_name = Arg.templateName
        if template_name and (str(Arg.report_type).lower() == 'application_model_threat_dragon' or str(
                Arg.report_type).lower() == 'application_model_threat_dragon_plus') and not check_template_at_orchestraotr(get_access_token(), customer_id, template_name):
            print_error("Threat Dragon template with template name " + template_name + " not found for domain " + Arg.domain + " at Orchestrator", None, None)
            template_name = None
        unique_id = generate_report(get_access_token(), customer_id, department_id, Arg.start_timestamp, Arg.end_timestamp, Arg.format, Arg.report_type, template_name, Arg.metadataFilter)
    else:
        unique_id = generate_report(get_access_token(), None, None, Arg.start_timestamp, Arg.end_timestamp, Arg.format, Arg.report_type, None, Arg.metadataFilter)

    print("Unique Id to report generation is " + unique_id)
    time.sleep(3)
    status = get_report_status(get_access_token(), unique_id)
    print("Status of the Report generation process: " + unique_id)
    if status == REPORT_GENERATION_STATUS_INPROGRESS:
        while status == REPORT_GENERATION_STATUS_INPROGRESS:
            status = get_report_status(get_access_token(), unique_id)
            print("Status of the Report generation process: " + status)
            time.sleep(REPORT_GENERATION_STATUS_CHECK_INTERVAL)

    if status == REPORT_GENERATION_STATUS_SUCCESS:
        file_name = download_report_file(get_access_token(), unique_id)
        print_info("Report generated successfully. Report file available at location :" + os.path.abspath(file_name))
    elif status == REPORT_GENERATION_STATUS_NO_DATA_FOUND:
        print("No data found for provided criteria for report generation.")
    else:
        print("Report generation failed at Orchestrator.")


def main():
	execute()
	print("Please refer log file '" + log_file + "' for more details.")


#---START-------------------------------------------------------------------------------------------------------------
main()	
