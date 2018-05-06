# Version 3
#   - Improvements for repeating events
# Version 2
#   - Events are objects of class CalEvent

# NEXT STEPS

# - filter -- show only the events corresponding to the selected projects
# - compute and display total hours this year relative to a standard
# schedule of 7.5 hours/day


# Important information:
# 
# The format of calendar files specifies time in terms of UTC. The
# local time in Central Europe is CET in winter (UTC +1) and CEST in
# summer (UTC+2). Note that some repeating events start in CET and end
# in CEST or viceversa.# - save and load assignment files; this means that these assignments overwrite
# those applied in the current session. For each event in the
# assignment file, find that event in the current calendar and modify
# its fields. NOTE: if we change the intervals of the displayed
# calendar, then some events in the assignment file may not be in the
# displayed calendar. If we only save the events in the displayed
# calendar, then the assignments in the file that do not correspond to
# any event in the displayed calendar will be lost. For this reason,
# the saved assignment file must contain BOTH the events in the current
# calendar, i.e. those in the selected interval, as well as the events
# out of the selected interval.

#
# Events that span the entire day ("all day") or multiple entire days
# do not have a field of the form "DTSTART:19700329T020000"; instead,
# they have a field of the form
# "DTSTART;VALUE=DATE:20170906". (similar for DTEND)
#
# iCalendar specification:  
#       The full range of calendar components specified by a
#       recurrence set is referenced by referring to just the "UID"
#       property value corresponding to the calendar component.  The
#       "RECURRENCE-ID" property allows the reference to an individual
#       instance within the recurrence set.
# So, when you modify a repeated event, what happens is that another event is created with the same UID and where RECURRENCE-ID is the original DTSTART.

# If one day we want to include the functionality of writing iCalendar
# files, take into account that whole-day events are ignored here.
# 


# For Python + GTK, see:  https://python-gtk-3-tutorial.readthedocs.io/en/latest/introduction.html

########################################################################


########################################################################


from AmsterdamTime import AmsterdamTime, UTC
from datetime import datetime,timedelta,time,date
from Calendar import Calendar,CalEvent

