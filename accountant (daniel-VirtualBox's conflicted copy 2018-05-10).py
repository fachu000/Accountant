#  ACCOUNTANT 1.0
#
# PROGRAM TO KEEP PERSONAL ACCOUNTS
#
# NEXT STEPS:
# 
# - Create class transactions
# - Read files -> form list of Transactions that contains the transactions of all  accounts.
# - Save/load list of Transactions to a file
# - Function that combines the loaded list of Transactions with the list read from a file. The list is sorted by date at the end.
# - Graphical interface
#     -On top: buttons to load/save Transaction lists or to read files
#     -Below: text boxes to specify filters (which transactions to display)
#     -Below: list of transactions that pass the filters
#     -Below: one button per category-- used to assign the selected event to a category. We can use a similar code as for readCalendar. 
#     -Below: buttons to plot, e.g. 
        # - balance vs time
        # - the amount of the filtered transactions vs time
# - Automatic classification of transactions into categories. If a transaction has the same description field as an already classified transaction, then it is assigned to the same category. If there already exist multiple classified transactions with the same description and different category, then the transaction at hand should not be automatically classified. 
#


# For Python + GTK, see:  https://python-gtk-3-tutorial.readthedocs.io/en/latest/introduction.html

########################################################################


########################################################################

from datetime import datetime,timedelta,time,date

###############################

print('here we go')

str_transactionFileName = '../data/savings.csv'


# read file
with open(str_transactionFileName, 'r',encoding = "ISO-8859-1") as input:

    input.readline() # first line neglected
    
    for myline in input:
        print(myline,end='---')



quit()
