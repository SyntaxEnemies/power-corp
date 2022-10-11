#!/bin/bash
py=$(command -v python3)
echo "Using python at: $py"

echo "Creating virtual environment ..."
"$py" -m venv venv
source ./venv/bin/activate

echo "Installing project dependencies ..."
pip --require-virtualenv install -r requirements.txt

echo "Done :)"
