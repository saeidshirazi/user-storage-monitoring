# User Storage and Activity Monitoring

This project reads data from `lastlog.txt` and `usage.txt`, processes user storage information, and generates a plot of the top 10 users based on their storage usage.

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)


## Description

This project analyzes user storage and login activity based on the outputs of the following commands:

1. `du -A -d 1` - Provides the amount of storage in kilobytes for each user in their home directories.
2. `lastlog` - Shows each user and the date of their last successful login on the primary SSH server.

The script processes these inputs to handle user status and sorts users by their storage cost. It also creates a plot of the top 10 users based on storage cost.

## Features

- Reads and processes storage usage data (`usage.txt`).
- Reads and processes last login data (`lastlog.txt`).
- Sorts users by their storage usage.
- Generates a plot for the top 10 users based on storage cost.

## Installation

### Prerequisites

- Python 3.6 or higher
- pipenv for managing virtual environments

### Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/user-storage-monitoring.git
    cd user-storage-monitoring
    ```

2. Install the dependencies:

    ```bash
    pipenv shell
    pip install -r requirements.txt
    ```

## Usage

To run the script and generate the report, execute:

```bash
python server.py
```
