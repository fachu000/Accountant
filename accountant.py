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

class Transaction:
    """An object of this class describes a bank transaction."""

    def __init__(self):
        self.d_date = []
        self.str_description = ''
        self.d_interestDate = []
        self.d_purchaseDate = []
        self.f_amount = 0 # >0 means incoming to the account
        self.str_fileName = ''

    def readTransactionFromString(str_csv,str_format,str_fileName):
#        return Transaction.readTransactionFromStringCreditCardFormat(str_csv)
        str1 = 'Date;Description;Interest date;In;Out;'
        str2 = ' "DATE";"DESCRIPTION";"PURCHASE DATE";"AMOUNT";'

        if str_format == str1:
            trans =  Transaction.readTransactionFromStringStandardFormat(str_csv)
        elif str_format[1:-1] == str2[1:-1]:
            trans =  Transaction.readTransactionFromStringCreditCardFormat(str_csv)
        else:
            print('ERROR: invalid format')
            print('format:"',str_format,'"')
            print('format:"',str2,'"')
            quit()

        if trans:
            trans.str_fileName = str_fileName

        return trans
        

    def readTransactionFromStringStandardFormat(str_csv):
        tran = Transaction()
        lstr_fields = str_csv.split(';')

        # date
        str_date = lstr_fields[0] 
        if len(str_date)>0:
            tran.d_date = Transaction.dateStrToDate(str_date)

        # description
        tran.str_description = lstr_fields[1]

        # interest date
        str_interestDate = lstr_fields[2] 
        if len(str_interestDate)>0:
            tran.d_interestDate = Transaction.dateStrToDate(str_interestDate)

        # Amount in 
        str_inAmount = lstr_fields[3].replace(',','.')
        if str_inAmount:
            f_in = float( str_inAmount )
        else:
            f_in = 0

        # Amount out 
        str_outAmount = lstr_fields[4].replace(',','.')
        if str_outAmount:
            f_out = float( str_outAmount )
        else:
            f_out = 0

        tran.f_amount = f_in + f_out
        
        return tran

    def readTransactionFromStringCreditCardFormat(str_csv):
        if len(str_csv)<5:
            return []
        elif str_csv[0:len('"TOTAL"')] == '"TOTAL"':
            return []
        

        tran = Transaction()

        lstr_fields = str_csv.split(';')

        # date
        str_date = lstr_fields[0].split('"')[1]
        if len(str_date)>0:
            tran.d_date = Transaction.dateStrToDate(str_date)

        # description
        tran.str_description = lstr_fields[1].split('"')[1]

        # Purchase date
        str_purchaseDate = lstr_fields[2].split('"')[1]
        if len(str_purchaseDate)>0:
            tran.d_purchaseDate = Transaction.dateStrToDate(str_purchaseDate)

        # Amount out 
        str_outAmount = lstr_fields[3].split('"')[1].replace(',','.')
        if str_outAmount:
            tran.f_amount = float( str_outAmount )
        else:
            tran.f_amount = 0

        return tran




    def dateStrToDate(str_date):

        if not str_date[0].isdigit():
            print('str_date = ',str_date)
            print('ERROR: invalid format of time field')
            quit()
        dt_out = date(int(str_date[6:10]),int(str_date[3:5]),int(str_date[0:2]))
        return dt_out

    def print(self):
        print('------------------------------')
        print('DATE: ',self.d_date)
        print('DESCRIPTION: ',self.str_description)
        print('INTEREST DATE: ',self.d_interestDate)
        print('PURCHASE DATE: ',self.d_purchaseDate)
        print('AMOUNT: ',self.f_amount)
        print('FILE NAME: ',self.str_fileName)
        print('------------------------------')


########################################################################

from datetime import datetime,timedelta,time,date

###############################

print('here we go')

str_transactionFileName = '../data/savings.csv'
#str_transactionFileName = '../data/creditCard.csv'

ll_files = [ ['../data/checking.csv', 'ISO-8859-1' ],
             ['../data/savings.csv', 'ISO-8859-1' ],
            ['../data/creditCard.csv','UTF8']]

l_transactions = [];

# read file
for l_file in ll_files:
    with open(l_file[0], 'r',encoding = l_file[1]) as input:
    #with open(str_transactionFileName, 'r',encoding = 'UTF8') as input:

        str_format = input.readline()[0:-1] # first line neglected

        for myline in input:
            tran = Transaction.readTransactionFromString(myline,str_format,l_file[0])
            if tran:
                l_transactions.append(tran)


for trans in l_transactions:
    trans.print()

quit()
