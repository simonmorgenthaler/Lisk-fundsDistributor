#!/usr/bin/python

####################################################################################################################
# File name: fundsDistributor.py                                                                                   #
# Author: cc001                                                                                                    #
# Last modified: 2016-12-11                                                                                        #
#                                                                                                                  #
# This is a script to distribute your funds from one account to several other accounts.                            #
# The configuration of the accounts and what percentage to want to transfer is defined in the config.yml file      #
#                                                                                                                  #
# Installation: make sure to have installed the modules time, json, requests, yaml                                 #
# Example: For the in Ubuntu this is done with 'sudo apt-get install python-json python-requests python-yaml'      #
# You have to modify the file config.yml to adapt it for your needs. See the instructions in config.yml            #
#                                                                                                                  #
# Usage: make sure this script is executable with 'chmod +x fundsDistributor.py'                                   #
# Start the script with no parameters: './fundsDistributor.py' to use the default config                           #
# Or add the desired config section: './fundsDistributor.py -c cc001'                                              #
# If you add the flag '-y', the question if it should execute the transactions is answered automatically with yes. #
# This is neede if you want to execute the script automatically, for example with cron every week.                 #
# Use it like this: './fundsDistributor.py -y' or './fundsDistributor.py -y -c cc001'                              #
# Check the 'SIMULATION' flag below. It is useful to test your configuration. If you are sure you're configuration #
# is correct, set it to 'SIMULATION = False', to execute real transactions                                         #
#                                                                                                                  #
# If you like and use this script, please vote for 'cc001' as Delegate on test- and mainnet, Thanks!               #
####################################################################################################################

import json, requests
import sys
import yaml
import time
import argparse
import getpass

OK = '\033[92m'
ERROR = '\033[91m'
ATTENTION = '\033[93m'
STANDARD = '\033[0m'

SATOSHIS = 100000000.0

# Change this from 'True' to 'False' when you really want to execute the transactions and if you are
# sure your configuration is correct.
SIMULATION = True

##########################################################################################
### Don't change anything below this line, except you know exactly what you're doing!
##########################################################################################

def getTotalAmount():
    api = "/api/accounts/getBalance?address=" + config['Sender']['Address']
    result = callApi(api)
    if result['success']:
        return int(result['balance'])
    else:
        return NULL

def getTransactionFee():
    api = "/api/blocks/getFee"
    result = callApi(api)
    if result['success']:
        return int(result['fee'])
    else:
        return NULL

def getDistributedAmount(totalAmount):
    distributedAmount = 0
    distributionStyle = config['Distribution']['Style']
    distributionAmount = config['Distribution']['Amount']
    
    if distributionStyle == "Percentage":
        distributedAmount = totalAmount * getFloatAmount(distributionAmount) / 100
    elif distributionStyle == "AllExcept":
        distributedAmount = totalAmount - getFloatAmount(distributionAmount) * SATOSHIS
    elif distributionStyle == "Fixed":
        distributedAmount = getFloatAmount(distributionAmount) * SATOSHIS
    else:
        print "Error: Unknown Distribution-Style in config.yml"
    return distributedAmount

def getPriceUsd():
    #query = "https://api.coinmarketcap.com/v1/ticker/lisk/"
    query = "https://explorer.lisk.io/api/getPriceTicker"
    answer = ""
    try:
        response = requests.get(url=query, timeout=5)
        answer = json.loads(response.text)
    except requests.exceptions.RequestException as e:
        answer = []
    except ValueError, e:
        print "Not allowed"
        answer = []
    
    if not answer:
        priceUSD = 0
    else:
        #priceUSD = answer[0]['price_usd'] # coinmarketcap
        priceUSD = answer['lisk_usd']
    
    return priceUSD

def verifyConfiguredValues(distributionSection, sectionName):
    correct = True
    totalPercentage = 0
    for distribution in distributionSection:
        if distribution['type'] == "direct_percentage" or distribution['type'] == "group_percentage":
            totalPercentage += getFloatAmount(distribution['amount'])
    if totalPercentage > 100:
        print "ERROR: invalid total percentage in section", sectionName, ":", str(totalPercentage)
        correct = False
    return correct
    
