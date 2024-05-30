reportGenerator.py
----------------
reportGenerator.py can be used to start report generation process at orchestrator and download the report after succssful completion.
===============================================================================================


Prerequisites:
---------------
1. Python 3 is installed
2. Python requests module installed
3. commonConfig.cnf is configured. You can locate commonConfig.cnf file at ORCH_HOME/scripts/ORCH_VERSION/python/common/ directory or same directory where  reportGenerator.py file located.
4. Added IP host mapping for orchestrator in /etc/hosts file.
5. The user should have root/sudo permissions
===============================================================================================


Usage:
---------------
usage: reportGenerator.py [-h] [--username USERNAME] [--password PASSWORD] [--fromdate FROMDATE] [--todate TODATE] [--domain DOMAIN] [--subdomain SUBDOMAIN] [--format FORMAT] [--reportType REPORTTYPE]

Start report generation at Orchestrator and download report after successful generation

optional arguments:
  -h, --help            show this help message and exit
  --username USERNAME   (Optional) Orchestrator user username
  --password PASSWORD   (Optional) Orchestrator user password
  --fromdate FROMDATE   (Mandatory) Filter out records from the date. The expected Date format is 'yyyy-mm-dd HH:MM:SS'.
  --todate TODATE       (Optional) Filter out records to date. The expected Date format is 'yyyy-mm-dd HH:MM:SS'.
  --domain DOMAIN       (Mandatory) Filter out records with the domain name
  --subdomain SUBDOMAIN
                        (Mandatory) Filter out records with the subdomain name
  --format FORMAT       (Optional) Set report format CSV or PDF. This option is applicable only for vulnerabilities_stride type reports. The default is CSV.
  --reportType REPORTTYPE
                        (Mandatory) Set required report type value from application_details, application_forensic, secure_application_policy_details, attacked_applications_details, discovered_application_details, owasp_top_10_report, vulnerabilities_stride_short, vulnerabilities_stride_long, application_forensic_session_details, pcre_policy_details, application_model, application_model_default, application_model_threat_dragon, application_model_threat_dragon_plus, application_model_microsoft_tmt, application_model_architecture, application_model_architecture_and_threat, application_version_information, version_information_master.,
  --templateName TEMPLATENAME  (Optional) Set the TD template name to integrate the Threat Dragon model with the provided template. Applicable only with reportType application_model_threat_dragon and application_model_threat_dragon_plus.
  --metadataFilter METADATAFILTER   (Optional) Set the comma seperated metadata attribute key and value pairs to filter out processes. Example srnumber:4582,srName:sampleService

Start report generation at Orchestrator and download report after successful generation
 
===============================================================================================


Examples:
---------------
python3 reportGenerator.py --fromdate '2023-08-01 00:00:01' --domain ACME --subdomain Sales --reportType vulnerabilities_stride_short --format pdf

python3 reportGenerator.py --fromdate '2023-08-01 00:00:01' --domain ACME --subdomain Sales --reportType application_model_architecture

python3 reportGenerator.py --fromdate '2023-08-01 00:00:01' --domain ACME --subdomain Sales --reportType application_model_threat_dragon --templateName template_TBB_212

python3 reportGenerator.py --fromdate '2023-08-01 00:00:01' --domain ACME --subdomain Sales --reportType application_model_threat_dragon --templateName template_TBB_212 --metadataFilter 'srNumber:13258,srName:metaservice'