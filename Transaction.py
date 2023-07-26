from datetime import datetime, timedelta, time, date
import math as math
import matplotlib.pyplot as plt
import pickle
import numpy as np

import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Transaction:
    """An object of this class describes a bank transaction."""

    lstr_categoryLabels = [
        'FUN', 'FOOD', 'CAR', 'MUSIC', 'FAMILY', 'HOME', 'ANIMALS', 'WORK'
    ]
    lstr_accountLabels = ['CREDIT_CARD-NO', 'CHECKING-NO', 'SAVINGS-NO']

    def __init__(self):
        self.d_date = []
        self.str_description = ''
        self.d_interestDate = []
        self.d_purchaseDate = []
        self.f_amount = 0  # >0 means incoming to the account
        self.str_account = ''
        self.str_category = ''
        self.str_comment = ''

    def readTransactionFromString(str_csv, str_format):
        #        return Transaction.readTransactionFromStringCreditCardFormat(str_csv)
        str1 = 'Date;Description;Interest date;In;Out;'
        str2 = ' "DATE";"DESCRIPTION";"PURCHASE DATE";"AMOUNT";'

        if str_format == str1:
            trans = Transaction.readTransactionFromStringStandardFormat(
                str_csv)
        elif str_format[1:-1] == str2[1:-1]:
            trans = Transaction.readTransactionFromStringCreditCardFormat(
                str_csv)
        else:
            print('ERROR: invalid format')
            print('format:"', str_format, '"')
            print('format:"', str2, '"')
            quit()

        return trans

    def readTransactionFromStringStandardFormat(str_csv):
        tran = Transaction()
        lstr_fields = str_csv.split(';')

        # date
        str_date = lstr_fields[0]
        if len(str_date) > 0:
            tran.d_date = Transaction.dateStrToDate(str_date)

        # description
        tran.str_description = lstr_fields[1]

        # interest date
        str_interestDate = lstr_fields[2]
        if len(str_interestDate) > 0:
            tran.d_interestDate = Transaction.dateStrToDate(str_interestDate)

        # Amount in
        str_inAmount = lstr_fields[3].replace(',', '.')
        if str_inAmount:
            f_in = float(str_inAmount)
        else:
            f_in = 0

        # Amount out
        str_outAmount = lstr_fields[4].replace(',', '.')
        if str_outAmount:
            f_out = float(str_outAmount)
        else:
            f_out = 0

        tran.f_amount = f_in + f_out

        return tran

    def readTransactionFromStringCreditCardFormat(str_csv):
        if len(str_csv) < 5:
            return []
        elif str_csv[0:len('"TOTAL"')] == '"TOTAL"':
            return []

        tran = Transaction()

        lstr_fields = str_csv.split(';')

        # date
        str_date = lstr_fields[0].split('"')[1]
        if len(str_date) > 0:
            tran.d_date = Transaction.dateStrToDate(str_date)

        # description
        tran.str_description = lstr_fields[1].split('"')[1]

        # Purchase date
        str_purchaseDate = lstr_fields[2].split('"')[1]
        if len(str_purchaseDate) > 0:
            tran.d_purchaseDate = Transaction.dateStrToDate(str_purchaseDate)

        # Amount out
        str_outAmount = lstr_fields[3].split('"')[1].replace(',', '.')
        if str_outAmount:
            tran.f_amount = float(str_outAmount)
        else:
            tran.f_amount = 0

        return tran

    def dateStrToDate(str_date):

        if not str_date[0].isdigit():
            print('str_date = ', str_date)
            print('ERROR: invalid format of time field')
            quit()
        dt_out = date(int(str_date[6:10]), int(str_date[3:5]),
                      int(str_date[0:2]))
        return dt_out

    def print(self):
        print('------------------------------')
        print('DATE: ', self.d_date)
        print('DESCRIPTION: ', self.str_description)
        print('INTEREST DATE: ', self.d_interestDate)
        print('PURCHASE DATE: ', self.d_purchaseDate)
        print('AMOUNT: ', self.f_amount)
        print('ACCOUNT: ', self.str_account)
        print('CATEGORY: ', self.str_category)
        print('COMMENT: ', self.str_comment)
        print('------------------------------')

    def readTransactionListFromCSVFile(ll_files):
        l_transactions = []

        for l_file in ll_files:
            with open(l_file[0], 'r', encoding=l_file[1]) as input:

                str_format = input.readline()[
                    0:-1]  # first line gives the format

                for myline in input:
                    tran = Transaction.readTransactionFromString(
                        myline, str_format)
                    if tran:
                        tran.str_account = l_file[2]
                        l_transactions.append(tran)

        return Transaction.sortTransactionList(l_transactions)

    def saveTransactionList(l_transactions, str_filename):

        with open(str_filename, 'wb') as output:
            pickle.dump(l_transactions, output, pickle.HIGHEST_PROTOCOL)
        print('Saving to ', str_filename)

    def loadTransactionList(str_filename):
        """returns a list of transactions loaded from the file with name
        <str_filename>."""

        with open(str_filename, 'rb') as input:
            l_transactions = pickle.load(input)

        return l_transactions

    def combineListsOfTransactions(l_master, l_slave):
        """The nodes of l_slave are added to the list l_master if a node with 
        the same dates, amount, and description does not already exist"""

        num_newTransactions = 0
        for slaveTransaction in l_slave:
            b_matchingTransaction = False
            for masterTransaction in l_master:
                if (slaveTransaction.d_date == masterTransaction.d_date) \
                   and (slaveTransaction.f_amount == masterTransaction.f_amount)\
                   and (slaveTransaction.d_interestDate == masterTransaction.d_interestDate)\
                   and (slaveTransaction.d_purchaseDate == masterTransaction.d_purchaseDate)\
                   and (slaveTransaction.str_description == masterTransaction.str_description):

                    # print('matching transaction:')
                    # masterTransaction.print()
                    b_matchingTransaction = True
                    break

            if not b_matchingTransaction:
                l_master.append(slaveTransaction)
                num_newTransactions = num_newTransactions + 1

        l_master = Transaction.sortTransactionList(l_master)
        return num_newTransactions

    def sortTransactionList(l_transactions):

        l_transactions = sorted(l_transactions,
                                key=lambda transaction: transaction.d_date)

        return l_transactions

    def autoAssignTransactionsToCategory(l_transactions):

        for transaction in l_transactions:
            Transaction.autoAssignTransactionToCategory(
                l_transactions, transaction)

    def autoAssignTransactionToCategory(l_transactions,
                                        transactionToBeAssigned):
        """Assigns transaction to a category C if each transactions in
        <l_transactions> with the same description as <transaction> is
        assigned either to C or not assigned to any category."""

        if transactionToBeAssigned.str_category:
            return
        category = ''
        for tran in l_transactions:
            if tran.str_description == transactionToBeAssigned.str_description:
                if category:
                    if (tran.str_category) and (category != tran.str_category):
                        return  # since there are two transactions with the
                        # same description as
                        # <transactionToBeAssigned> and they are
                        # assigned to different categories.
                else:
                    category = tran.str_category

        transactionToBeAssigned.str_category = category

    def firstAndLastDates(l_transactions):

        firstDate = l_transactions[1].d_date
        lastDate = l_transactions[-1].d_date
        for transaction in l_transactions:
            if transaction.d_date < firstDate:
                firstDate = transaction.d_date
            if transaction.d_date > lastDate:
                lastDate = transaction.d_date

        return firstDate, lastDate

    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #
    # FUNCTIONS TO FILTER
    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #

    def filterByDate(l_transactions, d_start, d_end):
        l_transactionsFilteredByDate = [None] * len(l_transactions)

        for indTransaction in range(0, len(l_transactions)):

            if (l_transactions[indTransaction].d_date >= d_start ) \
               and (l_transactions[indTransaction].d_date <= d_end ) :
                l_transactionsFilteredByDate[indTransaction] = True
            else:
                l_transactionsFilteredByDate[indTransaction] = False

        return l_transactionsFilteredByDate

    def filterByAccount(l_transactions, dc_activeAccounts):

        l_transactionsFilteredByAccount = [None] * len(l_transactions)

        for indTransaction in range(0, len(l_transactions)):
            if l_transactions[indTransaction].str_account:
                if dc_activeAccounts[
                        l_transactions[indTransaction].str_account]:
                    l_transactionsFilteredByAccount[indTransaction] = True
                else:
                    l_transactionsFilteredByAccount[indTransaction] = False
            else:
                l_transactionsFilteredByAccount[indTransaction] = False

        return l_transactionsFilteredByAccount

    def filterByCategory(l_transactions, dc_activeCategories):

        l_transactionsFilteredByCategory = [None] * len(l_transactions)

        for indTransaction in range(0, len(l_transactions)):
            if l_transactions[indTransaction].str_category:
                if dc_activeCategories[
                        l_transactions[indTransaction].str_category]:
                    l_transactionsFilteredByCategory[indTransaction] = True
                else:
                    l_transactionsFilteredByCategory[indTransaction] = False
            else:
                if dc_activeCategories['No Category']:
                    l_transactionsFilteredByCategory[indTransaction] = True
                else:
                    l_transactionsFilteredByCategory[indTransaction] = False

        return l_transactionsFilteredByCategory

    def filterByDescription(l_transactions, str_description):
        l_transactionsFilteredByDescription = [True] * len(l_transactions)

        if not str_description:
            return l_transactionsFilteredByDescription

        for indTransaction in range(0, len(l_transactions)):

            if str_description.upper(
            ) in l_transactions[indTransaction].str_description.upper():
                l_transactionsFilteredByDescription[indTransaction] = True
            else:
                l_transactionsFilteredByDescription[indTransaction] = False

            print('-------------')
            print(l_transactions[indTransaction].str_description)
            print(str_description)
            print(l_transactionsFilteredByDescription[indTransaction])
        return l_transactionsFilteredByDescription

    def listAnd(*args):
        return [all(tuple) for tuple in zip(*args)]

    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #
    # FUNCTIONS TO OBTAIN FIGURES
    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #

    def plotTotalOverTime(l_transactions):

        l_timeAxis = [None] * (len(l_transactions) + 1)
        l_timeAxis[0] = l_transactions[0].d_date
        l_total = [None] * (len(l_transactions) + 1)
        l_total[0] = 0
        for indTransaction in range(0, len(l_transactions)):
            l_total[indTransaction + 1] = l_total[
                indTransaction] + l_transactions[indTransaction].f_amount
            l_timeAxis[indTransaction +
                       1] = l_transactions[indTransaction].d_date

        dates = ['01/01/1991', '01/03/1991', '01/04/1991']

        dates = [d.strftime('%Y/%m/%d') for d in l_timeAxis]
        x = [dt.datetime.strptime(d, '%Y/%m/%d').date() for d in dates]
        y = l_total  # range(len(x)) # many thanks to Kyss Tao for setting me straight here

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.plot(x, y, 'ro-')
        plt.gcf().autofmt_xdate()
        plt.show()
        return

    def plotTotalPerCategoryOverTime(l_transactions, dc_activeCategories,
                                     dateStart, dateEnd, str_description,
                                     dc_activeAccounts):

        i_numCols = 2
        i_numRows = math.ceil(len(dc_activeCategories) / (i_numCols * 1.0))

        t2 = np.arange(0.0, 5.0, 0.02)

        plt.figure(1)
        for indCategory in range(0, len(dc_activeCategories)):

            plt.subplot(i_numRows, i_numCols, indCategory)
            plt.plot(t2, np.cos(2 * np.pi * t2), 'r--')
            print(dc_activeCategories)
            print(indCategory)


#            plt.title(dc_activeCategories[indCategory])

        plt.show()

        print('finish this')