###############################


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class CalendarWindow(Gtk.Window):

    def __init__(self,calendar,d_startDate,d_endDate):
        Gtk.Window.__init__(self, title="Assignment of hours to projects")
        self.set_border_width(10)
        self.calendar = calendar
        self.d_startDate = d_startDate
        self.d_endDate = d_endDate
        self.l_unusedAssignments = []

        #Setting up the self.grid in which the elements are to be positionned
        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        # List store for calendar events
        self.events_liststore = Gtk.ListStore(str, str, str,str,str)
        for eventIndex in range(0,len(self.calendar.l_CalEvents)):
            event =  self.calendar.l_CalEvents[eventIndex]
            row = CalendarWindow.eventToStoreRowList(event)
            self.events_liststore.append(row)

        # Treeview for calendar events
        self.events_treeview =   Gtk.TreeView.new_with_model(self.events_liststore)
        self.select = self.events_treeview.get_selection()
        self.selectedEventTreeIter = None
        self.select.connect("changed", self.on_tree_selection_changed)

        for i, column_title in enumerate(["Date", "Start", "Dur","Proj","Summary"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.events_treeview.append_column(column)

        # # List store for monthly hours
        self.formMonthlyHours_liststore()

        # Treeview for monthly hours
        self.monthlyHours_treeview =   Gtk.TreeView.new_with_model(self.monthlyHours_liststore)

        for i, column_title in enumerate(['Month']+Calendar.lstr_projectLabels + Calendar.lstr_genericProjectLabels + ['Total']):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.monthlyHours_treeview.append_column(column)

        #creating buttons to assign events to projects
        self.l_projectAssignmentButtons = list()
        for projectLabel in Calendar.lstr_projectLabels:
            button = Gtk.Button(projectLabel)
            self.l_projectAssignmentButtons.append(button)
            button.connect("clicked",
            self.projectAssignmentButtonCallback)

        #creating buttons in top row
        saveButton = Gtk.Button('Save Assignments')
        saveButton.connect("clicked", self.saveButtonCallback)
        loadButton = Gtk.Button('Load Assignments')
        loadButton.connect("clicked", self.loadButtonCallback)
        readProjectLabelsButton = Gtk.Button('Read Labels')
        readProjectLabelsButton.connect("clicked", self.readProjectLabelsButtonCallback)
        autoAssignButton = Gtk.Button('Auto Assign')
        autoAssignButton.connect("clicked", self.autoAssignButtonCallback)
        printAssignmentsButton = Gtk.Button('Print Assignments')
        printAssignmentsButton.connect("clicked", self.printAssignmentsButtonCallback)


        #setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
        self.events_scrollableTreelist = Gtk.ScrolledWindow()
        self.events_scrollableTreelist.set_vexpand(True)
        self.monthlyHours_scrollableTreelist = Gtk.ScrolledWindow()
        self.monthlyHours_scrollableTreelist.set_vexpand(True)


        # Place widgets in the grid
        self.grid.attach( saveButton , 0, 0, 2, 1)
        self.grid.attach( loadButton , 2, 0, 2, 1)
        self.grid.attach( readProjectLabelsButton , 4, 0, 2, 1)
        self.grid.attach( autoAssignButton , 6, 0, 2, 1)
        self.grid.attach( printAssignmentsButton , 8, 0, 2, 1)
        self.grid.attach(self.events_scrollableTreelist, 0, 1, 12, 10)
        self.grid.attach_next_to(self.l_projectAssignmentButtons[0], self.events_scrollableTreelist, Gtk.PositionType.BOTTOM, 1, 1)
        for i, button in enumerate(self.l_projectAssignmentButtons[1:]):
            self.grid.attach_next_to(button, self.l_projectAssignmentButtons[i], Gtk.PositionType.RIGHT, 1, 1)
        self.grid.attach(self.monthlyHours_scrollableTreelist, 0, 12, 12, 10)
        self.events_scrollableTreelist.add(self.events_treeview)
        self.monthlyHours_scrollableTreelist.add(self.monthlyHours_treeview)

        self.show_all()

    def saveButtonCallback(self,widget):

        dialog = Gtk.FileChooserDialog("Please choose a file", self,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("File selected: " + dialog.get_filename())
            CalEvent.saveAssignmentsToFile(self.calendar.l_CalEvents+self.l_unusedAssignments,dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

        print('now you save...')


    def formMonthlyHours_liststore(self):
        #l_types = [str,str, str,str,str,str,str,str,str,str,str,str,str,str]
        l_types = [str]*(len(Calendar.lstr_projectLabels + Calendar.lstr_genericProjectLabels)+2)
        liststore = Gtk.ListStore(*l_types)
        ld_monthlyHours = self.calendar.computeMonthlyHoursPerProject()
        for monthInd in range(0,len(ld_monthlyHours)):
            dic_row =  ld_monthlyHours[monthInd]
            lstr_row = self.monthlyHoursToStoreList(dic_row,monthInd)
            liststore.append(lstr_row)

        # Row of total hours
        d_totalHoursPerProject = self.calendar.sumMonthlyHoursPerProject()
        lf_totalHoursPerProject =  [d_totalHoursPerProject[str_proj] for str_proj in Calendar.lstr_projectLabels + Calendar.lstr_genericProjectLabels]

        liststore.append(['TOTAL']+[str(hours) for hours in lf_totalHoursPerProject] +[str(sum(lf_totalHoursPerProject))])

        # Row of project plan fractions
        liststore.append(self.formRowWorkPlanFractions(lf_totalHoursPerProject))

        self.monthlyHours_liststore = liststore
        return

    def formRowWorkPlanFractions(self,lf_totalHoursPerProject):

        lstr_fractions = [];
        lstr_allLabels = Calendar.lstr_projectLabels + Calendar.lstr_genericProjectLabels
        for ind_project in range(0,len(lstr_allLabels)):
            if lstr_allLabels[ind_project] in Calendar.d_workPlan:
                lstr_fractions = lstr_fractions + ["%.2f" % (lf_totalHoursPerProject[ind_project]/Calendar.d_workPlan[lstr_allLabels[ind_project]])]
            else:
                lstr_fractions = lstr_fractions + ['']

        return ['FRAC. WPLAN']+lstr_fractions+['']


    def updateMonthlyHours_liststore(self):

        ld_monthlyHours = self.calendar.computeMonthlyHoursPerProject()
        # Update month rows
        for monthInd in range(0,len(ld_monthlyHours)):

            path = Gtk.TreePath.new_from_string(str(monthInd))
            treeIter = self.monthlyHours_liststore.get_iter(path)
            dic_row =  ld_monthlyHours[monthInd]
            lstr_row = self.monthlyHoursToStoreList(dic_row,monthInd)

            for colInd in range(0,len(lstr_row)):
                self.monthlyHours_liststore[treeIter][colInd] = lstr_row[colInd]

        # Update row of totals
        path = Gtk.TreePath.new_from_string(str(len(ld_monthlyHours)))
        treeIter = self.monthlyHours_liststore.get_iter(path)

        d_totalHoursPerProject = self.calendar.sumMonthlyHoursPerProject()
        lf_totalHoursPerProject =  [d_totalHoursPerProject[str_proj] for str_proj in Calendar.lstr_projectLabels + Calendar.lstr_genericProjectLabels]

        lstr_row = ['TOTAL']+[str(hours) for hours in lf_totalHoursPerProject] +[str(sum(lf_totalHoursPerProject))]

        for colInd in range(0,len(lstr_row)):
            self.monthlyHours_liststore[treeIter][colInd] = lstr_row[colInd]

        # Update row of Work plan fractions
        path = Gtk.TreePath.new_from_string(str(len(ld_monthlyHours)+1))
        treeIter = self.monthlyHours_liststore.get_iter(path)
        lstr_fractions = self.formRowWorkPlanFractions(lf_totalHoursPerProject)
        for colInd in range(0,len(lstr_fractions)):
            self.monthlyHours_liststore[treeIter][colInd] = lstr_fractions[colInd]



        return

    def monthlyHoursToStoreList(self,dic_row,monthInd):
        l_entireMonths = self.calendar.getListOfEntireMonths()
        str_month = l_entireMonths[monthInd].strftime('%Y/%m')
        #        return [str_month]+[str(dic_row[str_proj]) for str_proj in Calendar.lstr_projectLabels + Calendar.lstr_genericProjectLabels]
        lf_hoursPerProject =  [dic_row[str_proj] for str_proj in Calendar.lstr_projectLabels + Calendar.lstr_genericProjectLabels]
        
        return [str_month]+ [str(hours) for hours in lf_hoursPerProject] +[str(sum(lf_hoursPerProject))]


    def loadButtonCallback(self,widget):

        dialog = Gtk.FileChooserDialog("Please choose a file", self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            self.l_unusedAssignments =  self.l_unusedAssignments  \
                                        + CalEvent.loadAssignmentsFromFile(self.calendar.l_CalEvents,
                                        dialog.get_filename(),self.d_startDate,self.d_endDate)
            for eventIndex in range(0,len(self.calendar.l_CalEvents)):
                self.updateStoreRow(eventIndex)

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        dialog.destroy()
        self.updateMonthlyHours_liststore()

    def readProjectLabelsButtonCallback(self,widget):
        self.calendar.readProjectLabels()

        # Update event table
        for eventIndex in range(0,len(self.calendar.l_CalEvents)):
            self.updateStoreRow(eventIndex)
        # Update table of monthly events 
        self.updateMonthlyHours_liststore()

    def autoAssignButtonCallback(self,widget):

        self.calendar.autoAssignEvents()
        # Update event table
        for eventIndex in range(0,len(self.calendar.l_CalEvents)):
            self.updateStoreRow(eventIndex)
        # Update table of monthly events 
        self.updateMonthlyHours_liststore()

    def printAssignmentsButtonCallback(self,widget):

        self.calendar.printAssignments() 


    def on_tree_selection_changed(self,selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            print("You selected", model[treeiter][0])        
        self.selectedEventTreeIter = treeiter
#        print('path = ',type(self.selectedEventTreeIter))


    def projectAssignmentButtonCallback(self, widget):
        """This function sets the property str_project of the selected
        event to the value of the label of the button."""  

        str_selectedProject = widget.get_label()
        treeiter = self.selectedEventTreeIter
        if treeiter == None:
            return
        selectedEventIndex = self.events_liststore.get_path(treeiter).get_indices()[0]
        self.calendar.l_CalEvents[selectedEventIndex].str_project = str_selectedProject
        self.calendar.l_CalEvents[selectedEventIndex].print()
        self.updateStoreRow(selectedEventIndex)
        #self.calendar.printMonthlyHoursPerProject()
        self.updateMonthlyHours_liststore()

    def eventToStoreRowList(event):
        """Returns a list of strings. The n-th entry is the text to be
        displayed in the n-th column of the row corresponding to the
        event <event>"""
        str_date = event.dt_start.astimezone(tz=UTC()).strftime('%Y/%m/%d')
        str_startTime =  event.dt_start.astimezone(tz=UTC()).strftime('%H:%M')
        str_duration = ':'.join(str(event.duration()).split(':')[:2])
        return [str_date,str_startTime,str_duration,event.str_project,event.str_summary]

    def updateStoreRow(self,i_rowIndex):
        """Updates the i_rowIndex-th row of the table"""
        path = Gtk.TreePath.new_from_string(str(i_rowIndex))
        treeIter = self.events_liststore.get_iter(path)
        rowList = CalendarWindow.eventToStoreRowList(self.calendar.l_CalEvents[i_rowIndex])

        for colInd in range(0,len(rowList)):
            self.events_liststore[treeIter][colInd] = rowList[colInd]
                    
#        self.events_liststore
        

#############################


# str_fileName ='data/caltest.txt'
# str_fileName ='data/calfull2.ics'
str_fileName ='data/calfull3.ics'
# str_fileName = 'data/new_test_calendar2.ics'

l_rawCalEvents = CalEvent.readNodeList(str_fileName)

# for it_ce in l_CalEvents:
#     it_ce.print()

d_startDate = date(2018,1,1)
d_endDate = date(2018,4,1) # excluded 

cal = Calendar(l_rawCalEvents,d_startDate,d_endDate)

cal.print()

# Print daily totals
# print('DATE          HOURS')
# for d_date in Calendar.dateRange(d_startDate,d_endDate):
#     td_totalHours = cal.computeTotalHours(d_date)
#     print(d_date,'  ',td_totalHours)



print('ooooooooooooooooooo')
l_entireMonths = cal.getListOfEntireMonths()
for d_date in l_entireMonths:
    print(d_date)
print('ooooooooooooooooooo')

cal.printMonthlyHoursPerProject()


#l_CalEvents = cal.getListOfEvents()

# print('=================')
# for it_ce in l_CalEvents:
#     it_ce.print()
# print('=================')

# no comment


# Graphical interface

win = CalendarWindow(cal,d_startDate,d_endDate)
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
quit()




