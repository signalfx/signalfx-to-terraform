import argparse
import logging
import os
import sys

from jinja2 import Environment, Template

sys.path.insert(0, '/Users/corywatson/src/signalfx-python')

import signalfx

def do_chart(client, chartId, name):
    c = client.get_chart(chartId)
    c['terraformName'] = name
    if c['options']['type'] == 'SingleValue':
        do_single_value_chart(client, c, name)
    else:
        print("TKTK")

def do_single_value_chart(client, chart, name):
    print(single_value_chart_template.render(chart))

def do_dashboard(client, dashboardId, name):
    d = client.get_dashboard(dashboardId)
    d['terraformName'] = name
    print(dashboard_template.render(d))

def do_detector(client, detectorId, name):
    d = client.get_detector(detectorId)
    d['terraformName'] = name
    print(detector_template.render(d))

parser = argparse.ArgumentParser()

parser.add_argument('--sfx_realm', help='SignalFx Realm (defaults to none)')
parser.add_argument('--verbose', help='Be verbose', action='store_const', const=True )
parser.add_argument('--chart', help='A chart to convert')
parser.add_argument('--dashboard', help='A dashboard to convert')
parser.add_argument('--detector', help='A detector to convert')
parser.add_argument('--name', help='Terraform name of resulting asset', required=True)

args = parser.parse_args()
if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

if 'SFX_AUTH_TOKEN' not in os.environ:
    logging.error('ERROR: Please specify an SFx auth token via SFX_AUTH_TOKEN')
    sys.exit(1)
sfx_api_key = os.environ['SFX_AUTH_TOKEN']

if args.sfx_realm is not None:
    # Use a realm if we get one
    sfx = signalfx.SignalFx(api_endpoint='https://api.' + args.realm + '.signalfx.com')

env = Environment(trim_blocks=True, lstrip_blocks=True)

single_value_chart_template = env.from_string('''resource "signalfx_single_value_chart" "{{ terraformName }}" {
    name                = "{{ name }}"
    {% if description != "" %}
    description         = "{{ description }}"
    {% endif %}
    {% if options.colorBy != "" %}
    color_by            = "{{ options.colorBy }}"
    {% endif %}
    color_scale         = TKTK
    maximum_precision   = {{ options.maximumPrecision }}
    is_timestamp_hidden = {{ options.timestampHidden }}
    refresh_interval    = {{ options.refreshInterval }}
    show_spark_line     = {{ options.showSparkLine }}
    {% if options.unitPrefix %}
    unit_prefix         = "{{ options.unitPrefix }}"
    {% endif %}

    program_text = <<-EOF
{{ programText }}
    EOF
}''')

dashboard_template = env.from_string('''{% for chart in charts %}
{{ do_chart(chart.chartId) }}
{% endfor %}
resource "signalfx_dashboard" "{{ terraformName }}" {
    name                = "{{ name }}"
    dashboard_group     = "{{ groupId }}"
    {% if description != "" %}
    description         = "{{ description }}"
    {% endif %}
    chart_resolution    = "{{ chartDensity | lower }}"

    {% for chart in charts %}
    chart {

    }
    {% endfor %}
}''')

detector_template = env.from_string('''resource "signalfx_detector" "{{ terraformName }}" {
    name                = "{{ name }}"
    {% if description != "" %}
    description         = "{{ description }}"
    {% endif %}
    {% if maxDelay != "" %}
    max_delay           = {{ maxDelay }}
    {% endif %}
    {% if teams | length > 0 %}
    teams               = {{ teams | tojson }}
    {% endif %}
    {% if tags | length > 0 %}
    tags                = {{ tags | tojson }}
    {% endif %}
    program_text        = <<-EOF
{{ programText }}
    EOF

    {% if visualizationOptions is not none  %}
    disable_sampling    = {{ visualizationOptions.disableSampling }}
    show_data_markers   = {{ visualizationOptions.showDataMarkers }}
    show_event_lines    = {{ visualizationOptions.showEventLines }}
    {% if visualizationOptions.time is defined and visualizationOptions.time is not none %}
    time_range          = {{ visualizationOptions.time.range }}
    start_time          = {{ visualizationOptions.time.start }}
    end_time            = {{ visualizationOptions.time.end }}
    {% endif %}
    {% endif %}

    {% for rule in rules %}
    rule {
        description             = "{{ rule.description }}"
        detect_label            = "{{ rule.detectLabel }}"
        {% if rule.tip != "" %}
        tip                     = "{{ rule.tip }}"
        {% endif %}
        severity                = "{{ rule.severity }}"
        disabled                = {{ rule.disabled }}
        {% if rule.parameterizedSubject != "" %}
        parameterized_subject   = "{{ rule.parameterizedSubject }}"
        {% endif %}
        {% if rule.parameterizedBody != "" %}
        parameterized_body      = "{{ rule.parameterizedBody }}"
        {% endif %}
        {% if rule.runbookUrl != "" %}
        runbook_url             = {{ rule.runbookUrl }}
        {% endif %}
        {% if notifications | length > 0 %}
        notifications = [
            {% for notification in rule.notifications %}
            {% if notification.type == "Team" %}
            "Team:{{ notification.team }}"
            {% endif %}
            {% endfor %}
        ]
        {% endif %}
    }
    {% endfor %}
}''')

if args.chart is None and args.dashboard is None and args.detector is None:
    sys.exit('Please supply a chart, dashboard, or detector ID to export')

if __name__ == "__main__":
    sfx = signalfx.SignalFx()
    if args.sfx_realm is not None:
        # Use a realm if we get one
        sfx = signalfx.SignalFx(api_endpoint='https://api.' + args.realm + '.signalfx.com')

    with sfx.rest(sfx_api_key) as rest:
        def do_chart_template(chartId):
            do_chart(rest, chartId, 'TKTKnamehere')

        env.globals.update(do_chart=do_chart_template)

        if args.chart:
            do_chart(rest, args.chart, args.name)
        elif args.dashboard:
            do_dashboard(rest, args.dashboard, args.name)
        elif args.detector:
            do_detector(rest, args.detector, args.name)
