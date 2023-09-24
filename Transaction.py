import csv
from datetime import datetime, timedelta, time, date
import math as math
import matplotlib.pyplot as plt
import pickle
import numpy as np

import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

ll_default_csv_files = [['../../data/CSV/checking.csv', 'UTF8', 'CHECKING-NO'],
                        ['../../data/CSV/savings.csv', 'UTF8', 'SAVINGS-NO'],
                        [
                            '../../data/CSV/creditCard.csv', 'UTF8',
                            'CREDIT_CARD-NO'
                        ]]


class CsvProcessor:

    @classmethod
    def isMe(cls, str_format):
        return str_format == cls.str_format


class OldCheckingCsvProcessor(CsvProcessor):

    str_format = 'Date;Description;Interest date;In;Out;'

    @staticmethod
    def getTransactionFromString(str_csv):

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


class CheckingCsvProcessor(CsvProcessor):
    #str_format = "ï»¿Dato;Beskrivelse;Rentedato;Inn;Ut;Til konto;Fra konto;"
    str_format = '\ufeffDato;Beskrivelse;Rentedato;Inn;Ut;Til konto;Fra konto;'

    @staticmethod
    def getTransactionFromString(str_csv):

        if str_csv == '\n':
            return None

        tran = Transaction()

        #lstr_fields = str_csv.split(';') lstr_fields = [f[1:-1] for f in
        #        lstr_fields]
        #
        # The following method is needed because sometimes there are semicolons
        # inside quotes in the description field.
        lstr_fields = next(csv.reader([str_csv], delimiter=';', quotechar='"'))

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

        tran.toAccount = lstr_fields[5]
        tran.fromAccount = lstr_fields[6]

        return tran


class OldCreditCardCsvProcessor(CsvProcessor):
    str_format = ' "DATE";"DESCRIPTION";"PURCHASE DATE";"AMOUNT";'

    @staticmethod
    def isMe(str_format):
        return str_format[1:-1] == OldCreditCardCsvProcessor.str_format[1:-1]

    @staticmethod
    def getTransactionFromString(str_csv):

        if len(str_csv) < 5:
            return None
        elif str_csv[0:len('"TOTAL"')] == '"TOTAL"':
            return None

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


class CreditCardCsvProcessor(CsvProcessor):
    str_format = '\ufeff"Kjøpsdato";"Posteringsdato";"Beskrivelse";"Beløp"'

    @staticmethod
    def isMe(str_format):
        return str_format == CreditCardCsvProcessor.str_format

    @staticmethod
    def getTransactionFromString(str_csv):

        def dateStrToDate(str_date):

            if not str_date[0].isdigit():
                print('str_date = ', str_date)
                raise TypeError('invalid format of time field')

            dt_out = date(year=int(str_date[0:4]),
                          month=int(str_date[5:7]),
                          day=int(str_date[8:10]))
            return dt_out

        # if len(str_csv) < 5:
        #     return None
        # elif str_csv[0:len('"TOTAL"')] == '"TOTAL"':
        #     return None

        tran = Transaction()

        # Split str_cs by ";" but only those that are not inside quotes.

        #lstr_fields = str_csv.split(';')
        lstr_fields = next(csv.reader([str_csv], delimiter=';', quotechar='"'))

        # date
        str_date = lstr_fields[1]
        if len(str_date) > 0:
            tran.d_date = dateStrToDate(str_date)

        # description
        tran.str_description = lstr_fields[2]

        # Purchase date
        str_purchaseDate = lstr_fields[0]
        if len(str_purchaseDate) > 0:
            tran.d_purchaseDate = dateStrToDate(str_purchaseDate)

        # Amount out
        str_outAmount = lstr_fields[3].replace(',', '.')
        tran.f_amount = float(str_outAmount)

        return tran


l_csvProcessors = [
    CheckingCsvProcessor, OldCheckingCsvProcessor, OldCreditCardCsvProcessor,
    CreditCardCsvProcessor
]


