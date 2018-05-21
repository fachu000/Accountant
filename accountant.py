#  ACCOUNTANT 1.0
#
# PROGRAM TO KEEP PERSONAL ACCOUNTS
#
# NEXT STEPS:
# - Automatic classification of transactions into categories. If a transaction has the same description field as an already classified transaction, then it is assigned to the same category. If there already exist multiple classified transactions with the same description and different category, then the transaction at hand should not be automatically classified. 
# - add functionality to add comments to a transaction
#
# GRAPHICAL INTERFACE:
#     -On top: buttons to load/save Transaction lists or to read files
#     -Below: text boxes to specify filters (which transactions to display)
#     -Below: list of transactions that pass the filters
#     -Below: one button per category-- used to assign the selected event to a category. We can use a similar code as for readCalendar. 
#     -Below: buttons to plot, e.g. 
        # - balance vs time
        # - the amount of the filtered transactions vs time
#


# For Python + GTK, see:  https://python-gtk-3-tutorial.readthedocs.io/en/latest/introduction.html

########################################################################


########################################################################
    
        
########################################################################


from AccountantGUI import AccountantGUI

from Transaction import Transaction

###############################

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# win = Gtk.Window()
# win.connect("destroy", Gtk.main_quit)
# win.show_all()
# Gtk.main()

# quit()


# load default list
l_transactions = Transaction.loadTransactionList('../data/default.pk')

print('here we go')



win = AccountantGUI(l_transactions)
#win = AccountantGUI([])
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
quit()

#l_transactions = Transaction.sortTransactionList(l_transactions)

# for trans in l_transactions:
#     trans.print()

quit()
