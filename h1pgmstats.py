from flask import Flask, render_template, request
from concurrent.futures import ThreadPoolExecutor
import threading
import requests
import json
import argparse

app = Flask(__name__)

URL_FOR_PUBLIC_HANDLES = "https://zy9ard3.github.io/h1pub.txt"
GRAPHQL_ENDPOINT = "https://hackerone.com/graphql"
GRAPHQL_QUERY = """
query TeamProfilePage($handle: String!) {
    team(handle: $handle) {
        id
        name
        handle
        state
        url
        ...BountyTableTeam
        ...BountyMetricTeam
        ...HackersThankedTeam
        ...ProfileMetricsTeam
        ...TeamDeclarativePolicyTeam
        ...ResponseEfficiencyPercentageTeam
    }
}

fragment BountyTableTeam on Team {
    id
    handle
    bounty_table {
        id
        low_label
        medium_label
        high_label
        critical_label
        use_range
        bounty_table_rows(first: 100) {
            edges {
                node {
                    id
                    low
                    medium
                    high
                    critical
                    low_minimum
                    medium_minimum
                    high_minimum
                    critical_minimum
                    smart_rewards_start_at
                    structured_scope {
                        id
                        asset_identifier
                    }
                }
            }
        }
    }
}

fragment BountyMetricTeam on Team {
    id
    base_bounty
    bounty_table {
        id
    }
}

fragment HackersThankedTeam on Team {
    id
    participants {
        total_count
    }
}

fragment ProfileMetricsTeam on Team {
    id
    handle
    currency
    offers_bounties
    average_bounty_lower_amount
    average_bounty_upper_amount
    top_bounty_lower_amount
    top_bounty_upper_amount
    formatted_total_bounties_paid_prefix
    formatted_total_bounties_paid_amount
    resolved_report_count
    formatted_bounties_paid_last_90_days
    reports_received_last_90_days
    last_report_resolved_at
    most_recent_sla_snapshot {
        id
        first_response_time: average_time_to_first_program_response
        triage_time: average_time_to_report_triage
        bounty_time: average_time_to_bounty_awarded
        resolution_time: average_time_to_report_resolved
    }
}

fragment TeamDeclarativePolicyTeam on Team {
    id
    handle
    declarative_policy {
        id
        complies_with_standard_ineligible_findings
        has_open_scope
        pays_within_one_month
        protected_by_gold_standard_safe_harbor
        introduction
        contact_email
    }
}

fragment ResponseEfficiencyPercentageTeam on Team {
    id
    response_efficiency_percentage
    response_efficiency_indicator
    team_display_options {
        id
        show_response_efficiency_indicator
    }
}
"""

def fetch_data(handle, headers):
    response = requests.post(GRAPHQL_ENDPOINT, json={'query': GRAPHQL_QUERY, 'variables': {'handle': handle}}, headers=headers)
    if response.status_code == 200:
        try:
            data = response.json()
            team_data = data.get("data", {}).get("team", {})
            if team_data:
                low = team_data.get("average_bounty_lower_amount", "0")
                high = team_data.get("top_bounty_upper_amount", "0")

                low = str(low) if low is not None else "0"
                high = str(high) if high is not None else "0"
                bounty_range = f"${low} - ${high}" if low != "0" or high != "0" else "-"

                extracted_data = {
                    'name': team_data.get("name", ""),
                    'url': team_data.get("url", ""),
                    'type': team_data.get("state", ""),
                    'bounty_range': bounty_range,
                    'total_bounties_paid': team_data.get("formatted_total_bounties_paid_amount", 0),
                    'resolved_report_count': team_data.get("resolved_report_count", 0),
                    'bounties_paid_in_last_90_days': team_data.get("formatted_bounties_paid_last_90_days", 0),
                    'reports_received_in_last_90_days': team_data.get("reports_received_last_90_days", 0),
                    'response_efficiency': team_data.get("response_efficiency_percentage", 0)
                }
                return extracted_data
            else:
                print(handle, ": Team data not found in JSON response")
                return {}
        except json.JSONDecodeError:
            print("Error decoding JSON response")
            return {}
    else:
        print("Error fetching data:", response.text)
        return {}

def read_handle_values(url):
    response = requests.get(url)
    lines = response.text.strip().split('\n')
    return lines

def worker(handle, headers, results):
    result = fetch_data(handle, headers)
    if result:
        results.append(result)

def run_parallel(headers, url):
    handles = read_handle_values(url)
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_handle = {executor.submit(worker, handle.strip(), headers, results): handle for handle in handles}

        for future in future_to_handle:
            future.result()

    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stats', methods=['POST'])
def run():
    run_type = request.form.get('run_type')
    headers = {
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }

    if run_type == "authenticated":
        csrf_token = request.form.get('csrf_token')
        cookie = request.form.get('cookie')
        url = request.form.get('url_auth')

        csrf_token = csrf_token.strip() if csrf_token else ""
        cookie = cookie.strip() if cookie else ""

        if csrf_token:
            headers['X-Csrf-Token'] = csrf_token

        if cookie:
            headers['Cookie'] = cookie

    else:
        url = URL_FOR_PUBLIC_HANDLES

    results = run_parallel(headers, url)

    return render_template('h1pgmstats.html', data=results)

if __name__ == '__main__':
    app.run(debug=True)
