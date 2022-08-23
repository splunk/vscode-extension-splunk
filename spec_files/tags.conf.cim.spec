# Version 9.0
#
# This file contains possible attribute/value pairs for configuring tags for
# the Common Information Model. 
# https://docs.splunk.com/Documentation/CIM/latest
#

###################
# Alerts data model
###################
alert = <enabled|disabled>
* Enable or disable CIM tagging for the Alerts data model.
* Events in the Alerts data model are vendor agnostic, which means that they are not specific to a vendor.
  The events in the Alerts data model are higher level event constructs or metadata events that carry new 
  knowledge based on multiple basic events. However, an event that pertains to multiple lower basic level 
  is not always mapped to the Alerts data model.

###########################
# Authentication data model
###########################
authentication = <enabled|disabled>
* Enable or disable CIM tagging for the Authentication data model.
* The fields and tags in the Authentication data model describe login activities from any data source.

# default is reused in other constraints (see below)
# default = <enabled|disabled>
# * Enable or disable CIM tagging for the Default_Authentication constraint in the Authentication data model.

cleartext = <enabled|disabled>
* Enable or disable CIM tagging for the Insecure_Authentication constraint in the Authentication data model.

insecure = <enabled|disabled>
* Enable or disable CIM tagging for the Insecure_Authentication constraint in the Authentication data model.

privileged = <enabled|disabled>
* Enable or disable CIM tagging for the Privileged_Authentication constraint in the Authentication data model.

#########################
# Certificates data model
#########################
certificate = <enabled|disabled>
* Enable or disable CIM tagging for the Certificates data model.
* The fields and tags in the Certificates data model describe key and certificate management events from a variety of secure servers and IAM systems.

ssl = <enabled|disabled>
* Enable or disable CIM tagging for the SSL constraint in the Certificates data model.

tls = <enabled|disabled>
* Enable or disable CIM tagging for the SSL constraint in the Certificates data model.

###################
# Change data model
###################
# change is reused in other constraints (see below)
# change = <enabled|disabled>
# * Enable or disable CIM tagging for the Change data model.
# * The fields in the Change data model describe Create, Read, Update, and Delete activities from any data source.

audit = <enabled|disabled>
* Enable or disable CIM tagging for the Auditing_Changes constraint in the Change data model.

# endpoint is reused in other constraints (see below)
# endpoint = <enabled|disabled>

# network is reused in other constraints (see below)
# network = <enabled|disabled>
# * Enable or disable CIM tagging for the Network_Changes constraint in the Change data model.

account = <enabled|disabled>
* Enable or disable CIM tagging for the Account_Management constraint in the Change data model.

# instance is reused in other constraints (see below)
# instance = <enabled|disabled>

########################
# Data Access data model
########################
data = <enabled|disabled>
* Enable or disable CIM tagging for the Data Access data model.
* The Data Access data model is for monitoring shared data access user activity. It helps you 
  detect a user's unauthorized data access, misuse, exfiltration, and more. It applies to 
  events about users accessing data on servers that are shared by many other users, such as: 
  The "file abc" on the "server xyz" was accessed (read, created, modified, shared, and so on) 
  by a "user Bob".

access = <enabled|disabled>
* Enable or disable CIM tagging for the Data Access data model.
* The Data Access data model is for monitoring shared data access user activity. It helps you 
  detect a user's unauthorized data access, misuse, exfiltration, and more. It applies to 
  events about users accessing data on servers that are shared by many other users, such as: 
  The "file abc" on the "server xyz" was accessed (read, created, modified, shared, and so on) 
  by a "user Bob".

######################
# Databases data model
######################
database = <enabled|disabled>
* Enable or disable CIM tagging for the Databases data model.
* The fields and tags in the Databases data model describe events that pertain to structured and semi-structured data storage.

# instance is reused in other constraints (see below)
# instance = <enabled|disabled>

# instance is reused in other constraints (see below)
# stats = <enabled|disabled>

# session is reused in other constraints (see below)
# session = <enabled|disabled>
# * Enable or disable CIM tagging for the Session_Info constraint in the Databases data model.

lock = <enabled|disabled>
* Enable or disable CIM tagging for the Lock_Info constraint in the Databases data model.

