# You can define multiple sections. This can be used to make different kind of distributions from different accounts or nodes.
# 'default' is the main section, that is executed if nothing additionally is defined. If you want to execute another section,
# add it with the flag "-c" to the program call like this: "./fundsDistributor.py -c <my-own-section>
# You can add as many sections as you want. They need the parts "Sender", "Distribution", and "Distribution_Main".
# They can contain additional subgroups.
# Please make sure that the spacing and intents are correct and exact, they are important in .yml-files.

default:
    Sender:
        # Add here a host where you want to send the api commands to. I recommend to use your own node.
        # I strongly recommend to use only nodes that are pretected with SSL (https://....)
        # because your secret passphrase needs to be submitted to this node to be able to vote.
        # Make sure to not put a '/' at the end of it
        # Example:
        # Host: "https://login.lisk.io"
        Host: "REPLACE_ME"
        
        # Add here the address of the account from where you want to send the transactions
        # Example:
        # Address: "12312352346456L"
        Address: "REPLACE_ME"
        
        # Add here the PublicKey of your account
        # Example:
        # PublicKey: "234234645jfweijf9384rz76gr39ehg938th283th398gh94ghb832gb9238gbwiegb83f"
        PublicKey: "REPLACE_ME"
        
        # Add here your secret passphrase of the account you want to use to vote
        # The passphrase is needed to be able to send transactions
        # If you leave it empty like this: Secret: "", the script will ask you on the prompt to enter it during runtime.
        # Of course this can not be used when run by cron
        # Secret: "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12" 
        Secret: "REPLACE_ME"
        
        # Add here your second passphrase if you configured it.
        # If no second passphrase is configured, remove it completely.
        # If you leave it empty like this: SecondSecret: "", the script will ask you on the prompt to enter it during runtime.
        # Of course this can not be used when run by cron
        # Example:
        # mySecondSecret: "other1 other2 other3 other4 other5 other6 other7 other8 other9 other10 other11 other12" 
        SecondSecret: "REPLACE_ME"


    # Define here how much of your current account balance should be distributed.
    # There are two possibilities how to define it: What percentage of the current balance should be distributed,
    # or what amount should be left inside the account as a reserve.
    # Case 1: Distribute a specific percentage -> the following example distributes 90% of the current balance
    #     Style: "Percentage"
    #     Amount: 90%
    # Case 2: Leave only a given amount in the account -> the following example distributes everything, except 100 LSK
    #     Style: "AllExcept"
    #     Amount: 100
    Distribution:
        Style: "AllExcept"
        Amount: 100
    
    # Mandatory Main Group. Leave it as "Distribution_Main". This is the starting point.
    # Add multiple elements, consisting of "type", "value", "amount" and "description".
    # There are two possibilites for an element. Either a subgroup, that contains again several elements or a direct transaction,
    # 1. for a subgroup, define the following:
    #     type: "group"
    #     value: "Distribution_mySubgroup" -> that can be defined freely
    #     amount: "90%" -> percentage of the allocated amount of this group
    # 2. for a direct transaction, define the following:
    #     type: "direct"
    #     value: "12345678L" -> Account to send the amount to
    #     amount: "30%" -> percentage of the allocated amount of this group to send to this account
    #     description: "Servers -Maintenance" -> just a description, needed only for the log
    # Subgroups can contain again direct transactions or subgroubs. that creates a kind of a hierarchy.
    # Every subgroup takes the amount allocated to it again as 100% to distribute it further.

    # The following example should illustrate it.
    # Let's say the account contained 1000 LSK at the time of execution. Because we defined we want to distribute "AllExcept" 100LSK
    # the script will distribute 900 LSK, according to the allocations in Distribution_Main.
    
    # This will make the following:
    #  * A direct transaction to the donation account of cc001 of 9 LSK (1% of 900 LSK)
    #  * Allocate 180 LSK (20% of 900) to the group Distribution_Servers (see below)
    #  * Allocate 225 LSK (25% of 900) to the group Distribution_Donations (see below)
    #  * Allocate 486 LSK (54% of 900) to the group Distribution_Servers (see below)
    Distribution_Main:
        - type: "direct"
          value: "9959711110222257320L"
          amount: 1%
          description: "Donations - cc001"
        - type: "group"
          value: "Distribution_Servers"
          amount: 20
        - type: "group"
          value: "Distribution_Donations"
          amount: 25
        - type: "group"
          value: "Distribution_Private"
          amount: 54   
   
    # This group receives 180 LSK to distribute. Because it contains only one direct transaction of 100%, it executes the following:
    #  * Send 180 LSK to the Account with the number <Addr-Server-Maintenance>
    Distribution_Servers:
        - type: "direct"
          value: "<Addr-Server-Maintenance>"
          amount: 100%
          description: "Servers -Maintenance"

    # This group receives 225 LSK to distribute. It executes the following:
    #  * Send 45 LSK (20% of 225 LSK) to the Account with the number <Addr-Community-Fund>
    #  * Send 67.5 LSK (30% of 225 LSK) to the Account with the number <Addr-User-Fund>
    #  * Send 112.5 LSK (50% of 225 LSK) to the Account with the number <Addr-Project-Fund>
    Distribution_Donations:
        - type: "direct"
          value: "<Addr-Community-Fund>"
          amount: 20%
          description: "Donations - Lisk Community Fund"
       - type: "direct"
          value: "<Addr-User-Fund>"
          amount: 30%
          description: "Donations - User Fund"
        - type: "direct"
          value: "<Addr-Project-Fund>"
          amount: 50%
          description: "Donations - Project Fund"

    # This group receives 486 LSK to distribute. It executes the following:
    #  * Send 160.38 LSK (33% of 486 LSK) to the Account with the number <Addr-Voting-Account>
    #  * Send 160.38 LSK (33% of 486 LSK) to the Account with the number <Addr-Savings-Account>
    #  * Send 165.24 LSK (34% of 486 LSK) to the Account with the number <Addr-Wage-Account>
    Distribution_Private:
        - type: "direct"
          value: "<Addr-Voting-Account>"
          amount: 33%
          description: "Private Payout - Voting Account"
        - type: "direct"
          value: "<Addr-Savings-Account>"
          amount: 33%
          description: "Private Payout - Savings Account"
        - type: "direct"
          value: "<Addr-Wage-Account>"
          amount: 34%
          description: "Private Payout - Wage Account"

