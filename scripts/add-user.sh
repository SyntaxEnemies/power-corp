#!/bin/bash
# HTTP client config
serv_port=5000
cookie_file='cookie-jar'
http_client="curl -L --silent --max-redirs 3 --cookie $cookie_file --cookie-jar $cookie_file"

if ! nc -z localhost "$serv_port"; then
    printf "\033[31m%s\033[0m\n" "Start flask development server on port $serv_port first."
    exit 1
fi

rand_str="$(tr -dc '[:upper:]' < /dev/urandom | head -c 6)"

rand_num() {
    if [[ -z $1 ]]; then
        printf "Random number size not given.\nExiting ...\n"
        exit 1
    fi

    tr -dc '[:digit:]' < /dev/urandom | head -c $1
}

# Basic details
fname='test'
lname="user$rand_str"
age=18
addr="test address $rand_str"
gender='Male'
mobile_num="$(rand_num 10)"
email="test$rand_str@example.com"

# Credit/Debit card details
cname="TEST USER$rand_str"
ctype='Credit'
cnum="$(rand_num 16)"
ccvv="$(rand_num 3)"
cexpiry='2030-11'

# Parse command-line args for username and password
while getopts "u:p:" arg; do
    case "$arg" in
        u) uname="$OPTARG" ;;
        p) pass="$OPTARG" ;;
    esac
done

# if username and password not provided as args
[[ -z "$uname" ]] && uname="test$rand_str"
[[ -z "$pass" ]] && pass='AAaa..11'

# User information request
$http_client --data "fname=$fname&lname=$lname&age=$age&addr=$addr&gender=$gender&mobile-num=$mobile_num&email=$email&card-name=$cname&card-type=$ctype&card-number=$cnum&card-cvv=$ccvv&card-expiry=$cexpiry" "localhost:$serv_port/register" > /dev/null

# Accept six digit OTP from user
read -p "Enter OTP (from flask log): " -n 6 otp

# Build verification request data form it.
# First five OTP digits
for ((i=0; i<5; ++i)); do
    req_data="${req_data}digits[]=${otp:$i:1}&"
done

# Last OTP digit
req_data="${req_data}digits[]=${otp:5:1}"

# TODO: Perform subsequent requests after the last one was successful

# OTP verification request
$http_client --data "$req_data" "localhost:$serv_port/verify" > /dev/null

# Set login credentials request
$http_client --data "username=$uname&password=$pass&confirm-password=$pass" "localhost:$serv_port/signup" > /dev/null

# TODO: Test login on newly created account

rm "$cookie_file"