query = <enabled|disabled>
* Enable or disable CIM tagging for the Database_Query constraint in the Databases data model.

tablespace = <enabled|disabled>
* Enable or disable CIM tagging for the Tablespace constraint in the Databases data model.

# instance is reused in other constraints (see below)
# stats = <enabled|disabled>

#################################
# Data Loss Prevention data model
#################################
dlp = <enabled|disabled>
* Enable or disable CIM tagging for the Data Loss Prevention data model.
* The fields in the Data Loss Prevention (DLP) data model describe events gathered from DLP tools used to identify, monitor and protect data.

# incident is reused in other constraints (see below)
# incident = <enabled|disabled>
# * Enable or disable CIM tagging for the Data Loss Prevention data model.
# * The fields in the Data Loss Prevention (DLP) data model describe events gathered from DLP tools used to identify, monitor and protect data.

##################
# Email data model
##################
email = <enabled|disabled>
* Enable or disable CIM tagging for the Email data model.
* The fields and tags in the Email data model describe email traffic, whether server:server or client:server.

delivery = <enabled|disabled>
* Enable or disable CIM tagging for the Delivery constraint in the Email data model.

content = <enabled|disabled>
* Enable or disable CIM tagging for the Content constraint in the Email data model.

filter = <enabled|disabled>
* Enable or disable CIM tagging for the Filtering constraint in the Email data model.

#####################
# Endpoint data model
#####################
listening = <enabled|disabled>
* Enable or disable CIM tagging for the Ports constraint in the Endpoint data model.

port = <enabled|disabled>
* Enable or disable CIM tagging for the Ports constraint in the Endpoint data model.

process = <enabled|disabled>
* Enable or disable CIM tagging for the Processes constraint in the Endpoint data model.

# report is reused in other constraints (see below)
# report = <enabled|disabled>

service = <enabled|disabled>
* Enable or disable CIM tagging for the Services constraint in the Endpoint data model.

# endpoint is reused in other constraints (see below)
# endpoint = <enabled|disabled>

filesystem = <enabled|disabled>
* Enable or disable CIM tagging for the Filesystem constraint in the Endpoint data model.

registry = <enabled|disabled>
* Enable or disable CIM tagging for the Registry constraint in the Endpoint data model.

#############################
# Event Signatures data model
#############################
track_event_signatures = <enabled|disabled>
* Enable or disable CIM tagging for the Event Signatures data model.
* Event Signatures is a standard location to store Windows EventID. 
  This data model is searchable as DataModel.DataSet. It is not accelerated 
  by default, but the appropriate acceleration settings have been defined.

###################################
# Interprocess Messaging data model
###################################
messaging = <enabled|disabled>
* Enable or disable CIM tagging for the Interprocess Messaging data model.
* The fields in the Interprocess Messaging data model describe transactional 
  requests in programmatic interfaces. This enables you to establish the data 
  requirements for a domain and create apps that support each other.

################################
# Intrusion Detection data model
################################
ids = <enabled|disabled>
* Enable or disable CIM tagging for the Intrusion Detection data model.
* The fields in the Intrusion Detection data model describe attack detection 
  events gathered by network monitoring devices and apps.

# attack is reused in other constraints (see below)
# attack = <enabled|disabled>
# * Enable or disable CIM tagging for the Intrusion Detection data model.
# * The fields in the Intrusion Detection data model describe attack detection 
#   events gathered by network monitoring devices and apps.

######################
# Inventory data model
######################
inventory = <enabled|disabled>
* Enable or disable CIM tagging for the Inventory data model.
* The fields and tags in the Inventory data model describe common computer 
  infrastructure components from any data source, along with network infrastructure inventory and topology.

# cpu is reused in other constraints (see below)
# cpu = <enabled|disabled>
# * Enable or disable CIM tagging for the CPU constraint in the Inventory data model.

# memory is reused in other constraints (see below)
# memory = <enabled|disabled>
# * Enable or disable CIM tagging for the Memory constraint in the Inventory data model.

# network is reused in other constraints (see below)
# network = <enabled|disabled>
# * Enable or disable CIM tagging for the Network constraint in the Inventory data model.

