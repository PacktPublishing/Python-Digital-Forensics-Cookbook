from __future__ import print_function
import argparse
from collections import Counter
import shutil
import os
import sys

"""
MIT License

Copyright (c) 2017 Chapin Bryce, Preston Miller

Please share comments and questions at:
    https://github.com/PythonForensics/PythonForensicsCookbook
    or email pyforcookbook@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__authors__ = ["Chapin Bryce", "Preston Miller"]
__date__ = 20170815
__description__ = "Generates dashboard of sample acquisition information"

try:
    from jinja2 import Template
except ImportError:
    print("[-] Install required third-party module jinja2")
    sys.exit(1)


DASH = Template("""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <link rel="icon" type="image/png" href="assets/img/favicon.ico">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />

    <title>Light Bootstrap Dashboard</title>

    <meta content='width=device-width, initial-scale=1.0,
      maximum-scale=1.0, user-scalable=0' name='viewport' />
    <meta name="viewport" content="width=device-width" />


    <!-- Bootstrap core CSS     -->
    <link href="assets/css/bootstrap.min.css" rel="stylesheet" />

    <!-- Animation library for notifications   -->
    <link href="assets/css/animate.min.css" rel="stylesheet"/>

    <!--  Light Bootstrap Table core CSS    -->
    <link href="assets/css/light-bootstrap-dashboard.css" rel="stylesheet"/>


    <!--  CSS for Demo Purpose, don't include it in your project     -->
    <link href="assets/css/demo.css" rel="stylesheet" />


    <!--     Fonts and icons     -->
    <link href="
      http://maxcdn.bootstrapcdn.com/font-awesome/4.2.0/css/
      font-awesome.min.css" rel="stylesheet">
    <link href='http://fonts.googleapis.com/css?family=Roboto:400,700,300'
      rel='stylesheet' type='text/css'>
    <link href="assets/css/pe-icon-7-stroke.css" rel="stylesheet" />

</head>
<body>

<div class="wrapper">
    <div class="sidebar" data-color="purple"
      data-image="assets/img/sidebar-5.jpg">

    <!--
        Tip 1: you can change the color of the sidebar using:
          data-color="blue | azure | green | orange | red | purple"
        Tip 2: you can also add an image using data-image tag
    -->

        <div class="sidebar-wrapper">
            <div class="logo">
            </div>

            <ul class="nav">
                <li class="active">
                    <a href="dashboard.html">
                        <i class="pe-7s-graph"></i>
                        <p>Dashboard</p>
                    </a>
                </li>
                <li>
                    <a href="table.html">
                        <i class="pe-7s-note2"></i>
                        <p>Table List</p>
                    </a>
                </li>
            </ul>
        </div>
    </div>

    <div class="main-panel">
        <nav class="navbar navbar-default navbar-fixed">
            <div class="container-fluid">
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle"
                      data-toggle="collapse"
                      data-target="#navigation-example-2">
                        <span class="sr-only">Toggle navigation</span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </button>
                    <a class="navbar-brand" href="#">Dashboard Example</a>
                </div>
            </div>
        </nav>


        <div class="content">
            <div class="container-fluid">
                <div class="row">
                <div class="col-md-4">
                <h4>Custodians: <b>{{num_custodians}}</b></h4>
                </div>
                <div class="col-md-4">
                <h4>Devices Preserved: <b>{{num_devices}}</b></h4>
                </div>
                <div class="col-md-4">
                <h4>Total Data Preserved: <b>{{data}}</b></h4>
                </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="header">
                                <h4 class="title">Acquired Device Types</h4>
                                <p class="category">Breakdown of Device
                                  Type</p>
                            </div>
                            <div class="content">
                                <div id="chartPreferences"
                                  class="ct-chart ct-perfect-fourth"></div>

                                <div class="footer">
                                </div>
                            </div>
                        </div>
                    </div>

                <div class="col-md-6">
                    <div class="card">
                        <div class="header">
                            <h4 class="title">Custodian Devices</h4>
                            <p class="category">Breakdown of Devices per
                              Custodian</p>
                        </div>
                        <div class="content">
                            <div id="chartPreferences2" class="ct-chart"></div>

                            <div class="footer">
                            </div>
                        </div>
                    </div>
                </div>
            </div>


                <div class="row">
                    <div class="col-md-12">
                        <div class="card ">
                            <div class="header">
                                <h4 class="title">Preserved Data per
                                  Day</h4>
                                <p class="category">Acquired Data per
                                  Acquistion Date</p>
                            </div>
                            <div class="content">
                                <div id="chartActivity" class="ct-chart">
                                </div>

                                <div class="footer">
                                    <div class="legend">
                                        <i class="fa fa-circle
                                        text-info"></i> Size (GB)
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
    </div>

                                <div class="footer">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>


