# Copyright (C) 2018 Riedel Communications GmbH & Co. KG
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import Flask, render_template, flash, request
from wtforms import Form, validators, StringField, SelectField, IntegerField
from testrail import *

import argparse
import configparser

import IS0401Test
import IS0501Test

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'nmos-interop-testing-jtnm'

NODE_URL = "http://<node_ip>:<node_port>/x-nmos/node/v1.2/"


class DataForm(Form):
    test = SelectField(label="Select test:", choices=[("IS-04-01", "IS-04-01: Node API"), ("IS-05-01", "IS-05-01: ConnectionMgmt API")])
    ip = StringField(label="Ip:", validators=[validators.IPAddress(message="Please enter a valid IPv4 address.")])
    port = IntegerField(label="Port:", validators=[validators.NumberRange(min=0, max=65535,
                                                                          message="Please enter a valid port number (0-65535).")])
    version = SelectField(label="API Version:", choices=[("v1.0", "v1.0"),
                                                        ("v1.1", "v1.1"),
                                                        ("v1.2", "v1.2")])


def send_result_to_test_rail(test, result):
    config = configparser.ConfigParser()
    config.read('config.ini')

    test_rail = APIClient(config['Credentials']['TestRailUrl'])
    test_rail.user = config['Credentials']['UserEmail']
    test_rail.password = config['Credentials']['ApiKey']

    if test == "IS-04-01":
        test_cases_map = 'Is04TestCasesMap'
    else:
        test_cases_map = 'Is05TestCasesMap'

    test_run = test_rail.send_post(
      'add_plan_entry' + '/' + config['TestRunDetails']['TestPlanId'],
      {
        'suite_id': config['TestRunDetails']['TestSuiteId'],
        'name': config['TestRunDetails']['TestRunName'],
        'include_all': False,
        'case_ids': list(dict(config.items(test_cases_map)).values())
      }
    )

    test_run_id = test_run['runs'][0]['id']
    test_run = test_rail.send_get('get_tests' + '/' + str(test_run_id))

    auto_results = list(filter(lambda i: i[2] != 'Manual', result))

    tr_results = []
    for test in test_run:
        for key, value in config.items(test_cases_map):
            if value == str(test['case_id']) and str(key) in [i[0] for i in auto_results]:
                for result in auto_results:
                    if key == result[0]:
                        tr_results.append([test['id'], 1 if result[2] == 'Pass' else 8, result[3]])

    for cur_result in tr_results:
        test_rail.send_post(
          'add_result' + '/' + str(cur_result[0]),
          {
            'status_id': cur_result[1],
            'comment': cur_result[2]
          }
        )
    return


@app.route('/', methods=["GET", "POST"])
def index_page():
    form = DataForm(request.form)
    if request.method == "POST":
        test = request.form["test"]
        ip = request.form["ip"]
        port = request.form["port"]
        version = request.form["version"]
        if form.validate():
            if test == "IS-04-01":
                url = "http://{}:{}/x-nmos/node/{}/".format(ip, str(port), version)
                test_obj = IS0401Test.IS0401Test(url, QUERY_URL)
            else:  # test == "IS-05-01"
                url = "http://{}:{}/x-nmos/connection/{}/".format(ip, str(port), version)
                test_obj = IS0501Test.IS0501Test(url)
            if args.test_number == None:
                result = test_obj.run_tests()
            else:
                result = test_obj.run_test(args.test_number)
            send_result_to_test_rail(test=test, result=result)
            return render_template("result.html", url=url, test=test, result=result)
        else:
            flash("Error: {}".format(form.errors))

    return render_template("index.html", form=form)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Riedel NMOS Interop Test Tool")
    parser.add_argument("--query_ip", help="String. IPv4 address of the query service (RDS).", required=True)
    parser.add_argument("--query_port", help="Integer. Port of the query service (RDS).", required=True)
    parser.add_argument("--test_number", help="Integer. A number of desired specific test.", required=False)
    args = parser.parse_args()
    QUERY_URL = "http://{}:{}/x-nmos/query".format(args.query_ip, args.query_port)
    app.run(host='0.0.0.0')