def groupContainsFixedAmounts(DistributionSection):
    groupContainsFixedAmounts = False
    for distribution in DistributionSection:
        if distribution['type'] == "direct_fixed" or distribution['type'] == "group_fixed":
           groupContainsFixedAmounts = True
           break
    return groupContainsFixedAmounts
    
def getTotalFixedAmount(DistributionSection):
    totalFixedAmount = 0
    for distribution in DistributionSection:
        if distribution['type'] == "direct_fixed" or distribution['type'] == "group_fixed":
           totalFixedAmount += getFloatAmount(distribution['amount']) * SATOSHIS
    return totalFixedAmount
    
def calculateDistributions(distributedAmount, section):
    global error
    DistributionSection = config[section]
    if not verifyConfiguredValues(DistributionSection, section):
        error = True
        return
        
    totalFixedAmount = getTotalFixedAmount(DistributionSection)
    if totalFixedAmount > distributedAmount:
        print "ERROR: Fixed amount is bigger than the distributed amount for this group (" + section + "). Not executing these transactions"
        error = True
        return
    
    ## Loop first over fixed amounts, remove them from amounts to distribute
    for distribution in DistributionSection:    
        if distribution['type'] == "direct_fixed":
            amount = getFloatAmount(distribution['amount'])
            if amount <= 0:
                continue
            realAmount = amount * SATOSHIS - transactionFee
            addTransaction(realAmount, distribution['value'], distribution['description'])
            distributedAmount -= realAmount + transactionFee
        elif distribution['type'] == "group_fixed":
            amount = getFloatAmount(distribution['amount'])
            if amount <= 0:
                continue
            groupAmount = amount * SATOSHIS
            calculateDistributions(groupAmount, distribution['value'])
            distributedAmount -= groupAmount
  
    ## Loop over percentages
    for distribution in DistributionSection:
        if distribution['type'] == "direct_percentage":
            amount = getFloatAmount(distribution['amount'])
            if amount <= 0:
                continue
            realAmount = distributedAmount*amount/100 - transactionFee
            addTransaction(realAmount, distribution['value'], distribution['description'])
        elif distribution['type'] == "group_percentage":
            amount = getFloatAmount(distribution['amount'])
            if amount <= 0:
                continue
            groupAmount = distributedAmount*amount/100
            calculateDistributions(groupAmount, distribution['value'])

def getFloatAmount(amount):
    return float(str(amount).rstrip('%'))

def addTransaction(amount, address, description):
    transactions.append({'Amount': amount, 'Address': address, 'Description': description})
    
def checkConfirmation():
    print ""
    if SIMULATION:
        answer = raw_input("Is this ok? Should the transactions be executed? (SIMULATION! No real transactions will be executed) [y/n]: ").lower()
    else:
        answer = raw_input("Is this ok? Should the transactions be executed? [y/n]: ").lower()
    execute = False
    if answer == 'y' or answer == 'yes':
        execute = True
    return execute
    
def testSecret():
    if not config['Sender']['Secret']:
        config['Sender']['Secret'] = getpass.getpass('Passphrase: ')

def testSecondSecret():
    if 'SecondSecret' in config['Sender']:
        if not config['Sender']['SecondSecret']:
            config['Sender']['SecondSecret'] = getpass.getpass('Second Passphrase: ')
            
    
def transactionPreview(transactions):
  
    template_header = "{0:>12} | {1:>12} | {2:>12} | {3:22}| {4:40}| {5:10}"
    template = "{0:>12.4f} | {1:>12.2f} | {2:>11.2f}% | {3:22}| {4:40}| {5:10}"
    
    print "Following transactions will be executed:"
    print ""
    print template_header.format("Amount LSK", "Amount USD", "Percentage", "Receiving Address", "Reason", "Result") # header
    print "-------------|--------------|--------------|-----------------------|-----------------------------------------|---------------------------------------"
    for transaction in transactions:
      if distributedAmount != 0:
          percentage = float(transaction['Amount']+transactionFee) / float(distributedAmount) * 100.0
      else:
          percentage = 0
      print template.format(transaction['Amount']/SATOSHIS, float(transaction['Amount']/SATOSHIS)*float(priceUsd), percentage, transaction['Address'], transaction['Description'], "")