</body>

    <!--   Core JS Files   -->
    <script src="assets/js/jquery-1.10.2.js" type="text/javascript">
    </script>
    <script src="assets/js/bootstrap.min.js" type="text/javascript">
    </script>

    <!--  Checkbox, Radio & Switch Plugins -->
    <script src="assets/js/bootstrap-checkbox-radio-switch.js"></script>

    <!--  Charts Plugin -->
    <script src="assets/js/chartist.min.js"></script>

    <!--  Notifications Plugin    -->
    <script src="assets/js/bootstrap-notify.js"></script>

    <!--  Google Maps Plugin    -->
    <script type="text/javascript"
    src="https://maps.googleapis.com/maps/api/js?sensor=false"></script>

    <!-- Light Bootstrap Table Core javascript and methods for
      Demo purpose -->
    <script src="assets/js/light-bootstrap-dashboard.js"></script>

    <!-- Light Bootstrap Table DEMO methods, don't include it in
      your project! -->
    <script src="assets/js/demo.js"></script>

    <script type="text/javascript">
        $(document).ready(function(){

            demo.initChartist();

        });
    </script>

</html>
""")

TABLE = Template("""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <link rel="icon" type="image/png" href="assets/img/favicon.ico">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />

    <title>Light Bootstrap Dashboard</title>

    <meta content='width=device-width, initial-scale=1.0,
      maximum-scale=1.0, user-scalable=0' name='viewport' />
    <meta name="viewport" content="width=device-width" />


    <!-- Bootstrap core CSS     -->
    <link href="assets/css/bootstrap.min.css" rel="stylesheet" />

    <!-- Animation library for notifications   -->
    <link href="assets/css/animate.min.css" rel="stylesheet"/>

    <!--  Light Bootstrap Table core CSS    -->
    <link href="assets/css/light-bootstrap-dashboard.css" rel="stylesheet"/>


    <!--  CSS for Demo Purpose, don't include it in your project     -->
    <link href="assets/css/demo.css" rel="stylesheet" />


    <!--     Fonts and icons     -->
    <link href="http://maxcdn.bootstrapcdn.com/font-awesome/4.2.0/css/
      font-awesome.min.css" rel="stylesheet">
    <link href='http://fonts.googleapis.com/css?family=Roboto:400,700,300'
      rel='stylesheet' type='text/css'>
    <link href="assets/css/pe-icon-7-stroke.css" rel="stylesheet" />
</head>
<body>

<div class="wrapper">
    <div class="sidebar" data-color="purple"
      data-image="assets/img/sidebar-5.jpg">
        <div class="sidebar-wrapper">
            <div class="logo">
            </div>
            <ul class="nav">
                <li>
                    <a href="dashboard.html">
                        <i class="pe-7s-graph"></i>
                        <p>Dashboard</p>
                    </a>
                </li>
                <li class="active">
                    <a href="table.html">
                        <i class="pe-7s-note2"></i>
                        <p>Table List</p>
                    </a>
                </li>
            </ul>
        </div>
    </div>
    <div class="main-panel">
    <nav class="navbar navbar-default navbar-fixed">
            <div class="container-fluid">
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle"
                      data-toggle="collapse"
                      data-target="#navigation-example-2">
                        <span class="sr-only">Toggle navigation</span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </button>
                    <a class="navbar-brand" href="#">Table List</a>
                </div>
            </div>
        </nav>
        <div class="content">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-md-12">
                        <div class="card">
                            <div class="header">
                                <h4 class="title">Evidence Information</h4>
                                <p class="category">Preserved Data
                                  Details</p>
                            </div>
                            <div class="content table-responsive
                              table-full-width">
                                <table class="table table-hover
                                  table-striped">
                                    <thead>
                                      <th>ID</th>
                                        <th>Description</th>
                                        <th>Type of Device</th>
    <th>Acquisition Date</th>
                                        <th>Size (GB)</th>
                                    </thead>
                                    <tbody>
                                        {{ table_body }}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>


</body>

    <!--   Core JS Files   -->
    <script src="assets/js/jquery-1.10.2.js" type="text/javascript">
    </script>
    <script src="assets/js/bootstrap.min.js" type="text/javascript">
    </script>

    <!--  Checkbox, Radio & Switch Plugins -->
    <script src="assets/js/bootstrap-checkbox-radio-switch.js"></script>

    <!--  Charts Plugin -->
    <script src="assets/js/chartist.min.js"></script>

    <!--  Notifications Plugin    -->
    <script src="assets/js/bootstrap-notify.js"></script>

    <!--  Google Maps Plugin    -->
    <script type="text/javascript"
    src="https://maps.googleapis.com/maps/api/js?sensor=false"></script>

    <!-- Light Bootstrap Table Core javascript and methods for
      Demo purpose -->
    <script src="assets/js/light-bootstrap-dashboard.js"></script>

    <!-- Light Bootstrap Table DEMO methods, don't include
      it in your project! -->
    <script src="assets/js/demo.js"></script>


</html>
""")

DEMO = Template("""type = ['','info','success','warning','danger'];