# storage is reused in other constraints (see below)
# storage = <enabled|disabled>
# * Enable or disable CIM tagging for the Storage constraint in the Inventory data model.

system = <enabled|disabled>
* Enable or disable CIM tagging for the OS constraint in the Inventory data model.

version = <enabled|disabled>
* Enable or disable CIM tagging for the OS constraint in the Inventory data model.

user = <enabled|disabled>
* Enable or disable CIM tagging for the User constraint in the Inventory data model.

password=* = <enabled|disabled>
* Enable or disable CIM tagging for the Cleartext_Passwords constraint in the Inventory data model.

# default is reused in other constraints (see below)
# default = <enabled|disabled>
# * Enable or disable CIM tagging for the Default_Accounts constraint in the Inventory data model.

virtual = <enabled|disabled>
* Enable or disable CIM tagging for the Virtual_OS constraint in the Inventory data model.

snapshot = <enabled|disabled>
* Enable or disable CIM tagging for the Snapshot constraint in the Inventory data model.

tools = <enabled|disabled>
* Enable or disable CIM tagging for the Tools constraint in the Inventory data model.

################
# JVM data model
################
jvm = <enabled|disabled>
* Enable or disable CIM tagging for the JVM data model.
* The fields in the JVM data model describe generic Java server platforms.

threading = <enabled|disabled>
* Enable or disable CIM tagging for the Threading constraint in the JVM data model.

runtime = <enabled|disabled>
* Enable or disable CIM tagging for the Runtime constraint in the JVM data model.

# os is reused in other constraints (see below)
# os = <enabled|disabled>
# * Enable or disable CIM tagging for the OS constraint in the JVM data model.

compilation = <enabled|disabled>
* Enable or disable CIM tagging for the Compilation constraint in the JVM data model.

classloading = <enabled|disabled>
* Enable or disable CIM tagging for the Classloading constraint in the JVM data model.

# memory is reused in other constraints (see below)
# memory = <enabled|disabled>
# * Enable or disable CIM tagging for the Threading constraint in the JVM data model.

####################
# Malware data model
####################
malware = <enabled|disabled>
* Enable or disable CIM tagging for the Malware data model.
* The fields in the Malware data model describe malware detection 
  and endpoint protection management activity. The Malware data 
  model is often used for endpoint antivirus product related events.

# attack is reused in other constraints (see below)
# attack = <enabled|disabled>
# * Enable or disable CIM tagging for the Malware data model.

operations = <enabled|disabled>
* Enable or disable CIM tagging for the Malware_Operations constraint in the Malware data model.

################
# DNS data model
################
dns = <enabled|disabled>
* Enable or disable CIM tagging for the DNS data model.
* The fields and tags in the Network Resolution (DNS) data model describe DNS traffic, both server:server and client:server.

# network is reused in other constraints (see below)
# network = <enabled|disabled>

resolution = <enabled|disabled>
* Enable or disable CIM tagging for the DNS data model.

#############################
# Network Sessions data model
#############################
start = <enabled|disabled>
* Enable or disable CIM tagging for the Session_Start constraint in the Network Sessions data model.

end = <enabled|disabled>
* Enable or disable CIM tagging for the Session_End constraint in the Network Sessions data model.

dhcp = <enabled|disabled>
* Enable or disable CIM tagging for the DHCP constraint in the Network Sessions data model.

vpn = <enabled|disabled>
* Enable or disable CIM tagging for the VPN constraint in the Network Sessions data model.

############################
# Network Traffic data model
############################
communicate = <enabled|disabled>
* Enable or disable CIM tagging for the Network Traffic data model.
* The fields and tags in the Network Traffic data model describe flows of data across network infrastructure components.

########################
# Performance data model
########################
performance = <enabled|disabled>
* Enable or disable CIM tagging for the Performance data model.
* The fields in the Performance data model describe performance tracking data.

facilities = <enabled|disabled>
* Enable or disable CIM tagging for the Facilities constraint in the Performance data model.

uptime = <enabled|disabled>
* Enable or disable CIM tagging for the Uptime constraint in the Performance data model.

time = <enabled|disabled>
* Enable or disable CIM tagging for the Timesync constraint in the Performance data model.

synchronize = <enabled|disabled>
* Enable or disable CIM tagging for the Timesync constraint in the Performance data model.

