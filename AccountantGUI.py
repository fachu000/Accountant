import numpy as np
from Transaction import Transaction
from datetime import datetime, timedelta, time, date

# When the ListStore is sorted by pressing a column header, the
# TreeIter that points to a row change as the row changes its
# position. Thus, to know what is the transaction in
# self.l_transactions associated with a certain row, we use the last
# column of the ListStore, which contains now the index.

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango

font_size = 18
treeview_height = 500


class AccountantGUI(Gtk.Window):

    def __init__(self, l_transactions, default_folder=None):

        self.default_folder = default_folder
        Transaction.checkList(l_transactions)
        self.l_transactions = l_transactions
        self.clearTransactionFilter()

        Gtk.Window.__init__(self, title="Accountant GUI")
        self.set_border_width(10)

        # box containing all
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.box)

        #Grid with the upper buttons
        def make_grid_with_upper_buttons():
            grid = Gtk.Grid()
            grid.set_column_homogeneous(True)
            grid.set_row_homogeneous(True)

            # Buttons
            saveButton = Gtk.Button('Save Transactions as')
            saveButton.connect("clicked", self.saveButtonCallback)
            loadButton = Gtk.Button('Load Transactions')
            loadButton.connect("clicked", self.loadButtonCallback)
            appendFromCSVFileButton = Gtk.Button('Append From CSV')
            appendFromCSVFileButton.connect(
                "clicked", self.appendFromCSVFileButtonCallback)
            autoAssignButton = Gtk.Button('Auto Assign')
            autoAssignButton.connect("clicked", self.autoAssignButtonCallback)
            addCommentButton = Gtk.Button('Add Comment')
            addCommentButton.connect("clicked", self.addCommentButtonCallback)

            grid.attach(saveButton, 0, 0, 2, 1)
            grid.attach(loadButton, 2, 0, 2, 1)
            grid.attach(appendFromCSVFileButton, 4, 0, 2, 1)
            grid.attach(autoAssignButton, 6, 0, 2, 1)
            grid.attach(addCommentButton, 8, 0, 2, 1)

            return grid

        self.grid = make_grid_with_upper_buttons()
        self.box.pack_start(self.grid, True, True, 0)

        def make_treeview():
            # TreeView  for transactions
            self.transaction_liststore = Gtk.ListStore(str, str, str, str, str,
                                                       str, str, str, str, int)
            self.fillTransactionListStore()

            self.transaction_treeview = Gtk.TreeView.new_with_model(
                self.transaction_liststore)
            self.select = self.transaction_treeview.get_selection()
            self.selectedTransactionTreeIter = None
            self.select.connect("changed", self.on_tree_selection_changed)

            for i, column_title in enumerate([
                    "Date", "Amount", "Category", "Description", "Account",
                    "Comment", "Purchase date", "Interest date", "Twin Index"
            ]):
                renderer = Gtk.CellRendererText()
                font_desc = Pango.FontDescription()
                font_desc.set_size(font_size *
                                   Pango.SCALE)  # Set font size to 12 points
                renderer.set_property("font-desc", font_desc)

                column = Gtk.TreeViewColumn(column_title, renderer, text=i)
                column.set_sort_column_id(i)
                self.transaction_treeview.append_column(column)

            transaction_scrollableTreelist = Gtk.ScrolledWindow()
            transaction_scrollableTreelist.set_vexpand(True)
            transaction_scrollableTreelist.add(self.transaction_treeview)
            transaction_scrollableTreelist.set_size_request(
                -1, treeview_height)
            return transaction_scrollableTreelist

        self.transaction_scrollableTreelist = make_treeview()
        #self.grid.attach(self.transaction_scrollableTreelist, 0, 1, 12, 10)
        self.box.pack_start(self.transaction_scrollableTreelist, True, True, 0)

        def make_grid_with_assignment_buttons():
            grid = Gtk.Grid()
            grid.set_column_homogeneous(True)
            grid.set_row_homogeneous(True)
            # buttons to assign transactions to categories
            self.l_categoryAssignmentButtons = list()
            for categoryLabel, shortcut_key in Transaction.lstr_categoryLabels:
                button = Gtk.Button(categoryLabel + ' (' + shortcut_key + ')')
                button.connect("clicked",
                               self.categoryAssignmentButtonCallback)
                self.l_categoryAssignmentButtons.append(button)

            num_cols = 500
            for i, button in enumerate(self.l_categoryAssignmentButtons[1:]):
                if i < num_cols:
                    grid.attach(button, 2 * i, 0, 2, 1)
                else:
                    self.grid.attach_next_to(
                        button, self.l_categoryAssignmentButtons[i - num_cols],
                        Gtk.PositionType.BOTTOM, 1, 1)
            return grid

        self.grid_with_assignment_buttons = make_grid_with_assignment_buttons()
        self.box.pack_start(self.grid_with_assignment_buttons, True, True, 0)

        ################# FILTER BOX #############################
        filterFrame = Gtk.Frame()
        self.filterBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                 spacing=6)
        self.box.pack_start(filterFrame, True, True, 0)
        filterFrame.add(self.filterBox)

        # Top row contains label and filter button
        self.filterBoxTopRow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                       spacing=6)
        self.filterBox.pack_start(self.filterBoxTopRow, True, True, 0)

        filteringLabel = Gtk.Label('Filtering Tools')
        self.filterBoxTopRow.pack_start(filteringLabel, True, True, 0)

        self.filterBox.filterButton = Gtk.Button(label="Filter")
        self.filterBox.filterButton.connect("clicked",
                                            self.filterButtonCallBack)
        self.filterBoxTopRow.pack_start(self.filterBox.filterButton, True,
                                        True, 0)

        # Row of category checkbuttons
        self.filterBoxCategoryRow = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.filterBox.pack_start(self.filterBoxCategoryRow, True, True, 0)

        self.filterBox.categoryCheckButtons = list()
        for str_cat, _ in Transaction.lstr_categoryLabels:
            cb = Gtk.CheckButton(str_cat)
            self.filterBox.categoryCheckButtons.append(cb)
            self.filterBoxCategoryRow.pack_start(cb, True, True, 0)
            cb.set_active(True)

        cb = Gtk.CheckButton('No Category')
        self.filterBox.categoryCheckButtons.append(cb)
        self.filterBoxCategoryRow.pack_start(cb, True, True, 0)
        cb.set_active(True)

        # Row with dates and description
        self.filterBoxDateRow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                        spacing=6)
        self.filterBox.pack_start(self.filterBoxDateRow, True, True, 0)

        self.calendarStartBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                        spacing=6)
        self.filterBoxDateRow.pack_start(self.calendarStartBox, True, True, 0)
        self.calendarStart = Gtk.Calendar()
        calendarStartLabel = Gtk.Label('From date:')
        self.calendarStartBox.pack_start(calendarStartLabel, True, True, 0)
        self.calendarStartBox.pack_start(self.calendarStart, True, True, 0)

        self.calendarEndBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                      spacing=6)
        self.filterBoxDateRow.pack_start(self.calendarEndBox, True, True, 0)
        self.calendarEnd = Gtk.Calendar()
        calendarEndLabel = Gtk.Label('To date:')
        self.calendarEndBox.pack_start(calendarEndLabel, True, True, 0)
        self.calendarEndBox.pack_start(self.calendarEnd, True, True, 0)
        self.resetCalendarDates()

        self.descriptionFilterBox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.filterBoxDateRow.pack_start(self.descriptionFilterBox, True, True,
                                         0)
        descriptionFilterLabel = Gtk.Label('Description contains words:')
        self.descriptionFilterBox.pack_start(descriptionFilterLabel, False,
                                             False, 0)
        self.descriptionFilterEntry = Gtk.Entry()
        self.descriptionFilterBox.pack_start(self.descriptionFilterEntry,
                                             False, False, 0)

        self.filterBox.accountCheckButtons = list()
        for str_accountLabel in Transaction.lstr_accountLabels:
            cb = Gtk.CheckButton(str_accountLabel)
            self.filterBox.accountCheckButtons.append(cb)
            self.descriptionFilterBox.pack_start(cb, True, True, 0)
            cb.set_active(True)

        ################# PLOT BOX #############################

        plotFrame = Gtk.Frame()
        self.box.pack_start(plotFrame, True, True, 0)
        self.plotBox = Gtk.Box(spacing=6)
        plotFrame.add(self.plotBox)

        plotLabel = Gtk.Label('Plot Filtered Transactions:')
        self.plotBox.pack_start(plotLabel, True, True, 0)

        plotCumsumButton = Gtk.Button('Plot Cumsum')
        plotCumsumButton.connect("clicked", self.plotCumsumButtonCallback)
        self.plotBox.pack_start(plotCumsumButton, True, True, 0)

        plotMonthlySumsPerCategoryButton = Gtk.Button(
            'Plot Monthly Sums Per Category')
        plotMonthlySumsPerCategoryButton.connect(
            "clicked", self.plotMonthlySumsPerCategoryButtonCallback)
        self.plotBox.pack_start(plotMonthlySumsPerCategoryButton, True, True,
                                0)

        self.show_all()

        ### keyboard shortcuts
        self.connect("key-press-event", self.on_key_press_event)

    def on_key_press_event(self, widget, event):
        """Note: Return true if you want to prevent the default callbacks from
        running. """
        # print("Key press on widget: ", widget)
        # print("          Modifiers: ", event.state)
        # print("      Key val, name: ", event.keyval,
        #       Gdk.keyval_name(event.keyval))

        if self.descriptionFilterEntry.is_focus():
            if event.keyval == Gdk.KEY_Return:
                self.filterButtonCallBack(self)
                return True
            else:
                return False  # the user is typing on the filter box

        for cat in Transaction.lstr_categoryLabels:
            if event.state & Gdk.ModifierType.CONTROL_MASK and event.keyval == Gdk.KEY_n:
                self.selectNextTransaction()
                return True
            if event.keyval == Gdk.keyval_from_name(cat[1]):
                self.assignSelectedTransactionToCategory(cat[0], auto=True)
                self.selectNextTransaction()
                return True

    def clearTransactionFilter(self):
        self.l_transactionsFiltered = [True] * len(self.l_transactions)

    def resetCalendarDates(self):
        firstDate, lastDate = Transaction.firstAndLastDates(
            self.l_transactions)
        self.calendarStart.select_day(firstDate.day)
        self.calendarStart.select_month(firstDate.month - 1, firstDate.year)
        self.calendarEnd.select_day(lastDate.day)
        self.calendarEnd.select_month(lastDate.month + 1, lastDate.year)

    def getFilteredTransactions(self):
        return [
            self.l_transactions[i] for i in range(len(self.l_transactions))
            if self.l_transactionsFiltered[i]
        ]

    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #
    # FUNCTIONS TO MANIPULATE THE LIST STORE
    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #

    def fillTransactionListStore(self):
        """Clears and fills the transaction ListStore."""

        self.transaction_liststore.clear()
        for transactionIndex, transaction in enumerate(self.l_transactions):
            """The last (not visible) column contains the index of the
            transaction in self.l_transactions. """
            if self.l_transactionsFiltered[transactionIndex]:
                row = AccountantGUI.transactionToStoreRowList(
                    transaction, transactionIndex)
                self.transaction_liststore.append(row)

    def updateStoreRows(self):
        for i_rowIndex in range(0, len(self.transaction_liststore)):
            self.updateStoreRow(i_rowIndex)

    def updateStoreRow(self, i_rowIndex):
        """Updates the i_rowIndex-th row of the table (not necessarily the
        i_rowIndex-th transaction)"""

        path = Gtk.TreePath.new_from_string(str(i_rowIndex))
        treeIter = self.transaction_liststore.get_iter(path)
        i_indTransaction = self.transaction_liststore[treeIter][
            -1]  # transaction
        # index
        # corresponding
        # to
        # that
        # row.
        rowList = AccountantGUI.transactionToStoreRowList(
            self.l_transactions[i_indTransaction], i_indTransaction)
        for colInd in range(0, len(rowList)):
            self.transaction_liststore[treeIter][colInd] = rowList[colInd]

    def transactionToStoreRowList(transaction, i_indexInList):
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
        str_amount = format(transaction.f_amount, ",.0f")
        str_category = transaction.str_category
        str_account = transaction.str_account
        str_comment = transaction.str_comment
        str_twinInd = str(transaction.twinInd) if hasattr(
            transaction, 'twinInd') else ''
        return [
            str_date, str_amount, str_category, str_description, str_account,
            str_comment, str_purchaseDate, str_interestDate, str_twinInd,
            i_indexInList
        ]

    def selectNextTransaction(self):
        """Moves the selection one step forward """

        selection = self.transaction_treeview.get_selection()

        # Get the model and currently selected iter
        model, current_iter = selection.get_selected()
        if not current_iter:
            # No current selection, return
            return

        # Get the next iter
        next_iter = model.iter_next(current_iter)
        if next_iter:
            selection.select_iter(next_iter)

    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #
    # CALLBACK FUNCTIONS
    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #    # # # #

    def saveButtonCallback(self, widget):

        dialog = Gtk.FileChooserDialog(
            "Please choose a .pk file", self, Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE,
             Gtk.ResponseType.OK))

        dialog.set_current_folder(self.default_folder)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("File selected: " + dialog.get_filename())
            Transaction.saveTransactionList(self.l_transactions,
                                            dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()
        print('now you save...')

    def loadButtonCallback(self, widget):

        dialog = Gtk.FileChooserDialog(
            "Please choose a .pk file", self, Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN,
             Gtk.ResponseType.OK))
        dialog.set_current_folder(self.default_folder)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            self.l_transactions = Transaction.loadTransactionList(
                dialog.get_filename())
            self.clearTransactionFilter()
            self.resetCalendarDates()
            self.fillTransactionListStore()

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        dialog.destroy()

    def appendFromCSVFileButtonCallback(self, widget):

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

        #l_transactions = Transaction.readTransactionListFromCSVFile(ll_files)
        l_transactions_CSV = Transaction.readTransactionListFromCSVFile()

        self.l_transactions = Transaction.combineListsOfTransactions(
            self.l_transactions, l_transactions_CSV)

        self.clearTransactionFilter()
        self.resetCalendarDates()
        self.fillTransactionListStore()

    def autoAssignButtonCallback(self, widget):

        Transaction.autoAssignTransactionsToCategory(self.l_transactions)

        self.updateStoreRows()

    def addCommentButtonCallback(self, widget):

        treeiter = self.selectedTransactionTreeIter
        if treeiter == None:
            return
        selectedTransactionIndex = self.transaction_liststore[treeiter][-1]

        dialog = addCommentDialog(
            self, self.l_transactions[selectedTransactionIndex].str_comment)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            print("Adding comment ", dialog.entry.get_text())
            self.l_transactions[
                selectedTransactionIndex].str_comment = dialog.entry.get_text(
                )
            self.updateStoreRows()

        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")

        dialog.destroy()

        return

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        # if treeiter is not None:
        #     print("You selected", model[treeiter][3])
        self.selectedTransactionTreeIter = treeiter

    def categoryAssignmentButtonCallback(self, widget):
        """This function sets the property str_category of the selected
        transaction to the value of the label of the button."""

        str_selectedCategory = widget.get_label().split(' ')[0]
        self.assignSelectedTransactionToCategory(str_selectedCategory,
                                                 auto=True)

    def getSelectedTransactionInd(self):
        """ Returns the index of the selected transaction. Note that this is 
        with respect to the entire list of transactions, not just the ones
        that pass the filter."""
        treeiter = self.selectedTransactionTreeIter
        if treeiter == None:
            return None
        # When we do [-1] in the next line, we are accessing the last column of
        # the ListStore, which is not visible but contains the index of the
        # transaction in self.l_transactions.
        selectedTransactionIndex = self.transaction_liststore[treeiter][-1]
        return selectedTransactionIndex

    def assignSelectedTransactionToCategory(self, str_category, auto=False):
        """
        If `auto` is True, then all transactions with the same description and
        without an assigned category are assigned `str_category`+ ' [auto]'.
        
        NOTE: str_category must be stripped, i.e., it must have no ' [auto]'

        """

        selectedTransactionIndex = self.getSelectedTransactionInd()
        if selectedTransactionIndex is None:
            return

        self.l_transactions[
            selectedTransactionIndex].str_category = str_category
        self.updateTransactionInListStore(selectedTransactionIndex)

        if auto:
            for ind_t, t in enumerate(self.l_transactions):
                if t.str_description == self.l_transactions[
                        selectedTransactionIndex].str_description and (
                            (t.str_category == '')
                            or Transaction.isAutoCategory(t.str_category)):
                    t.str_category = Transaction.makeAutoCategory(str_category)

                    # Update the list store if needed
                    self.updateTransactionInListStore(ind_t)

        #self.updateStoreRows()

    def updateTransactionInListStore(self, ind_t):
        """ 
        Args:

        `ind_t`: index of the transaction in self.l_transactions

        """
        if self.l_transactionsFiltered[ind_t]:
            ind_in_store_row = int(np.sum(self.l_transactionsFiltered[:ind_t]))
            if self.transaction_liststore[ind_in_store_row][-1] == ind_t:
                self.updateStoreRow(ind_in_store_row)
            else:
                # The place of the transaction has changed in the list store as
                # a result of column sorting. We need to find the new place of
                # the transaction in the list store.
                for ind_in_store_row in range(0,
                                              len(self.transaction_liststore)):
                    if self.transaction_liststore[ind_in_store_row][
                            -1] == ind_t:
                        self.updateStoreRow(ind_in_store_row)
                        break

    def plotCumsumButtonCallback(self, widget):

        Transaction.plotCumsumOverTime(self.getFilteredTransactions())

    def plotMonthlySumsPerCategoryButtonCallback(self, widget):

        #dc_activeCategories, dateStart, dateEnd, str_description, dc_activeAccounts = self.readFilterBox(

        Transaction.plotMonthlySumsPerCategoryOverTime(
            self.getFilteredTransactions())

    def filterTransactionList(self):
        dc_activeCategories, dateStart, dateEnd, str_description, dc_activeAccounts = self.readFilterBox(
        )

        # Filter by active categories
        l_transactionsFilteredByCategory = Transaction.filterByCategory(
            self.l_transactions, dc_activeCategories)

        # Filter by date interval
        l_transactionsFilteredByDate = Transaction.filterByDate(
            self.l_transactions, dateStart, dateEnd)

        # Filter by description
        l_transactionsFilteredByDescription = Transaction.filterByDescription(
            self.l_transactions, str_description)

        # Filter by account
        l_transactionsFilteredByAccount = Transaction.filterByAccount(
            self.l_transactions, dc_activeAccounts)

        # Combine filters
        l_transactionsFiltered = Transaction.listAnd(l_transactionsFilteredByCategory,\
                                                            l_transactionsFilteredByDate,\
                                                            l_transactionsFilteredByDescription,\
                                                            l_transactionsFilteredByAccount)
        self.l_transactionsFiltered = l_transactionsFiltered
        # return [
        #     l_transactions[i] for i in range(len(l_transactions))
        #     if l_transactionsFiltered[i]
        # ]

    def filterButtonCallBack(self, widget=None):
        self.filterTransactionList()
        self.fillTransactionListStore()
        print(
            f'Total of filtered transactions: {np.sum([t.f_amount for t,f in zip(self.l_transactions,self.l_transactionsFiltered) if f])}'
        )

    def readFilterBox(self):

        dc_activeCategories = {}  #[None]*len(Transaction.lstr_categoryLabels)
        for indCategory in range(0, len(self.filterBox.categoryCheckButtons)):
            dc_activeCategories[self.filterBox.categoryCheckButtons[indCategory].get_label()] = \
                self.filterBox.categoryCheckButtons[indCategory].get_active()

        (yearStart, monthStart, dayStart) = self.calendarStart.get_date()
        (yearEnd, monthEnd, dayEnd) = self.calendarEnd.get_date()
        dateStart = date(yearStart, monthStart + 1, dayStart)
        dateEnd = date(yearEnd, monthEnd + 1, dayEnd)

        str_description = self.descriptionFilterEntry.get_text()

        dc_activeAccounts = {}
        for indAccount in range(0, len(self.filterBox.accountCheckButtons)):
            dc_activeAccounts[self.filterBox.accountCheckButtons[indAccount].get_label()] = \
                self.filterBox.accountCheckButtons[indAccount].get_active()

        return dc_activeCategories, dateStart, dateEnd, str_description, dc_activeAccounts


#############################


class DialogExample(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "My Dialog", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 100)

        label = Gtk.Label("""
            Do you want to read the files checking.csv, savings.csv and
            creditCard.csv from the folder data/CSV?'
                          
            Note that the first day in the CSV files must contain all the
            transactions of that day. 
                          
            After that, you can use Auto Assign to assign categories based on
            previous assignments.
                          
                          """)

        box = self.get_content_area()
        box.add(label)
        self.show_all()

    def run(self):

        response = Gtk.Dialog.run(self)
        print('psssss')
        #        return (response,str_filename,str_format,str_account)
        return response


class addCommentDialog(Gtk.Dialog):

    def __init__(self, parent, str_defaultText):
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
