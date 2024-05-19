import csv
import os
from datetime import datetime, timezone
import re
import pandas as pd
import matplotlib.pyplot as plt

# Constants
INACTIVE_THRESHOLD = 365
GB_MONTH_FACTOR = 30

class UserStatus:
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    UNKNOWN = 'Unknown'

def read_lastlog(file_path):
    data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()[1:]
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 3:
                username = parts[0]
                lastlogin = ' '.join(parts[2:])
                if lastlogin == '**Never logged in**':
                    lastlogin = None
                data.append({'user': username, 'lastlogin': lastlogin})
    return data

def read_usage(file_path):
    data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                usage = int(parts[0])
                username = parts[1].split('/')[-1]
                data.append({'user': username, 'usage': usage})
    return data

def calculate_days_between(lastlogin_str):
    if lastlogin_str:
        if lastlogin_str == '**Never logged in**':
            return None
        else:
            try:
                lastlogin_date = parse_date(lastlogin_str)
                today = datetime.now(timezone.utc)
                days_between = (today - lastlogin_date).days
                return days_between
            except ValueError:
                # Handle the case where the last login entry is 'logged in**'
                return None
    return None

def parse_date(date_str):
    # Regex pattern to match the date format
    pattern = r"(\w{3} \w{3} \d{1,2} \d{2}:\d{2}:\d{2} [+\-]\d{4} \d{4})"
    match = re.search(pattern, date_str)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
    else:
        raise ValueError("Invalid date format")

def calculate_storage_cost(storage, days_inactive):
    return storage * (days_inactive / GB_MONTH_FACTOR)

def merge_data(lastlog_data, usage_data):
    merged_data = []
    for lastlog_entry in lastlog_data:
        username = lastlog_entry['user']
        usage_entry = next((entry for entry in usage_data if entry['user'] == username), None)
        
        days_between = calculate_days_between(lastlog_entry.get('lastlogin', None))
        if days_between is not None and days_between > INACTIVE_THRESHOLD:
            status = UserStatus.INACTIVE
        elif days_between is not None:
            status = UserStatus.ACTIVE
        else:
            status = UserStatus.UNKNOWN
        
        if usage_entry is not None:
            if days_between is not None and days_between > INACTIVE_THRESHOLD:
                storage_cost = calculate_storage_cost(usage_entry['usage'], days_between)
            else:
                storage_cost = usage_entry['usage']
        else:
            storage_cost = None

        merged_data.append({
            'user': username,
            'lastlogin': lastlog_entry.get('lastlogin', None),
            'time_between': f"{days_between} Days" if days_between is not None else 'Information not available',
            'status': status,
            'storage_cost': storage_cost
        })

    return merged_data

def write_to_csv(data, output_file):
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['user', 'lastlogin', 'time_between', 'status', 'storage_cost']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def write_to_xlsx(data, output_file):
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)
    
def plot_top_10_users(data):
    top_10_users = sorted(data, key=lambda x: x['storage_cost'] if x['storage_cost'] is not None else 0, reverse=True)[:10]
    users = [entry['user'] for entry in top_10_users]
    storage_costs = [entry['storage_cost'] / (1024 ** 3) if entry['storage_cost'] is not None else 0 for entry in top_10_users]  # Convert bytes to GB
    colors = plt.cm.viridis(range(len(users)))  # Get a color map

    plt.figure(figsize=(10, 6))
    bars = plt.bar(users, storage_costs, color=colors)
    plt.xlabel('Users')
    plt.ylabel('Storage Cost (GB)')
    plt.title('Top 10 Users by Storage Cost')
    plt.xticks(rotation=45, ha='right')
    
    # Add the storage cost values on top of each bar
    for bar, cost in zip(bars, storage_costs):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05, f'{cost:.2f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig('top_10_users_plot.png')


def main():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    lastlog_file = os.path.join(script_directory, 'lastlog.txt')
    usage_file = os.path.join(script_directory, 'usage.txt')

    try:
        lastlog_data = read_lastlog(lastlog_file)
        usage_data = read_usage(usage_file)
        merged_data = merge_data(lastlog_data, usage_data)

        # Prompt user for output format
        output_format = input("Enter the desired output format (CSV or XLSX): ").lower()
        output_file = os.path.join(script_directory, 'result.' + output_format)

        if output_format not in ['csv', 'xlsx']:
            raise ValueError("Invalid output format. Please choose either CSV or XLSX.")
        
        # Prompt user for sorting option
        sort_option = input("Do you want to sort based on storage cost? (yes/no): ").lower()
        if sort_option == 'yes':
            sorted_merged_data = sorted(merged_data, key=lambda x: x['storage_cost'] if x['storage_cost'] is not None else float('inf'), reverse=True)
        else:
            sorted_merged_data = merged_data

        if output_format == 'csv':
            write_to_csv(sorted_merged_data, output_file)
        elif output_format == 'xlsx':
            write_to_xlsx(sorted_merged_data, output_file)
        
        plot_top_10_users(sorted_merged_data)

        print(f"Data has been successfully written to {output_file}")
        print("Top 10 users plot has been saved as 'top_10_users_plot.png'")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