def executeTransactions(transactions):
    distributionResults = {
        'DistributedAmount': 0,
        'SuccessfulTransactions': 0,
        'FailedTransactions': 0,
        'TotalFees': 0
    }
    url = config['Sender']['Host'] + "/api/transactions"
    
    template_header = "{0:>12} | {1:>12} | {2:>12} | {3:22}| {4:40}| {5:10}"
    template = "{0:>12.4f} | {1:>12.2f} | {2:>11.2f}% | {3:22}| {4:40}| {5:10}"
    
    if SIMULATION:
        print ""
        print "!! SIMULATION, No real transactions executed !!"
        
    testSecret()
    testSecondSecret()
                    
    print ""
    print template_header.format("Amount LSK", "Amount USD", "Percentage", "Receiving Address", "Reason", "Result") # header
    print "-------------|--------------|--------------|-----------------------|-----------------------------------------|---------------------------------------"
    
    headers = {'content-type': 'application/json'}
    
    answer = {}
    
    for transaction in transactions:
        try:
            if SIMULATION:
                answer['success'] = True
                answer['transactionId'] = "123412341234"
            else:
                payload = {
                    'secret' : config['Sender']['Secret'],
                    'amount' : int(round(transaction['Amount'])),
                    'recipientId' : transaction['Address']
                }
                if 'SecondSecret' in config['Sender']:
                    payload['secondSecret'] = config['Sender']['SecondSecret']
                response = requests.put(url=url, data=json.dumps(payload), headers=headers, timeout=6.05, verify=False)
                answer = json.loads(response.text)
                
            if 'success' in answer and answer['success']:
                result = OK + "SUCCESS: (TxId: " + answer['transactionId'] + ")" + STANDARD
                distributionResults['DistributedAmount'] += int(round(transaction['Amount']))
                distributionResults['SuccessfulTransactions'] += 1
                distributionResults['TotalFees'] += transactionFee
            else:
                result = ERROR + "FAILURE: (" + answer['error'] + ")" + STANDARD
                distributionResults['FailedTransactions'] += 1
            
            percentage = float(transaction['Amount']+transactionFee) / float(distributedAmount) * 100.0
            
            print template.format(transaction['Amount']/SATOSHIS, float(transaction['Amount']/SATOSHIS)*float(priceUsd), percentage, transaction['Address'], transaction['Description'], result)
            
        except requests.exceptions.RequestException as e:
            print "ERROR"
    
    distributedPercentage = (distributionResults['DistributedAmount'] + distributionResults['TotalFees']) / float(distributedAmount) * 100.0
    print "-------------|--------------|--------------|-----------------------|-----------------------------------------|---------------------------------------"
    print template.format(float(distributionResults['DistributedAmount']/SATOSHIS), float(distributionResults['DistributedAmount']/SATOSHIS)*float(priceUsd), distributedPercentage, "", "", "")
                
    return distributionResults
    
def calculateTotalDistributions(transactions):
    totalDistributions = 0
    for transaction in transactions:
        totalDistributions += transaction['Amount']
    return totalDistributions

def callApi(api):
    query = config['Sender']['Host'] + api
    answer = ""
    try:
        response = requests.get(url=query, timeout=5)
        answer = json.loads(response.text)
    except requests.exceptions.RequestException as e:
        answer = []
    except ValueError, e:
        print "Not allowed"
        answer = []
        
    return answer   
    
def help():
    print "You need to append the desired config section"
    print "Example:", sys.argv[0], "cc001_test"
    