##############################
# Splunk Audit Logs data model
##############################
modaction = <enabled|disabled>
* Enable or disable CIM tagging for the Modular Alerts Actions dataset in the Splunk Audit Logs data model.
* The fields in the Splunk Audit Logs data model describe audit information for systems producing event logs.

invocation = <enabled|disabled>
* Enable or disable CIM tagging for the Modular Action Invocations dataset in the Splunk Audit Logs data model.
* The fields in the Splunk Audit Logs data model describe audit information for systems producing event logs.

##############################
# Ticket Management data model
##############################
ticketing = <enabled|disabled>
* Enable or disable CIM tagging for the Ticket Management data model.
* The fields and tags in the Ticket Management data model describe service requests and their states in
  ITIL-influenced service desks, bug trackers, simple ticket systems, or GRC systems.

problem = <enabled|disabled>
* Enable or disable CIM tagging for the Problem constraint in the Ticket Management data model.

####################
# Updates data model
####################
update = <enabled|disabled>
* Enable or disable CIM tagging for the Updates data model.
* The fields in the Updates data model describe patch management events from individual
  systems or central management tools.

status = <enabled|disabled>
* Enable or disable CIM tagging for the Status constraint in the Updates data model.

error = <enabled|disabled>
* Enable or disable CIM tagging for the Error constraint in the Updates data model.

############################
# Vulnerabilities data model
############################
vulnerability = <enabled|disabled>
* Enable or disable CIM tagging for the Vulnerabilities data model.
* The fields in the Vulnerabilities data model describe vulnerability detection data.

################
# Web data model
################
web = <enabled|disabled>
* Enable or disable CIM tagging for the Web data model.
* The fields in the Web data model describe web server and/or proxy server data 
  in a security or operational context.

proxy = <enabled|disabled>
* Enable or disable CIM tagging for the Proxy constraint in the Web data model.

#########################################
# Constraint tags used in multiple models
#########################################

# attack is used in the following data models:
# Data Loss Prevention, Malware
attack = <enabled|disabled>
* Enable or disable CIM tagging for the Attack constraint in a data model.

# change is used in the following data models:
# Change, Ticket Management
change = <enabled|disabled>
* Enable or disable CIM tagging for the Change constraint in a data model.

# cpu is used in the following data models
# Inventory, Performance
cpu = <enabled|disabled>
* Enable or disable CIM tagging for the CPU constraint in a data model.

# default is used in the following data models:
# Authentication, Inventory
default = <enabled|disabled>
* Enable or disable CIM tagging for the default constraint in a data model.

# incident is used in the following data models:
# Data Loss Prevention, Ticket Management
incident = <enabled|disabled>
* Enable or disable CIM tagging for the Incident constraint in a data model.

# instance is used in the following data models:
# Change, Databases
instance = <enabled|disabled>
* Enable or disable CIM tagging for the Instance constraint in a data model.

# network is used in the following data models:
# Change, Inventory, DNS, Network Sessions
network = <enabled|disabled>
* Enable or disable CIM tagging for the Network constraint in a data model.

# endpoint is used in the following data models:
# Change, Endpoint Filesystem
endpoint = <enabled|disabled>
* Enable or disable CIM tagging for the Endpoint constraint in a data model.

# memory is used in the following data models:
# Inventory, JVM, Performance
memory = <enabled|disabled>
* Enable or disable CIM tagging for the Memory constraint in a data model.

# os is used in the following data models:
# JVM, Performance 
os = <enabled|disabled>
* Enable or disable CIM tagging for the OS constraint in a data model.

# stats is used in the following data models:
# Databases Instance_Stats, Databases Query_Stats
stats = <enabled|disabled>
* Enable or disable CIM tagging for the Stats constraint in a data model.

# report is used in the following data models:
# Endpoint Processes, Endpoint Services
report = <enabled|disabled>
* Enable or disable CIM tagging for the Report constraint in a data model.

# session is used in the following data models:
# Databases, Network Sessions
session = <enabled|disabled>
* Enable or disable CIM tagging for the Session constraint in a data model.

# storage is used in the following data models
storage = <enabled|disabled>
* Enable or disable CIM tagging for the Storage constraint in a data model.