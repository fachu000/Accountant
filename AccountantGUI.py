

from Transaction import Transaction



import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class AccountantGUI(Gtk.Window):

    def __init__(self,l_transactions):

        Gtk.Window.__init__(self, title="Accountant GUI")
        self.set_border_width(10)
        self.l_transactions = l_transactions

        #Setting up the self.grid in which the elements are to be positioned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        # List store for transactions
        self.transaction_liststore = Gtk.ListStore(str, str, str,str,str,str,str,str)
        self.fillTransactionListStore()

        # Treeview for transactions
        self.transaction_treeview =   Gtk.TreeView.new_with_model(self.transaction_liststore)
        self.select = self.transaction_treeview.get_selection()
        self.selectedTransactionTreeIter = None
        self.select.connect("changed", self.on_tree_selection_changed)

        for i, column_title in enumerate(["Date", "Amount","Category", "Description","Account","Purchase date","Interest date","Comment"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.transaction_treeview.append_column(column)

        # # # List store for monthly hours
        # self.formMonthlyHours_liststore()

        # # Treeview for monthly hours
        # self.monthlyHours_treeview =   Gtk.TreeView.new_with_model(self.monthlyHours_liststore)

        # for i, column_title in enumerate(['Month']+Calendar.lstr_projectLabels + Calendar.lstr_genericProjectLabels + ['Total']):
        #     renderer = Gtk.CellRendererText()
        #     column = Gtk.TreeViewColumn(column_title, renderer, text=i)
        #     self.monthlyHours_treeview.append_column(column)

        #creating buttons to assign transactions to categories
        self.l_categoryAssignmentButtons = list()
        for categoryLabel in Transaction.lstr_categoryLabels:
            button = Gtk.Button(categoryLabel)
            self.l_categoryAssignmentButtons.append(button)
            button.connect("clicked",self.categoryAssignmentButtonCallback)

        # #creating buttons in top row
        saveButton = Gtk.Button('Save')
        saveButton.connect("clicked", self.saveButtonCallback)
        loadButton = Gtk.Button('Load')
        loadButton.connect("clicked", self.loadButtonCallback)
        appendFromCSVFileButton = Gtk.Button('Append From CSV')
        appendFromCSVFileButton.connect("clicked", self.appendFromCSVFileButtonCallback)
        autoAssignButton = Gtk.Button('Auto Assign')
        autoAssignButton.connect("clicked", self.autoAssignButtonCallback)
        printAssignmentsButton = Gtk.Button('Print Assignments')
        printAssignmentsButton.connect("clicked", self.printAssignmentsButtonCallback)


        #setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
        self.transaction_scrollableTreelist = Gtk.ScrolledWindow()
        self.transaction_scrollableTreelist.set_vexpand(True)
        # self.monthlyHours_scrollableTreelist = Gtk.ScrolledWindow()
        # self.monthlyHours_scrollableTreelist.set_vexpand(True)


        # Place widgets in the grid
        self.grid.attach( saveButton , 0, 0, 2, 1)
        self.grid.attach( loadButton , 2, 0, 2, 1)
        self.grid.attach( appendFromCSVFileButton , 4, 0, 2, 1)
        self.grid.attach( autoAssignButton , 6, 0, 2, 1)
        #self.grid.attach( printAssignmentsButton , 8, 0, 2, 1)
        self.grid.attach(self.transaction_scrollableTreelist, 0, 1, 12, 10)
        self.grid.attach_next_to(self.l_categoryAssignmentButtons[0], self.transaction_scrollableTreelist, Gtk.PositionType.BOTTOM, 1, 1)
        for i, button in enumerate(self.l_categoryAssignmentButtons[1:]):
            self.grid.attach_next_to(button, self.l_categoryAssignmentButtons[i], Gtk.PositionType.RIGHT, 1, 1)
        # self.grid.attach(self.monthlyHours_scrollableTreelist, 0, 12, 12, 10)
        self.transaction_scrollableTreelist.add(self.transaction_treeview)
#        self.monthlyHours_scrollableTreelist.add(self.monthlyHours_treeview)

        self.show_all()

    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #
    # FUNCTIONS TO MANIPULATE THE LIST STORE
    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #

    def fillTransactionListStore(self):
        
        for transactionIndex in range(0,len(self.l_transactions)):
            transaction =  self.l_transactions[transactionIndex]
            row = AccountantGUI.transactionToStoreRowList(transaction)
            self.transaction_liststore.append(row)

    def updateStoreRows(self):
        for i_rowIndex in range(0,len(self.l_transactions)):
            self.updateStoreRow(i_rowIndex)

    def updateStoreRow(self,i_rowIndex):
        """Updates the i_rowIndex-th row of the table"""

        rowList = AccountantGUI.transactionToStoreRowList(self.l_transactions[i_rowIndex])

        path = Gtk.TreePath.new_from_string(str(i_rowIndex))
        treeIter = self.transaction_liststore.get_iter(path)
        for colInd in range(0,len(rowList)):
            self.transaction_liststore[treeIter][colInd] = rowList[colInd]
                    
    def transactionToStoreRowList(transaction):
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
        return [str_date,str_amount,str_category,str_description,str_account,str_purchaseDate,str_interestDate,str_comment]

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
            self.transaction_liststore.clear()
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
        self.calendar.appendFromCSVFile()

        # Update event table
        for eventIndex in range(0,len(self.calendar.l_CalEvents)):
            self.updateStoreRow(eventIndex)
        # Update table of monthly events 
        self.updateMonthlyHours_liststore()


    def appendTransactionsFromDefaultCSVFiles(self):
        
        ll_files = [ ['../data/CSV/checking.csv', 'ISO-8859-1','CHECKING-NO' ],
                     ['../data/CSV/savings.csv', 'ISO-8859-1','SAVINGS-NO' ],
                     ['../data/CSV/creditCard.csv','UTF8','CREDIT_CARD-NO']]


        #l_transactions = Transaction.readTransactionListFromCSVFile(ll_files)
        l_transactions_CSV = Transaction.readTransactionListFromCSVFile(ll_files)

        num_newTransactions = Transaction.combineListsOfTransactions(self.l_transactions,l_transactions_CSV)
        print('new transactions = ',num_newTransactions)
        self.transaction_liststore.clear()
        self.fillTransactionListStore()




    def autoAssignButtonCallback(self,widget):

        Transaction.autoAssignTransactionsToCategory(self.l_transactions)

        self.updateStoreRows()


    def printAssignmentsButtonCallback(self,widget):

        self.calendar.printAssignments() 


    def on_tree_selection_changed(self,selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            print("You selected", model[treeiter][0])        
        self.selectedTransactionTreeIter = treeiter
#        print('path = ',type(self.selectedEventTreeIter))


    def categoryAssignmentButtonCallback(self, widget):
        """This function sets the property str_category of the selected
        transaction to the value of the label of the button."""  

        str_selectedCategory = widget.get_label()
        treeiter = self.selectedTransactionTreeIter
        if treeiter == None:
            return
        selectedTransactionIndex = self.transaction_liststore.get_path(treeiter).get_indices()[0]
        self.l_transactions[selectedTransactionIndex].str_category = str_selectedCategory
#        self.calendar.l_CalEvents[selectedEventIndex].print()
        self.updateStoreRow(selectedTransactionIndex)
        #self.calendar.printMonthlyHoursPerProject()
#        self.updateMonthlyHours_liststore()


#        self.events_liststore
        

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