def updateConfigFile():
    
    filename = "config.yml"    
    replacements = {'"direct"':'"direct_percentage"', '"group"':'"group_percentage"'}
    foundOldStrings = False
    for old in replacements.keys():
        if old in open(filename).read():
            foundOldStrings = True
            break
    
    if foundOldStrings:
        file_in = open(filename).read()
        file_out = open(filename, 'w')
        for old in replacements.keys():
            file_in = file_in.replace(old, replacements[old])
        file_out.write(file_in)
        file_out.close
        print ""
        print ATTENTION + "Found old version of config.yml Updated to the new version. Everything OK" + STANDARD
        print ""
        
def readConfig():
    
    updateConfigFile()
    
    global config, interactiveMode
    with open("config.yml", 'r') as ymlfile:
        configuration = yaml.load(ymlfile)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', action='store', dest='configsection', default="default", help="Use the CONFIGSECTION in config.yml. If omitted, section 'default' is used")
    parser.add_argument('-y', action='store_false', default=True, dest='interactiveMode', help="If you set this flag, the confirmation before the execution of the transactions is answered automatically with 'yes'. This is usefull if the script is executed automatically, for example with cron, and shouldn't wait for an answer.")
    
    arguments = parser.parse_args()
    configsection = arguments.configsection
    interactiveMode = arguments.interactiveMode

    if not configsection in configuration:
        print "Unknown config section in config.yml:", configsection
        exit(0)

    config = configuration[configsection]
    
    if config['Sender']['Host'] == "REPLACE_ME" or config['Sender']['Address'] == "REPLACE_ME" or config['Sender']['PublicKey'] == "REPLACE_ME" or config['Sender']['Secret'] == "REPLACE_ME" or ('SecondSecret' in config['Sender'] and config['Sender']['SecondSecret'] == "REPLACE_ME"):
        print "Please read the instructions at the top of this file and adapt the configuration in config.yml accordingly"
        print "Type './fundsDistributor.py -h' for help"
        exit (0)

    config['Sender']['Host'] = config['Sender']['Host'].rstrip('/') # Remove trailing slashes
    

template = "{:27} {:20}"

error = False
transactions = []
interactiveMode = False
readConfig()

print "#### START", time.strftime("%Y-%m-%d %H:%M:%S")
totalAmount = getTotalAmount()
transactionFee = getTransactionFee()
distributedAmount = getDistributedAmount(totalAmount)
priceUsd = getPriceUsd()

print template.format("Balance:", str(totalAmount / SATOSHIS))
print template.format("Fee per transaction:", str(transactionFee / SATOSHIS))
print template.format("Amount to distribute:", str(distributedAmount / SATOSHIS) + " LSK (" + str(distributedAmount / SATOSHIS * float(priceUsd)) + " USD) - (" + str(config['Distribution']['Style']) + ": " + str(config['Distribution']['Amount']) + ")")
print template.format("LSK/USD", str(priceUsd));
print ""

if distributedAmount <= 0:
    print "ERROR: distributed Amount is negative:", str(distributedAmount / SATOSHIS)
    error = True
elif distributedAmount > totalAmount:
    print "ERROR: distributed Amount is bigger than the available balance:", str(distributedAmount / SATOSHIS)
    error = True
else:
    calculateDistributions(distributedAmount, "Distribution_Main")

if not error:
  
    confirmation = True
    if interactiveMode:
        transactionPreview(transactions)
        confirmation = checkConfirmation()
    
    if confirmation:
        distributionResults = executeTransactions(transactions)
        print ""
        print template.format("Successful transactions:", str(distributionResults['SuccessfulTransactions']))
        print template.format("Failed transactions:", str(distributionResults['FailedTransactions']))
        print template.format("Totally distributed:", str((distributionResults['DistributedAmount'] + distributionResults['TotalFees'])/ SATOSHIS) + " (" + str(distributionResults['DistributedAmount']/SATOSHIS) + " + " + str(distributionResults['TotalFees']/SATOSHIS) + " Fees)")

    else:
        print ""
        print "Aborted. Doing nothing\n"
    
    
print "#### END", time.strftime("%Y-%m-%d %H:%M:%S")
print ""
