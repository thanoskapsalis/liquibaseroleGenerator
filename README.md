# Liquibase XML Generation Script

This script generates Liquibase XML changelog files for managing database changes for roles and rights. It can be used to create database change sets for roles and their associated rights.

## Prerequisites

- Python 3.x
- `xml.etree.ElementTree` library (usually comes with Python)
- Command-line environment

## Usage

1. Clone or download this repository to your local machine.

2. Open a command-line terminal.

3. Navigate to the directory where the script is located.

4. Run the script with the following command:

   ```bash
   python script.py --dbDriver [DATABASE_DRIVER] --roleName [ROLE_NAME] --rightsFile [RIGHTS_FILE] --revision [REVISION]
