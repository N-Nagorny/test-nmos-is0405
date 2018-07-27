# Riedel NMOS Test Tool

This tool creates a simple web service to test against the JTNM February 2018 "Dirty Hands" NMOS checklist.

Currently NMOS-IS-04-01 (Basic) and NMOS-IS-05-01 (Basic) tests are integrated.

**Attention:**
The NMOS-IS-04-01 test only works if the target node is in registered mode. The registration service endpoint has to be specified on program startup (see section "Usage"). For testing purposes a reference implementation of the RDS is provided by the BBC (https://github.com/bbc/nmos-discovery-registration-ri).

## Usage:
Required command line parameters:

--query_ip: the ip of the query service on which the node is currently registered (RDS) 

--query_port: the port of the query service on which the node is currently registered (RDS) 

e.g. python nmos-test.py --query_ip=172.56.123.5 --query_port=4480

Supported command line parameters:

--test_number: a number of desired specific test. If it is not presented all tests will be performed

e.g. python nmos-test.py --query_ip=172.56.123.5 --query_port=4480 --test_number=09

This tool provides a simple web service which is available on http://localhost:5000.
Provide the NodeUrl (see the detailed description on the webpage) and select a checklist.
The result of the the test will be shown after a couple seconds.

Tested with Firefox 58 and Chrome 63.

### TestRail support (testing mode)
This branch contains version that have TestRail support. Now it works as follows:

1. You should open config.ini and fill it with your credentials, desired test plan and test suite IDs and also desired test run name.

2. Also there are sections with test cases IDs corresponding to test cases of Riedel.

3. After launch script creates new test run in specified test plan and fills it with test cases used in selected test.

##  External dependencies:
- Python3

Python packages:
- flask 
- wtforms
- jsonschema
- zeroconf
- requests