demo = {
    initPickColor: function(){
        $('.pick-class-label').click(function(){
            var new_class = $(this).attr('new-class');
            var old_class = $('#display-buttons').attr('data-class');
            var display_div = $('#display-buttons');
            if(display_div.length) {
            var display_buttons = display_div.find('.btn');
            display_buttons.removeClass(old_class);
            display_buttons.addClass(new_class);
            display_div.attr('data-class', new_class);
            }
        });
    },

    initChartist: function(){

        var data = {
          labels: [{{bar_labels}}],
          series: [[{{bar_series}}]]
        };

        var options = {
            seriesBarDistance: 10,
            axisX: {
                showGrid: false
            },
            height: "245px"
        };

        var responsiveOptions = [
          ['screen and (max-width: 640px)', {
            seriesBarDistance: 5,
            axisX: {
              labelInterpolationFnc: function (value) {
                return value[0];
              }
            }
          }]
        ];

        Chartist.Bar('#chartActivity', data, options, responsiveOptions);

        var dataPreferences = {
            series: [
                [25, 30, 20, 25]
            ]
        };

        var optionsPreferences = {
            donut: true,
            donutWidth: 40,
            startAngle: 0,
            total: 100,
            showLabel: false,
            axisX: {
                showGrid: false
            }
        };

        Chartist.Pie('#chartPreferences', dataPreferences,
          optionsPreferences);

        Chartist.Pie('#chartPreferences', {
          labels: [{{pi_labels}}],
          series: [{{pi_series}}]
        });

        Chartist.Pie('#chartPreferences2', dataPreferences,
          optionsPreferences);

        Chartist.Pie('#chartPreferences2', {
          labels: [{{pi_2_labels}}],
          series: [{{pi_2_series}}]
        });
    }

}
""")


def main(output_dir):
    acquisition_data = [
        ["001", "Debbie Downer", "Mobile", "08/05/2017 13:05:21", "32"],
        ["002", "Debbie Downer", "Mobile", "08/05/2017 13:11:24", "16"],
        ["003", "Debbie Downer", "External", "08/05/2017 13:34:16", "128"],
        ["004", "Debbie Downer", "Computer", "08/05/2017 14:23:43", "320"],
        ["005", "Debbie Downer", "Mobile", "08/05/2017 15:35:01", "16"],
        ["006", "Debbie Downer", "External", "08/05/2017 15:54:54", "8"],
        ["007", "Even Steven", "Computer", "08/07/2017 10:11:32", "256"],
        ["008", "Even Steven", "Mobile", "08/07/2017 10:40:32", "32"],
        ["009", "Debbie Downer", "External", "08/10/2017 12:03:42", "64"],
        ["010", "Debbie Downer", "External", "08/10/2017 12:43:27", "64"]
    ]

    print("[+] Processing acquisition data")
    process_data(acquisition_data, output_dir)


def process_data(data, output_dir):
    html_table = ""
    for acq in data:
        html_table += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td>" \
            "<td>{}</td></tr>\n".format(
                acq[0], acq[1], acq[2], acq[3], acq[4])

    device_types = Counter([x[2] for x in data])
    custodian_devices = Counter([x[1] for x in data])

    date_dict = {}
    for acq in data:
        date = acq[3].split(" ")[0]
        if date in date_dict:
            date_dict[date] += int(acq[4])
        else:
            date_dict[date] = int(acq[4])
    output_html(output_dir, len(data), html_table,
                device_types, custodian_devices, date_dict)


def output_html(output, num_devices, table, devices, custodians, dates):
    print("[+] Rendering HTML and copy files to {}".format(output))
    cwd = os.getcwd()
    bootstrap = os.path.join(cwd, "light-bootstrap-dashboard")
    shutil.copytree(bootstrap, output)

    dashboard_output = os.path.join(output, "dashboard.html")
    table_output = os.path.join(output, "table.html")
    demo_output = os.path.join(output, "assets", "js", "demo.js")

    with open(dashboard_output, "w") as outfile:
        outfile.write(DASH.render(num_custodians=len(custodians.keys()),
                                  num_devices=num_devices,
                                  data=calculate_size(dates)))

    with open(table_output, "w") as outfile:
        outfile.write(TABLE.render(table_body=table))

    with open(demo_output, "w") as outfile:
        outfile.write(
            DEMO.render(bar_labels=return_labels(dates.keys()),
                        bar_series=return_series(dates.values()),
                        pi_labels=return_labels(devices.keys()),
                        pi_series=return_series(devices.values()),
                        pi_2_labels=return_labels(custodians.keys()),
                        pi_2_series=return_series(custodians.values())))


def calculate_size(sizes):
    return sum(sizes.values())


def return_labels(list_object):
    return ", ".join("'{}'".format(x) for x in list_object)


def return_series(list_object):
    return ", ".join(str(x) for x in list_object)


if __name__ == "__main__":
    # Command-line Argument Parser
    parser = argparse.ArgumentParser(
        description=__description__,
        epilog="Developed by {} on {}".format(
            ", ".join(__authors__), __date__)
    )
    parser.add_argument("OUTPUT_DIR", help="Desired Output Path")
    args = parser.parse_args()

    main(args.OUTPUT_DIR)
