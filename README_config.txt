# You can define multiple sections. This can be used to make different kind of distributions from different accounts or nodes.
# 'default' is the main section, that is executed if nothing additionally is defined. If you want to execute another section,
# add it with the flag "-c" to the program call like this: "./fundsDistributor.py -c <my-own-section>
# You can add as many sections as you want. They need at least the parts "Sender", "Distribution", and "Distribution_Main".
# They can contain additional subgroups.
# Please make sure that the spacing and intents are correct and exact, they are important in .yml-files.

default:
    Sender:
        # Add here a host where you want to send the api commands to. I recommend to use your own node.
        # I strongly recommend to use only nodes that are pretected with SSL (https://....)
        # because your secret passphrase needs to be submitted to this node to be able to execute transactions.
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
        
        # Add here your secret passphrase of the account you want to send the transactions from
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

    
    # "Distribution:" is a mandatory part 
    # Define here how much of your current account balance should be distributed.
    # There are three possibilities how to define it: What fixed amount should be distributed, what percentage of the current balance
    # should be distributed, or what amount should be left inside the account as a reserve.
    #
    # Case 1: Distribute a fixed amount -> the following example distributes 250 LSK (if there is enough in the wallet)
    #     Style: "Fixed"
    #     Amount: 250
    #    
    # Case 2: Distribute a specific percentage -> the following example distributes 90% of the current balance
    #     Style: "Percentage"
    #     Amount: 90%
    #
    # Case 3: Leave only a given amount in the account -> the following example distributes everything, except 100 LSK
    #     Style: "AllExcept"
    #     Amount: 100
    #
    # Example, distributes everything except 100 LSK:
    Distribution:
        Style: "AllExcept"
        Amount: 100
    
    # "Distribution_Main:" is the mandatory main group. Leave it as "Distribution_Main". This is the starting point.
    # Add multiple elements, consisting of "type", "value", "amount" and "description".
    # There are five possibilites for an element:
    # Either a subgroup, that contains again several elements, defined as a fixed value or a percentage value
    # or a direct transaction, also defined with a fixed value or a percentage, or a text file that contains the distribution
    
    # 1. for a subgroup with a percentage value, define the following ("description" is not needed):
    #     type: "group_percentage"
    #     value: "Distribution_mySubgroup" -> that is the name of another part. it can be defined freely
    #     amount: "90%"                    -> percentage of the allocated amount of this group
    #
    # 2. for a subgroup with a fixed value, use the following template:
    #     type: "group_fixed"
    #     value: "Distribution_mySubgroup" -> that is the name of another part
    #     amount: 500                      -> 500 LSK will be allocated to that group
    #
    # 3. for a direct transaction with a percentage value, define the following:
    #     type: "direct_percentage"
    #     value: "12345678L"                  -> Account to send the amount to
    #     amount: "30%"                       -> percentage of the allocated amount of this group to send to this account
    #     description: "Servers -Maintenance" -> just a description, needed only for the log
    #
    # 4. for a direct transaction with a fixed value, define the following:
    #     type: "direct_fixed"
    #     value: "12345678L"                  -> Account to send the amount to
    #     amount: 200                         -> send 200 LSK to this account
    #     description: "Servers -Maintenance" -> just a description, needed only for the log
    #
    # 5. for a textfile with the distributions, define the following (example.csv is a valid example file):
    #     type: "file_fixed"
    #     value: "example.csv"                -> Filename that contains your distribution. You can also use a relative or 
    #                                            absolute path
    #                                            See the file example.csv to find out how the file must look like. It is a csv file.
    #                                            First row (column names) must be exactly as in the example file. Then put every 
    #                                            Transaction on a separate line in the following format:
    #                                            <Amount>;<ReceiverAddress>;"<Description (only for documentation>"


    # Percentage values in one group should add up to 100%. If they are bigger than 100%, they won't be executed
    # If they are smaller than 100%, they will be executed.
    # Fixed amounts are executed only if enough funds are available. They are executed first and substracted from the allocated
    # amount to this group. The rest is distributed accordingly to the defined percentages.
    # Example: If allcate 1000LSK to a group, which contains a fixed transaction of 200LSK, one of 40% and one of 60%,
    # the following transactions will be executed:
    # 200LSK (fixed), 320LSK (40% of 800LSK, which is left after 200 are substracted from 1000), and 480 (60% of 800)

    # Subgroups can contain again direct transactions or subgroubs. that creates a kind of a hierarchy.
    # Every subgroup takes the amount allocated to it again as 100% to distribute it further.

    # The following example should illustrate it.
    # Let's say the account contained 1000 LSK at the time of execution. Because we defined we want to distribute "AllExcept" 100LSK
    # the script will distribute 900 LSK, according to the allocations in Distribution_Main.
    
    # This will make the following:
    #  * Allocate 180 LSK (fixed) to the group Distribution_Servers (see below)
    #  * A direct transaction to the donation account of cc001 of 36 LSK (5% of 720LSK (900 - 180))
    #  * Allocate 216 LSK (30% of 720) to the group Distribution_Donations (see below)
    #  * Allocate 468 LSK (65% of 720) to the group Distribution_Servers (see below)
    Distribution_Main:
        - type: "direct_percentage"
          value: "9959711110222257320L"
          amount: 5%
          description: "Donations - cc001"
        - type: "group_fixed"
          value: "Distribution_Servers"
          amount: 180
        - type: "group_percentage"
          value: "Distribution_Donations"
          amount: 30%
        - type: "group_percentage"
          value: "Distribution_Private"
          amount: 65%   
   
    # This group receives 180 LSK to distribute. Because it contains only one direct transaction of 100%, it executes the following:
    #  * Send 180 LSK to the Account with the number <Addr-Server-Maintenance>
    Distribution_Servers:
        - type: "direct"
          value: "<Addr-Server-Maintenance>"
          amount: 100%
          description: "Servers -Maintenance"

    # This group receives 216 LSK to distribute. It executes the following:
    #  * Send 43.2 LSK (20% of 216 LSK) to the Account with the number <Addr-Community-Fund>
    #  * Send 64.8 LSK (30% of 216 LSK) to the Account with the number <Addr-User-Fund>
    #  * Send 108 LSK (50% of 216 LSK) to the Account with the number <Addr-Project-Fund>
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

    # This group receives 468 LSK to distribute. It executes the following:
    #  * Send 150 LSK (fixed) to the Account with the number <Addr-Voting-Account>
    #  * Send 159 LSK (50% of 318 LSK) to the Account with the number <Addr-Savings-Account>
    #  * Send 159 LSK (50% of 318 LSK) to the Account with the number <Addr-Wage-Account>
    Distribution_Private:
        - type: "direct_fixed"
          value: "<Addr-Voting-Account>"
          amount: 150
          description: "Private Payout - Voting Account"
        - type: "direct"
          value: "<Addr-Savings-Account>"
          amount: 50%
          description: "Private Payout - Savings Account"
        - type: "direct"
          value: "<Addr-Wage-Account>"
          amount: 50%
          description: "Private Payout - Wage Account"