class Transaction:
    """An object of this class describes a bank transaction."""

    # Pairs of (label, shortcut key)
    lstr_categoryLabels = [('FUN', 'f'), ('FOOD', 'o'), ('CAR', 'c'),
                           ('MUSIC', 'm'), ('HOME', 'h'), ('WORK', 'w')]
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
        self.fromAccount = ''  # str in order to hold an IBAN
        self.toAccount = ''  # str in order to hold an IBAN
        # Twin transactions are those with the same fields. This may happen e.g.
        # when buying two coffees in the same day at the same place. `twinInd`
        # indexes the twin transactions with the same fields. Thus, the first
        # coffee in the day has id 0, the second 1, etc. This field is 0 if the
        # transaction has no twin.
        self.twinInd = None

    def dateStrToDate(str_date):

        if not str_date[0].isdigit():
            print('str_date = ', str_date)
            raise TypeError('invalid format of time field')

        dt_out = date(year=int(str_date[6:10]),
                      month=int(str_date[3:5]),
                      day=int(str_date[0:2]))
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
        print('TWIN IND: ', self.twinInd)
        print('------------------------------')

    def __str__(self):
        return f"[{self.d_date},{self.str_account},{self.f_amount}] {self.str_description}"

    @staticmethod
    def setTwinInd(l_trans):
        """Sets the twinInd field of each transaction in l_transactions. 
        
        It is assumed that the oldest transaction has no twins out of those in
        `l_trans`. This will occur if the first day is complete, as it will
        typically occur when we download a CSV file. 
        """

        if len(l_trans) == 0:
            return

        # Sort the list so that twins are consecutive.
        l_trans = sorted(
            l_trans,
            key=lambda t:
            (t.d_date, t.str_description, t.f_amount, t.str_account))

        l_trans[0].twinInd = 0
        if len(l_trans) == 1:
            return

        # Compare each transaction with the previous one in the list.
        for indTransaction in range(1, len(l_trans)):
            if l_trans[indTransaction].equals(l_trans[indTransaction - 1],
                                              excludeTwinInd=True):
                l_trans[indTransaction].twinInd = l_trans[indTransaction -
                                                          1].twinInd + 1
                print('WARNING: twin transactions found:')
                l_trans[indTransaction].print()
            else:
                l_trans[indTransaction].twinInd = 0

    def readTransactionListFromCSVFile(ll_csv_files=ll_default_csv_files):

        def findCsvProcessor(str_format):
            for p in l_csvProcessors:
                if p.isMe(str_format):
                    return p

            raise ValueError(f"Unrecognized format {str_format}.")

        l_transactions = []

        for l_file in ll_csv_files:
            with open(l_file[0], 'r', encoding=l_file[1]) as input:

                str_format = input.readline()[
                    0:-1]  # first line gives the format

                p = findCsvProcessor(str_format)

                for myline in input:
                    tran = p.getTransactionFromString(myline)
                    if tran is None:
                        continue
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

    def combineListsOfTransactions(l_existing,
                                   l_possibly_new,
                                   skip_overlapping_time=True):
        """A list is created with the nodes of l_existing and the nodes in
        l_possibly new that are not in l_existing. """

        def inList(t, l_t):
            # Returns True iff transaction `t` is in the list `l_t`.
            return findInList(t, l_t) is not None

        def findInList(t, l_t):
            # Returns the first transaction in l_t that is equal to `t`.
            for refTrans in l_t:
                if t.equals(refTrans):
                    return refTrans
            return None

        if skip_overlapping_time:
            # Sometimes, a given transaction appears in `l_existing` and in
            # `l_possibly_new` with a different description. This is due to
            # changes in the export system used by the bank. Thus, counting
            # twins is not enough to avoid duplicates.
            #
            # What we do here is to remove transactions from `l_possibly_new`
            # whose date is before the last date in the sublist of l_existing
            # that contains transactions with the same str_account as
            # l_possibly_new.
            #
            # In this way, for each account, only the last day in l_existing
            # needs to be merged. This is needed as the last day of a csv file
            # may not be complete.

            # 1. Make a dict with the last day for each account in l_existing
            d_lastDate = {}
            for t in l_existing:
                if t.str_account not in d_lastDate:
                    d_lastDate[t.str_account] = t.d_date
                else:
                    if t.d_date > d_lastDate[t.str_account]:
                        d_lastDate[t.str_account] = t.d_date

            # 2. Remove transactions from l_possibly_new whose date is before
            # the last date for the corresponding account in l_existing.
            l_to_remove = []
            for t in l_possibly_new:
                if t.str_account in d_lastDate:
                    if t.d_date < d_lastDate[t.str_account]:
                        l_to_remove.append(t)
            for t in l_to_remove:
                l_possibly_new.remove(t)

            Transaction.setTwinInd(l_existing)
            Transaction.setTwinInd(l_possibly_new)

            # 3. Remove transactions from l_possibly_new that took place in the
            #    dates in d_lastDate and that are already in l_existing.
            l_to_remove = []
            for t in l_existing:
                if t.d_date == d_lastDate[t.str_account]:
                    # Two cases: l_possibly_new starts on day
                    # d_lastDate[t.str_account] for this account. In this case,
                    # t must be in l_possibly_new, since the first day of a CSV
                    # file is assumed complete.
                    t_match = findInList(t, l_possibly_new)
                    if t_match is None:
                        # In this case, if there are transactions in the same
                        # account and with the same date in l_possibly_new, it
                        # means that `t` is in l_possibly_new with a different
                        # description (or other field). Merging thus requires
                        # manual intervention.
                        for tpn in l_possibly_new:
                            if (tpn.d_date == t.d_date) and (tpn.str_account
                                                             == t.str_account):
                                print(
                                    f"Transaction T:={t}, already in the data base, is not "
                                    +
                                    "present in the data being imported, despite the latter "
                                    +
                                    "contains transactions for the date of the former and the same "
                                    + "account, namely:")
                                l_candidates = [
                                    tpn2 for tpn2 in l_possibly_new
                                    if (tpn2.d_date == t.d_date) and (
                                        tpn2.str_account == t.str_account)
                                ]
                                for ind in range(len(l_candidates)):
                                    print(f"{ind}: {l_candidates[ind]}")
                                print(
                                    "This means that either the imported files have an "
                                    +
                                    "incomplete first day, which is not allowed, or "
                                    +
                                    "transaction T is correspondso to one of the transactions "
                                    + "in the above list.")
                                ind_selected = input(
                                    f"Which one is the version of T? (enter 0-{len(l_candidates)-1})"
                                )
                                l_to_remove.append(
                                    l_candidates[int(ind_selected)])
                                break

                    else:
                        l_to_remove.append(t_match)
            for t in l_to_remove:
                l_possibly_new.remove(t)

            num_newTransactions = len(l_possibly_new)
            l_out = l_existing + l_possibly_new

        else:
            Transaction.setTwinInd(l_existing)
            Transaction.setTwinInd(l_possibly_new)

            l_out = [t for t in l_existing]
            num_newTransactions = 0
            for t in l_possibly_new:
                if not inList(t, l_out):
                    l_out.append(t)
                    num_newTransactions = num_newTransactions + 1

        print('new transactions = ', num_newTransactions)
        return Transaction.sortTransactionList(l_out)

    def sortTransactionList(l_transactions):

        l_transactions = sorted(l_transactions,
                                key=lambda transaction: transaction.d_date)

        return l_transactions

    def autoAssignTransactionsToCategory(l_transactions):

        def autoAssignTransactionToCategory(l_transactions,
                                            transactionToBeAssigned):
            """Assigns transaction to a category C if each transactions in
            <l_transactions> with the same description as <transaction> is
            assigned either to C or not assigned to any category."""

            if transactionToBeAssigned.str_category:
                return

            if transactionToBeAssigned.str_description == 'Universitetet i':
                print("checking for trans on  = ",
                      transactionToBeAssigned.d_date)

            # We finish the following loop with category = '' if there are no
            # transactions with the same description as <transactionToBeAssigned>
            # and different categories.
            category = ''
            for tran in l_transactions:
                if (not tran.str_category):
                    continue
                if tran.str_description == 'Universitetet i':
                    print("cat = ", tran.str_category)
                    if tran.str_category == 'WORK':
                        print("It is work")
                if tran.str_description == transactionToBeAssigned.str_description:
                    if (Transaction.isAutoCategory(tran.str_category)):
                        # We do not take into account automatically assigned categories
                        continue
                    # We arrive at this point if tran has a non-empty and
                    # non-auto category and the description of tran is the same
                    # as the description of transactionToBeAssigned.
                    #
                    if category:
                        if (category != tran.str_category):
                            return  # since there are two transactions with the
                            # same description as
                            # <transactionToBeAssigned> and they are
                            # assigned to different categories.
                    else:
                        category = Transaction.stripCategory(tran.str_category)

            if category:
                transactionToBeAssigned.str_category = Transaction.makeAutoCategory(
                    category)

        for transaction in l_transactions:
            if not transaction.str_category:
                autoAssignTransactionToCategory(l_transactions, transaction)

    def firstAndLastDates(l_transactions):

        if len(l_transactions) == 0:
            return date(2000, 1, 1), date(2000, 1, 1)

        firstDate = l_transactions[0].d_date
        lastDate = l_transactions[-1].d_date
        for transaction in l_transactions:
            if transaction.d_date < firstDate:
                firstDate = transaction.d_date
            if transaction.d_date > lastDate:
                lastDate = transaction.d_date

        return firstDate, lastDate

    def equals(self, refTrans, excludeTwinInd=False):
        """ Returns True if the main fields are equal.

        If `excludeTwinInd` is True, the twinInd field is not considered.

        """
        b_out_val = (self.d_date == refTrans.d_date) \
                   and (self.f_amount == refTrans.f_amount)\
                   and (self.str_description == refTrans.str_description)\
                    and (self.str_account == refTrans.str_account)\
                   and (excludeTwinInd or (hasattr(self,'twinInd') and hasattr(refTrans,'twinInd') and (self.twinInd == refTrans.twinInd)))

        if b_out_val:
            if not( (self.d_interestDate == refTrans.d_interestDate)\
                    and (self.d_purchaseDate == refTrans.d_purchaseDate)):
                print("There were changes in some fields")
        return b_out_val

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
                if dc_activeCategories[Transaction.stripCategory(
                        l_transactions[indTransaction].str_category)]:
                    l_transactionsFilteredByCategory[indTransaction] = True
                else:
                    l_transactionsFilteredByCategory[indTransaction] = False
            else:
                if dc_activeCategories['No Category']:
                    l_transactionsFilteredByCategory[indTransaction] = True
                else:
                    l_transactionsFilteredByCategory[indTransaction] = False

        return l_transactionsFilteredByCategory

    @staticmethod
    def makeAutoCategory(category):
        return category + ' [auto]'

    @staticmethod
    def stripCategory(category):
        """ Removes the [auto] part at the end of a category name"""
        return category.split(' [')[0]

    @staticmethod
    def isAutoCategory(category):
        return category[-6:] == '[auto]'

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
    @staticmethod
    def _setYaxisCommaFormatting():

        def with_commas(x, pos):
            return format(x, ",.0f")

        plt.gca().yaxis.set_major_formatter(FuncFormatter(with_commas))

    def plotCumsumOverTime(l_transactions):
        # ,
        #                   start_date_lim=None,
        #                   end_date_lim=None):
        # """
        # start_date_lim and end_date_lim are datetime.date objects that limit the
        # x-axis.

        # """

        # # Default start and end dates
        # if start_date_lim is None or end_date_lim is None:
        #     _start, _end = Transaction.firstAndLastDates(l_transactions)
        #     start_date_lim = _start if start_date_lim is None else start_date_lim
        #     end_date_lim = _end if end_date_lim is None else end_date_lim

        l_timeAxis = [None] * (len(l_transactions) + 1)
        l_timeAxis[0] = l_transactions[0].d_date
        l_total = [None] * (len(l_transactions) + 1)
        l_total[0] = 0
        for indTransaction in range(0, len(l_transactions)):
            l_total[indTransaction + 1] = l_total[
                indTransaction] + l_transactions[indTransaction].f_amount
            l_timeAxis[indTransaction +
                       1] = l_transactions[indTransaction].d_date

        dates = [d.strftime('%Y/%m/%d') for d in l_timeAxis]
        x = [dt.datetime.strptime(d, '%Y/%m/%d').date() for d in dates]
        y = l_total  # range(len(x)) # many thanks to Kyss Tao for setting me straight here

        Transaction._setYaxisCommaFormatting()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m/%d'))
        #plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.plot(x, y, marker='.')
        plt.gcf().autofmt_xdate()
        plt.grid()
        plt.title("Cumsum of the filtered transactions")
        plt.ylabel("Cumsum [NOK]")
        print("Total amount = ", l_total[-1])
        plt.show()
        return

    def plotMonthlySumsPerCategoryOverTime(l_transactions):

        # Find which categories exist in l_transactions
        l_cat = [t.str_category for t in l_transactions]
        l_cat = list(set(l_cat))
        l_cat = [Transaction.stripCategory(c) for c in l_cat]
        l_cat = list(set(l_cat))

        start_date, end_date = Transaction.firstAndLastDates(l_transactions)
        num_years = end_date.year - start_date.year + 1

        # Obtain totals per month
        def get_monthly_partials(l_transactions):
            l_totals = [[0] * 12 for _ in range(num_years)]
            for t in l_transactions:
                year = t.d_date.year - start_date.year
                month = t.d_date.month - 1
                l_totals[year][month] += t.f_amount

            return l_totals

        plt.figure(1)
        l_months = [
            date(year=year, month=month, day=1)
            for year in range(start_date.year, end_date.year + 1)
            for month in range(1, 13)
        ]

        for indCategory in range(0, len(l_cat)):
            l_transactions_now = [
                t for t in l_transactions if Transaction.stripCategory(
                    t.str_category) == l_cat[indCategory]
            ]
            l_partials = get_monthly_partials(l_transactions_now)
            plt.plot(l_months, [-t for y in l_partials for t in y],
                     marker='.',
                     label=l_cat[indCategory]
                     if l_cat[indCategory] else 'No Category')

        Transaction._setYaxisCommaFormatting()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y/%m'))
        plt.ylabel("Outgoing amount [NOK/month]")
        plt.title(l_cat[indCategory])
        plt.gcf().autofmt_xdate()
        plt.legend()
        plt.grid()

        plt.show()
