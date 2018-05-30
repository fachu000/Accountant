

from Transaction import Transaction
from datetime import datetime,timedelta,time,date

# When the ListStore is sorted by pressing a column header, the
# TreeIter that point to a row change as the row changes its
# position. Thus, to know what is the transaction in
# self.l_transactions associated with a certain row, we use the last
# column of the ListStore, which contains now the index.


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class AccountantGUI(Gtk.Window):

    def __init__(self,l_transactions):

        Gtk.Window.__init__(self, title="Accountant GUI")
        self.set_border_width(10)
        self.l_transactions = l_transactions
        self.l_transactionsFiltered = [True]*len(self.l_transactions)

        # box containing all
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        self.add(self.box)

        #Grid with the upper buttons
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.box.pack_start(self.grid, True, True, 0)

        saveButton = Gtk.Button('Save')
        saveButton.connect("clicked", self.saveButtonCallback)
        loadButton = Gtk.Button('Load')
        loadButton.connect("clicked", self.loadButtonCallback)
        appendFromCSVFileButton = Gtk.Button('Append From CSV')
        appendFromCSVFileButton.connect("clicked", self.appendFromCSVFileButtonCallback)
        autoAssignButton = Gtk.Button('Auto Assign')
        autoAssignButton.connect("clicked", self.autoAssignButtonCallback)
        addCommentButton = Gtk.Button('Add Comment')
        addCommentButton.connect("clicked", self.addCommentButtonCallback)

        self.grid.attach( saveButton , 0, 0, 2, 1)
        self.grid.attach( loadButton , 2, 0, 2, 1)
        self.grid.attach( appendFromCSVFileButton , 4, 0, 2, 1)
        self.grid.attach( autoAssignButton , 6, 0, 2, 1)
        self.grid.attach( addCommentButton , 8, 0, 2, 1)


        # TreeView  for transactions
        self.transaction_liststore = Gtk.ListStore(str, str, str,str,str,str,str,str,int)
        self.fillTransactionListStore()

        self.transaction_treeview =   Gtk.TreeView.new_with_model(self.transaction_liststore)
        self.select = self.transaction_treeview.get_selection()
        self.selectedTransactionTreeIter = None
        self.select.connect("changed", self.on_tree_selection_changed)

        for i, column_title in enumerate(["Date", "Amount","Category", "Description","Account","Comment","Purchase date","Interest date"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_sort_column_id(i)
            self.transaction_treeview.append_column(column)

        self.transaction_scrollableTreelist = Gtk.ScrolledWindow()
        self.transaction_scrollableTreelist.set_vexpand(True)
        self.transaction_scrollableTreelist.add(self.transaction_treeview)

        self.grid.attach(self.transaction_scrollableTreelist, 0, 1, 12, 10)

        # buttons to assign transactions to categories
        self.l_categoryAssignmentButtons = list()
        for categoryLabel in Transaction.lstr_categoryLabels:
            button = Gtk.Button(categoryLabel)
            self.l_categoryAssignmentButtons.append(button)
            button.connect("clicked",self.categoryAssignmentButtonCallback)


        self.grid.attach_next_to(self.l_categoryAssignmentButtons[0], self.transaction_scrollableTreelist, Gtk.PositionType.BOTTOM, 1, 1)
        for i, button in enumerate(self.l_categoryAssignmentButtons[1:]):
            self.grid.attach_next_to(button, self.l_categoryAssignmentButtons[i], Gtk.PositionType.RIGHT, 1, 1)

        ################# FILTER BOX #############################
        filterFrame = Gtk.Frame()
        self.filterBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        self.box.pack_start(filterFrame , True , True , 0)
        filterFrame.add(self.filterBox)

        # Top row contains label and filter button
        self.filterBoxTopRow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=6)
        self.filterBox.pack_start(self.filterBoxTopRow , True , True , 0)

        filteringLabel = Gtk.Label('Filtering Tools')
        self.filterBoxTopRow.pack_start(filteringLabel, True, True, 0)

        self.filterBox.filterButton = Gtk.Button(label="Filter")
        self.filterBox.filterButton.connect("clicked", self.filterButtonCallBack)
        self.filterBoxTopRow.pack_start(self.filterBox.filterButton, True, True, 0)
        
        # Row of category checkbuttons
        self.filterBoxCategoryRow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=6)
        self.filterBox.pack_start(self.filterBoxCategoryRow , True , True , 0)

        self.filterBox.categoryCheckButtons = list()
        for str_cat in Transaction.lstr_categoryLabels:
            cb = Gtk.CheckButton(str_cat)
            self.filterBox.categoryCheckButtons.append(cb)
            self.filterBoxCategoryRow.pack_start(cb, True, True, 0)
            cb.set_active(True)

        cb = Gtk.CheckButton('No Category')
        self.filterBox.categoryCheckButtons.append(cb)
        self.filterBoxCategoryRow.pack_start(cb, True, True, 0)
        cb.set_active(True)

        # Row with dates and description
        self.filterBoxDateRow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,spacing=6)
        self.filterBox.pack_start(self.filterBoxDateRow , True , True , 0)

        self.calendarStartBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        self.filterBoxDateRow.pack_start(self.calendarStartBox , True , True , 0)
        self.calendarStart = Gtk.Calendar()
        calendarStartLabel = Gtk.Label('From date:')
        self.calendarStartBox.pack_start(calendarStartLabel,True,True,0)
        self.calendarStartBox.pack_start(self.calendarStart,True,True,0)

        self.calendarEndBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        self.filterBoxDateRow.pack_start(self.calendarEndBox , True , True , 0)
        self.calendarEnd = Gtk.Calendar()
        calendarEndLabel = Gtk.Label('To date:')
        self.calendarEndBox.pack_start(calendarEndLabel,True,True,0)
        self.calendarEndBox.pack_start(self.calendarEnd,True,True,0)
        
        firstDate,lastDate = Transaction.firstAndLastDates(self.l_transactions)
        self.calendarStart.select_day(firstDate.day)
        self.calendarStart.select_month(firstDate.month-1,firstDate.year)
        self.calendarEnd.select_day(lastDate.day)
        self.calendarEnd.select_month(lastDate.month-1,lastDate.year)

        self.descriptionFilterBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
        self.filterBoxDateRow.pack_start(self.descriptionFilterBox,True,True,0)
        descriptionFilterLabel = Gtk.Label('Description contains words:')
        self.descriptionFilterBox.pack_start(descriptionFilterLabel,False,False,0)
        self.descriptionFilterEntry = Gtk.Entry()
        self.descriptionFilterBox.pack_start(self.descriptionFilterEntry,False,False,0)

        self.filterBox.accountCheckButtons = list()
        for str_accountLabel in Transaction.lstr_accountLabels:
            cb = Gtk.CheckButton(str_accountLabel)
            self.filterBox.accountCheckButtons.append(cb)
            self.descriptionFilterBox.pack_start(cb, True, True, 0)
            cb.set_active(True)


        ################# PLOT BOX #############################  

        plotFrame = Gtk.Frame()
        self.box.pack_start(plotFrame , True , True , 0)
        self.plotBox = Gtk.Box(spacing=6)
        plotFrame.add(self.plotBox)

        plotLabel = Gtk.Label('Plotting Tools')
        self.plotBox.pack_start(plotLabel,True,True,0)

        plotTotalButton = Gtk.Button('Plot Total')
        plotTotalButton.connect("clicked", self.plotTotalButtonCallback)
        self.plotBox.pack_start(plotTotalButton,True,True,0)

        plotTotalPerCategoryButton = Gtk.Button('Plot Total Per Category')
        plotTotalPerCategoryButton.connect("clicked", self.plotTotalPerCategoryButtonCallback)
        self.plotBox.pack_start(plotTotalPerCategoryButton,True,True,0)

        self.show_all()

    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #
    # FUNCTIONS TO MANIPULATE THE LIST STORE
    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #

    def fillTransactionListStore(self):
        """Clears and fills the transaction ListStore."""

        self.transaction_liststore.clear()
        for transactionIndex in range(0,len(self.l_transactions)):
            if not self.l_transactionsFiltered[transactionIndex]:
                continue
            transaction =  self.l_transactions[transactionIndex]
            row = AccountantGUI.transactionToStoreRowList(transaction,transactionIndex)
            self.transaction_liststore.append(row)

    def updateStoreRows(self):
        for i_rowIndex in range(0,len(self.transaction_liststore)):
            self.updateStoreRow(i_rowIndex)

    def updateStoreRow(self,i_rowIndex):
        """Updates the i_rowIndex-th row of the table (not necessarily the
        i_rowIndex-th transaction)"""

        path = Gtk.TreePath.new_from_string(str(i_rowIndex))
        treeIter = self.transaction_liststore.get_iter(path)
        i_indTransaction = self.transaction_liststore[treeIter][-1] # transaction
                                                                    # index
                                                                    # corresponding
                                                                    # to
                                                                    # that
                                                                    # row.
        rowList = AccountantGUI.transactionToStoreRowList(self.l_transactions[i_indTransaction],i_indTransaction)
        for colInd in range(0,len(rowList)):
            self.transaction_liststore[treeIter][colInd] = rowList[colInd]
                    
    def transactionToStoreRowList(transaction,i_indexInList):
        """Returns a list of strings. The n-th entry is the text to be
        displayed in the n-th column of the row corresponding to the
        Transaction <transaction>"""
        str_date = transaction.d_date.strftime('%Y/%m/%d')
        if transaction.d_purchaseDate:
            str_purchaseDate = transaction.d_purchaseDate.strftime('%Y/%m/%d')
        else:
            str_purchaseDate = ''
        if transaction.d_interestDate:
            str_interestDate = transaction.d_interestDate.strftime('%Y/%m/%d')
        else:
            str_interestDate = ''            
        str_description = transaction.str_description
        str_amount = str(transaction.f_amount)
        str_category = transaction.str_category
        str_account = transaction.str_account
        str_comment = transaction.str_comment
        return [str_date,str_amount,str_category,str_description,str_account,str_comment,str_purchaseDate,str_interestDate,i_indexInList]

    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #
    # CALLBACK FUNCTIONS
    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #

    def saveButtonCallback(self,widget):

        dialog = Gtk.FileChooserDialog("Please choose a .pk file", self,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("File selected: " + dialog.get_filename())
            Transaction.saveTransactionList(self.l_transactions,dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()
        print('now you save...')


    def loadButtonCallback(self,widget):

        dialog = Gtk.FileChooserDialog("Please choose a .pk file", self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            self.l_transactions = Transaction.loadTransactionList(dialog.get_filename())
            self.fillTransactionListStore()

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        dialog.destroy()


    def appendFromCSVFileButtonCallback(self,widget):

        dialog = DialogExample(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            print("Appending transactions from default CSV files.")
            self.appendTransactionsFromDefaultCSVFiles()
        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")

        dialog.destroy()

        return


    def appendTransactionsFromDefaultCSVFiles(self):
        
        ll_files = [ ['../data/CSV/checking.csv', 'ISO-8859-1','CHECKING-NO' ],
                     ['../data/CSV/savings.csv', 'ISO-8859-1','SAVINGS-NO' ],
                     ['../data/CSV/creditCard.csv','UTF8','CREDIT_CARD-NO']]


        #l_transactions = Transaction.readTransactionListFromCSVFile(ll_files)
        l_transactions_CSV = Transaction.readTransactionListFromCSVFile(ll_files)

        num_newTransactions = Transaction.combineListsOfTransactions(self.l_transactions,l_transactions_CSV)
        print('new transactions = ',num_newTransactions)
        self.fillTransactionListStore()




    def autoAssignButtonCallback(self,widget):

        Transaction.autoAssignTransactionsToCategory(self.l_transactions)

        self.updateStoreRows()


    def addCommentButtonCallback(self,widget):

        treeiter = self.selectedTransactionTreeIter
        if treeiter == None:
            return
        selectedTransactionIndex = self.transaction_liststore[treeiter][-1]

        dialog = addCommentDialog(self,self.l_transactions[selectedTransactionIndex].str_comment)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            print("Adding comment ",dialog.entry.get_text())
            self.l_transactions[selectedTransactionIndex].str_comment = dialog.entry.get_text()
            self.updateStoreRows()


        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")

        dialog.destroy()

        return

    # def printAssignmentsButtonCallback(self,widget):

    #     self.calendar.printAssignments()
        


    def on_tree_selection_changed(self,selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            print("You selected", model[treeiter][3])        
        self.selectedTransactionTreeIter = treeiter
#        print('path = ',type(self.selectedEventTreeIter))


    def categoryAssignmentButtonCallback(self, widget):
        """This function sets the property str_category of the selected
        transaction to the value of the label of the button."""  

        str_selectedCategory = widget.get_label()
        treeiter = self.selectedTransactionTreeIter
        if treeiter == None:
            return
#        selectedRowIndex = self.transaction_liststore.get_path(treeiter).get_indices()[0]
        selectedTransactionIndex = self.transaction_liststore[treeiter][-1]
#        print('here',self.transaction_liststore[treeiter][-1],self.transaction_liststore[treeiter][3])

#        self.l_transactions[selectedTransactionIndex].print()
        self.l_transactions[selectedTransactionIndex].str_category = str_selectedCategory
#        self.calendar.l_CalEvents[selectedEventIndex].print()
#        self.updateStoreRow(selectedRowIndex)
        self.updateStoreRows()
        #self.calendar.printMonthlyHoursPerProject()
#        self.updateMonthlyHours_liststore()


#        self.events_liststore
        


    def plotTotalButtonCallback(self,widget):

        Transaction.plotTotalOverTime(self.l_transactions)


    def plotTotalPerCategoryButtonCallback(self,widget):

        Transaction.plotTotalPerCategoryOverTime(self.l_transactions)


    def filterButtonCallBack(self,widget):

        # Filter by active categories
        l_activeCategories = {} #[None]*len(Transaction.lstr_categoryLabels)
        for indCategory in range(0,len(self.filterBox.categoryCheckButtons)):
            l_activeCategories[self.filterBox.categoryCheckButtons[indCategory].get_label()] = \
                self.filterBox.categoryCheckButtons[indCategory].get_active()

        l_transactionsFilteredByCategory = self.filterByCategory(l_activeCategories)

        # Filter by date interval
        (yearStart,monthStart,dayStart) = self.calendarStart.get_date()
        (yearEnd,monthEnd,dayEnd) = self.calendarEnd.get_date()

        l_transactionsFilteredByDate = self.filterByDate(date(yearStart,monthStart+1,dayStart),\
                                                         date(yearEnd,monthEnd+1,dayEnd))

        # Filter by description
        str_description = self.descriptionFilterEntry.get_text()
        l_transactionsFilteredByDescription = self.filterByDescription(str_description)

        # Filter by account
        dc_activeAccounts = {} 
        for indAccount in range(0,len(self.filterBox.accountCheckButtons)):
            dc_activeAccounts[self.filterBox.accountCheckButtons[indAccount].get_label()] = \
                self.filterBox.accountCheckButtons[indAccount].get_active()

        print('dc=',dc_activeAccounts)
        l_transactionsFilteredByAccount = self.filterByAccount(dc_activeAccounts)

        # Combine filters
        self.l_transactionsFiltered = AccountantGUI.listAnd(l_transactionsFilteredByCategory,\
                                                            l_transactionsFilteredByDate,\
                                                            l_transactionsFilteredByDescription,\
                                                            l_transactionsFilteredByAccount)


        print(self.l_transactionsFiltered)
        self.fillTransactionListStore()

    def filterByDate(self,d_start,d_end):
        l_transactionsFilteredByDate = [None]*len(self.l_transactions)

        for indTransaction in range(0,len(self.l_transactions)):

            if (self.l_transactions[indTransaction].d_date >= d_start ) \
               and (self.l_transactions[indTransaction].d_date <= d_end ) :
                l_transactionsFilteredByDate[indTransaction] = True
            else:
                l_transactionsFilteredByDate[indTransaction] = False

        return l_transactionsFilteredByDate




    def filterByAccount(self,dc_activeAccounts):

        l_transactionsFilteredByAccount = [None]*len(self.l_transactions)
        
        for indTransaction in range(0,len(self.l_transactions)):
            if self.l_transactions[indTransaction].str_account:
                if dc_activeAccounts[self.l_transactions[indTransaction].str_account]:
                    l_transactionsFilteredByAccount[indTransaction] = True
                else:
                    l_transactionsFilteredByAccount[indTransaction] = False
            else:
                l_transactionsFilteredByAccount[indTransaction] = False

        return l_transactionsFilteredByAccount


        

    def filterByCategory(self,l_activeCategories):

        l_transactionsFilteredByCategory = [None]*len(self.l_transactions)
        
        for indTransaction in range(0,len(self.l_transactions)):
            if self.l_transactions[indTransaction].str_category:
                if l_activeCategories[self.l_transactions[indTransaction].str_category]:
                    l_transactionsFilteredByCategory[indTransaction] = True
                else:
                    l_transactionsFilteredByCategory[indTransaction] = False
            else:
                if l_activeCategories['No Category']:
                    l_transactionsFilteredByCategory[indTransaction] = True
                else:
                    l_transactionsFilteredByCategory[indTransaction] = False

        return l_transactionsFilteredByCategory


    def filterByDescription(self,str_description):
        l_transactionsFilteredByDescription = [True]*len(self.l_transactions)

        if not str_description:
            return l_transactionsFilteredByDescription

        for indTransaction in range(0,len(self.l_transactions)):

            if str_description.upper() in self.l_transactions[indTransaction].str_description.upper():
                l_transactionsFilteredByDescription[indTransaction] = True
            else:
                l_transactionsFilteredByDescription[indTransaction] = False

            print('-------------')
            print(self.l_transactions[indTransaction].str_description)
            print(str_description)
            print(l_transactionsFilteredByDescription[indTransaction] )
        return l_transactionsFilteredByDescription


    def listAnd(*args):
        return [all(tuple) for tuple in zip(*args)]

#############################



class DialogExample(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "My Dialog", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)

        label = Gtk.Label('Do you want to read the files checking.csv, savings.csv' + ' and creditCard.csv from the folder data/CSV?')

        box = self.get_content_area()
        box.add(label)
        self.show_all()

    def run(self):

        response = Gtk.Dialog.run(self)
        print('psssss')
#        return (response,str_filename,str_format,str_account)
        return response


class addCommentDialog(Gtk.Dialog):

    def __init__(self, parent,str_defaultText):
        Gtk.Dialog.__init__(self, "Add a Comment", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)

        label = Gtk.Label('Please type the comment')

        box = self.get_content_area()
        box.add(label)

        self.entry = Gtk.Entry()
        self.entry.set_text(str_defaultText)
        box.pack_start(self.entry, True, True, 0)

        self.show_all()
