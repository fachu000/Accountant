
from AmsterdamTime import AmsterdamTime, UTC
from datetime import datetime,timedelta,time,date
import copy
import pickle

class Calendar:
    """Objects of this class contain a list of CalEvents for each day"""

    lstr_projectLabels = ['PET','SFI','WIS','IND','LUC','TEA','ORG','EXP','REV','FUT']
    # Project plan: for assignment of generic labels to project labels
    d_workPlan =    {'PET':220,'SFI':200,'WIS':340 ,'IND':270}
#    lstr_genericProjectLabels = ['PET','SFI','WIS','IND','LUC','TEA','ORG','EXP','REV','FUT','ALL','NET','email']
    lstr_genericProjectLabels = ['ALL','NET','email','SFI-PET','PAP']
    dl_labelCorrespondence = {'ALL':['PET','SFI','WIS','IND'],'NET':['PET','SFI','IND'],
                              'email':['PET','SFI','WIS','IND'],'SFI-PET':['PET','SFI'],
                              'PAP':['PET','SFI','WIS','IND']}
    

    def __init__(self,l_CalEvents,d_startDate,d_endDate):
        """With the CalEvents in the list l_CalEvents, this constructor forms
        a list of lists called self.ll_CalEvents, where the n-th list
        contains the CalEvents corresponding to the events in the n-th
        day. The 0-th day is CalEvents.d_startDate.

        """ 

        l_CalEvents = CalEvent.expandRepeatingEvents(l_CalEvents) 
        l_CalEvents = CalEvent.splitAtMidnight(l_CalEvents)
        # So far we have considered all events in the input list l_CalEvents. This is necessary due to repeating events.
        # From now on, only those days between d_startDate and d_endDate will be considered.
        self.d_startDate = d_startDate
        self.d_endDate = d_endDate
        self.l_CalEvents = self.obtainEventsInInterval(l_CalEvents)

        # self.ll_CalEvents is a list of lists of indices of events
        # inside self.l_CalEvents
        self.ll_CalEvents =  self.ll_CalEvents_from_l_CalEvents(self.l_CalEvents)
        self.ensureNoOverlappingEvents()

        # Sort the list l_CalEvents and update the indices in ll_CalEvents
        self.l_CalEvents = self.l_CalEvents_from_ll_CalEvents()
        self.ll_CalEvents =  self.ll_CalEvents_from_l_CalEvents(self.l_CalEvents)
        #        self.confineToDateInterval(self.d_startDate,self.d_endDate)


    def l_CalEvents_from_ll_CalEvents(self):
        
        new_l_CalEvents = []
        for dayList in self.ll_CalEvents:
            if dayList:
                for eventInd in dayList:
                    new_l_CalEvents = new_l_CalEvents + [self.l_CalEvents[eventInd]]

        return new_l_CalEvents
            

    def obtainEventsInInterval(self,l_CalEventsIn):
        """returns a list with the events in l_CalEvents that take
        place (on self.d_startDate or after) AND (before
        self.d_endDate). Note the date self.d_endDate is excluded.""" 
        l_CalEventsOut = []
        for event in l_CalEventsIn:
            i_dayRelInd = self.dateToDayIndex(event.dt_start.date()) 
            if (i_dayRelInd >= 0)& (i_dayRelInd < self.dateToDayIndex( self.d_endDate )): 
                l_CalEventsOut.append(event)

        return(l_CalEventsOut)


    def  getListOfEntireMonths(self):
        """List of dates of the 1st of each month that is completely 
        contained between self.d_startDate and self.d_endDate"""
        if self.d_startDate.day == 1:
            l_entireMonths = [self.d_startDate]
        else:
            l_entireMonths = []

        d_date = Calendar.firstDayOfNextMonth(self.d_startDate)
        while Calendar.firstDayOfNextMonth(d_date).toordinal() <= self.d_endDate.toordinal()+1:
            l_entireMonths.append(d_date)
            d_date = Calendar.firstDayOfNextMonth(d_date)
    
        return l_entireMonths
        
    def firstDayOfNextMonth(d_date):
        """returns the first day of the month right after the month of d_date"""
        if d_date.day<20:
            d_dayNextMonth = date.fromordinal( d_date.toordinal() + 31 )
        else:
            d_dayNextMonth = date.fromordinal( d_date.toordinal() + 15 )

        return date(d_dayNextMonth.year,d_dayNextMonth.month,1)

# this method should disappear
    def getListOfEvents(self):
        """Returns a list that contains (in a single dimension) the 
        events in self.ll_CalEvents""" 

        return self.l_CalEvents
        # l_CalEvents = []
        # for ind in range(0,len(self.ll_CalEvents)):
        #     if self.ll_CalEvents[ind]:
        #         l_CalEvents = l_CalEvents + self.ll_CalEvents[ind]




    def dateToDayIndex(self,d_date):
        """Returns the index of the day to which d_date corresponds. 0
        is the index of the 1st day of the calendar, i.e.,
        self.d_startDate"""
        return d_date.toordinal() - self.d_startDate.toordinal()

    def dayIndexToDate(self,i_ind):
        """Returns the date corresponding to the day with index i_ind"""
        return date.fromordinal(self.d_startDate.toordinal() + i_ind)

            
    def ll_CalEvents_from_l_CalEvents(self,l_CalEvents):
        ll_CalEvents = [None]*self.dateToDayIndex( self.d_endDate )
        for eventInd,event in enumerate(l_CalEvents):
            dayInd = self.dateToDayIndex(event.dt_start.date()) 
            if dayInd < 0:
                print('ERROR: event out of bounds')
                quit()
            elif dayInd >= len(ll_CalEvents):
                print('ERROR: event out of bounds')
                quit()
            elif ll_CalEvents[dayInd]==None:
                ll_CalEvents[dayInd]=[eventInd]
            else:
                ll_CalEvents[dayInd].append(eventInd)
        return(ll_CalEvents)

    def sortDays(self):
        """Sorts the events within each day"""
        for i_day in range(0,len(self.ll_CalEvents)-1):
            if self.ll_CalEvents[i_day] != None:
                self.ll_CalEvents[i_day] = sorted(self.ll_CalEvents[i_day],key=lambda ind:self.l_CalEvents[ind].dt_start)

    def ensureNoOverlappingEvents(self):
        """produces a warning if there are distinct overlapping events"""
        self.sortDays()
        for i_day in range(0,len(self.ll_CalEvents)-1):
            if self.ll_CalEvents[i_day] != None:
                for i_eventTodayInd in range(0,len(self.ll_CalEvents[i_day])-1):
                    evt1Ind = self.ll_CalEvents[i_day][i_eventTodayInd]
                    evt2Ind = self.ll_CalEvents[i_day][i_eventTodayInd+1]
                    evt1 = self.l_CalEvents[evt1Ind]
                    evt2 = self.l_CalEvents[evt2Ind]

                    if evt1.dt_end > evt2.dt_start:
                        print('---> WARNING: the following events are overlapping')
                        evt1.print()
                        evt2.print()
                        wait = input("PRESS ENTER TO CONTINUE.")

    # def confineToDateInterval(self,d_start,d_end):
    #     """Modifies the calendar by removing all the events whose dates are
    #     not between d_start and d_end; note that events whose date
    #     equals d_end are excluded.

    #     """

    #     ind_start = self.dateToDayIndex(d_start)
    #     ind_end = self.dateToDayIndex(d_end)

    #     print('u ',ind_start,' to ',ind_end)

    #     self.ll_CalEvents = self.ll_CalEvents[ind_start:ind_end]
    #     self.d_startDate = d_start
        
    #     return

    def computeTotalHours(self,d_date):
        """Returns a timedelta corresponding to the sum of the
        duration of the events in the day indicated by the date
        d_date""" 
        
        i_ind = self.dateToDayIndex(d_date)
        if (i_ind<0)|(i_ind>=len(self.ll_CalEvents)):
            print('ERROR: the date does not belong to the calendar')
            quit()
                    

        td_totalHours = timedelta(0)
        if self.ll_CalEvents[i_ind]:
            l_events = [self.l_CalEvents[i] for i in self.ll_CalEvents[i_ind]]
            if l_events:
                for event in l_events:
                    td_totalHours = td_totalHours + event.duration()

        return td_totalHours

    def print(self):
        for i_day in range(0,len(self.ll_CalEvents)):
            if self.ll_CalEvents[i_day] != None:
                print('=== Day ',self.dayIndexToDate(i_day),' ===')
                for event in [self.l_CalEvents[i] for i in self.ll_CalEvents[i_day]]:
                    event.print()
        
    def dateRange(start_date, end_date):
        for ordinal in range(start_date.toordinal(), end_date.toordinal()):
            yield date.fromordinal(ordinal)


    def computeMonthlyHoursPerProject(self):
        """Returns a list of dictionaries. There is a dictionary per
        month. Each dictionary has an entry per project, and that
        entry indicates the number of hours spent in that project in
        the corresponding month"""

        l_entireMonths = self.getListOfEntireMonths()
        
        d_zeroHours = {str_proj:0 for str_proj in (Calendar.lstr_projectLabels + Calendar.lstr_genericProjectLabels)}
        ld_monthlyHours = [copy.copy(d_zeroHours) for r in range(0,len(l_entireMonths))]
        for event in self.l_CalEvents:
            if event.str_project:
                # obtain first day of the month of the event
                month = date(event.dt_start.year,event.dt_start.month,1)
                # find that day in l_entireMonths
                indMonth = l_entireMonths.index(month)
                # increase the corresponding entry of ld_monthly hours
                ld_monthlyHours[indMonth][event.str_project] =    \
                    ld_monthlyHours[indMonth][event.str_project] +  (event.duration().seconds)/3600
        
        return ld_monthlyHours


    def sumMonthlyHoursPerProject(self):
        """Returns a dictionary which has an entry per project that 
        indicates the total number of hours in the considered months.""" 
        ld_monthlyHours = self.computeMonthlyHoursPerProject()
        d_totalHours = {str_proj:0 for str_proj in (Calendar.lstr_projectLabels + Calendar.lstr_genericProjectLabels)}
        for d_month in ld_monthlyHours:
            for str_proj in (Calendar.lstr_projectLabels + Calendar.lstr_genericProjectLabels):
                d_totalHours[str_proj] = d_totalHours[str_proj] + d_month[str_proj]
        return d_totalHours


    def printMonthlyHoursPerProject(self):

        ld_monthlyHours = self.computeMonthlyHoursPerProject()
        print('      ',end='')
        for str_proj in Calendar.lstr_projectLabels + Calendar.lstr_genericProjectLabels:
            print(str_proj,end=' ')
        print('')
        for d_month in ld_monthlyHours:
            print('      ',end='')
            for str_proj in (Calendar.lstr_projectLabels + Calendar.lstr_genericProjectLabels):
                print(d_month[str_proj],end='   ')
            print('')
    


    def readProjectLabels(self):
        
        l_unlabeledEvents = []
        for event in self.l_CalEvents:
            if event.str_summary.find(':')!=-1:
                str_label = event.str_summary[0:event.str_summary.find(':')]
            else:
                str_label = event.str_summary
                
            if str_label in self.lstr_projectLabels+self.lstr_genericProjectLabels:
                event.str_project = str_label
            else:
                # unlabeled events
                l_unlabeledEvents = l_unlabeledEvents + [event]

        if l_unlabeledEvents:
            print('============== UNLABELED EVENTS ==================')
            for event in l_unlabeledEvents:
                event.print()
                
        return


    def autoAssignEvents(self):

        print('now auto assign')

        l_entireMonths = self.getListOfEntireMonths()
        for event in self.l_CalEvents:
            if event.str_project:
                if event.str_project not in self.lstr_projectLabels: # then it is a generic label
                    # find to which project it must be assigned
                    # 1- hours so far in each project
                    month = date(event.dt_start.year,event.dt_start.month,1)
                    indMonth = l_entireMonths.index(month)
                    d_projectHours = self.sumMonthlyHoursPerProject()

                    # 2- to which projects we may assign these hours
                    if event.str_project not in self.dl_labelCorrespondence.keys():
                        print('ERROR: no key ',event.str_project,' in Calendar.dl_labelCorrespondence')
                        quit()
                    l_candidateProjects = self.dl_labelCorrespondence[event.str_project]
                
                    # 3- see how many hours we have worked in those projects so far
                    d_weightedHoursCandidateProjects = {}
                    for str_project in l_candidateProjects:
                        d_weightedHoursCandidateProjects[str_project] = d_projectHours[str_project]/self.d_workPlan[str_project]
                        
                    l_weightedHoursCandidateProjects = list(d_weightedHoursCandidateProjects.values())
                    # 4- find project where we worked least weighted hours
                    lstr_projects = list(d_weightedHoursCandidateProjects.keys())
                    str_targetProject = lstr_projects[l_weightedHoursCandidateProjects.index(min(l_weightedHoursCandidateProjects))]

                    # 5- Assign event to that project
                    print('assigning to ',str_targetProject)
                    event.str_project = str_targetProject
                    
    def printAssignments(self):

        str_assignmentsFile = 'data/assignments.txt'
        print('Printing event asssignments to file ',str_assignmentsFile)

        with open(str_assignmentsFile, 'w') as output:

            for str_project in Calendar.lstr_projectLabels:
                output.write('---- Project: ' + str_project + '----- \n')
                output.write('YEAR       START END   DUR  DESCRIPTION\n')
                for event in self.l_CalEvents:                    
                    if event.str_project == str_project:
                        str_date = event.dt_start.astimezone(tz=AmsterdamTime()).strftime('%Y/%m/%d')
                        str_startTime =  event.dt_start.astimezone(tz=AmsterdamTime()).strftime('%H:%M')
                        str_endTime =  event.dt_end.astimezone(tz=AmsterdamTime()).strftime('%H:%M')
                        str_duration = ':'.join(str(event.duration()).split(':')[:2])
                        output.write(str_date+' '+str_startTime+' '+str_endTime+' '+str_duration+' '+event.str_summary+'\n')

                output.write('\n\n')


########################################################################


class CalEvent:
    """Each instance is an event in a calendar"""

    def __init__(self):
        self.dt_start = datetime(1900,1,1,tzinfo=UTC())
        self.dt_end = datetime(1900,1,1,tzinfo=UTC())
        self.str_summary = ''
        self.ldt_exdates = [] # exception dates
        self.str_rfreq = '' # empty iff not a repeating event
        self.dt_runtil = ''
        self.i_rcount = ''
        self.str_uid = ''
        self.dt_recurrenceId = []
        self.str_project = '' # project to which this event is assigned

    def CalEventFromStringList(l_strings):
        newEvent = CalEvent()
        for str in l_strings:
            if str[0:len('SUMMARY')] == 'SUMMARY':
                newEvent.str_summary = str[len('SUMMARY')+1:len(str)-1]
            elif str[0:len('DTSTART;VALUE=DATE')] == 'DTSTART;VALUE=DATE': # whole-day events are ignored
                return None
            elif str[0:len('DTSTART')] == 'DTSTART':
                str_start = str[len('DTSTART')+1:len(str)-1]
                newEvent.dt_start = CalEvent.dateStrToDateTime(str_start) 
            elif str[0:len('DTEND')] == 'DTEND':
                str_end = str[len('DTEND')+1:len(str)-1]
                newEvent.dt_end =  CalEvent.dateStrToDateTime(str_end) 
            elif str[0:len('RRULE')] == 'RRULE':
                str_rrule = str[len('RRULE')+1:len(str)-1]
                if not str_rrule[0:len('FREQ=WEEKLY')] == 'FREQ=WEEKLY':
                    print('---> ERROR: ONLY IMPLEMENTED FOR EVENTS REPEATING WEEKLY')
                    print(l_strings)
                    quit()
                else:
                    newEvent.str_rfreq = 'WEEKLY'
                    str_rule = str_rrule[len('FREQ=WEEKLY')+1:]

                    str_untilPattern = 'UNTIL='
                    str_countPattern = 'COUNT='
                    if str_rule[0:len(str_untilPattern)] == str_untilPattern:
                        newEvent.dt_runtil = CalEvent.dateStrToDateTime(str_rule[len(str_untilPattern):])
                    elif str_rule[0:len(str_countPattern)] == str_countPattern:
                        str_rule = str_rule[len(str_countPattern):str_rule.find(';')]
                        newEvent.i_rcount = int(str_rule)

            elif str[0:len('EXDATE')] == 'EXDATE':
                str_exdate = str[len('EXDATE')+1:len(str)-1]
                newEvent.ldt_exdates.append( CalEvent.dateStrToDateTime(str_exdate))
            elif str[0:len('UID')] == 'UID':
                newEvent.str_uid = str[len('UID')+1:len(str)-1]
            elif str[0:len('RECURRENCE-ID')] == 'RECURRENCE-ID':
                str_recurrence = str[len('RECURRENCE-ID')+1:len(str)-1]
                newEvent.dt_recurrenceId = CalEvent.dateStrToDateTime(str_recurrence) 

        return newEvent




    def dateStrToDateTime(str_date):
        
        str_amsterdam = 'TZID=Europe/Amsterdam:'
        if str_date[0:len(str_amsterdam)]==str_amsterdam:
            str_date = str_date[len(str_amsterdam):]
            tzinfo_here = AmsterdamTime()
        else:
            tzinfo_here = UTC()

        if not str_date[0].isdigit():
            disp('ERROR: invalid format of time field')
            quit()
        
        dt_out = datetime(int(str_date[0:4]),int(str_date[4:6]),int(str_date[6:8]),int(str_date[9:11]),int(str_date[11:13]),int(str_date[13:15]),tzinfo=tzinfo_here)
        return dt_out


    def __OLD__dateStrToDateTime(str_date,tzinfo_in):
        dt_out = datetime(int(str_date[0:4]),int(str_date[4:6]),int(str_date[6:8]),int(str_date[9:11]),int(str_date[11:13]),int(str_date[13:15]),tzinfo=tzinfo_in)
        return dt_out

    def duration(self):
        """returns a datetime obj with the duration of the event"""
        dt_dur = self.dt_end - self.dt_start
        return dt_dur

    def print(self):
        print('SUMMARY = ',self.str_summary)
        print('START = ',self.dt_start.astimezone(tz=UTC()))
        print('END = ',self.dt_end.astimezone(tz=UTC()))
        print('DURATION = ',self.duration())
        if self.str_project:
            print('PROJECT = ',self.str_project)
        if self.str_rfreq:
            print(' RFREQ = ',self.str_rfreq)        
        if self.dt_runtil:
            print(' RUNTIL = ',self.dt_runtil)        
        if self.i_rcount:
            print(' RCOUNT = ',self.i_rcount)        
        for str_exdate in self.ldt_exdates:        
            print(' EXDATE = ',str_exdate.astimezone(tz=UTC()))
        if self.str_uid:
            print(' UID = ',self.str_uid)        
        if self.dt_recurrenceId:
            print(' RECURRENCE-ID = ',self.dt_recurrenceId.astimezone(tz=UTC()))

        print('\n')

    def expandRepeatingEvents(l_CalEvents_in):
        """Returns a list with the same events  as l_CalEvents_in but no 
        repeating events are present, they are replaced with as many 
        non-repeating events as needed"""  

        l_CalEvents_out = []
        for event in l_CalEvents_in:
            if event.str_rfreq == '': # the event is not repeating
                l_CalEvents_out.append(event)
            else:
                ld_dates = event.findRepeatingDatesWithoutExceptions()

                
                # dates remaining after the exceptions (EXDATES) have been removed                
                for dt_exdate in event.ldt_exdates:
                    ld_dates.remove(dt_exdate.date())

                # dates remaining after the dates of modified events have been removed
                ldt_modifyingEvents = event.findDTOfModifyingEvents(l_CalEvents_in)

                # print('----- EVENT ------')
                # event.print()
                # print('--- repeating dates with exceptions removed')
                # for it_dt in ld_dates:
                #     print(it_dt)
                # print('--- dates modifying events')
                # for it_dt in ldt_modifyingEvents:
                #     print(it_dt)

#                print(ldt_modifyingEvents)
                for dt_exdate in ldt_modifyingEvents:
                    ld_dates.remove(dt_exdate.date())

                # Find Amsterdam time of initial event
                dt_firstEventAmsterdamTime = event.dt_start.astimezone(tz=AmsterdamTime())
                t_firstEventAmsterdamTime = time(hour=dt_firstEventAmsterdamTime.hour,minute=dt_firstEventAmsterdamTime.minute,second=dt_firstEventAmsterdamTime.second,tzinfo=AmsterdamTime())       
                
                # create the events
                for d_date in ld_dates:
                    l_CalEvents_out.append(CalEvent())
                    l_CalEvents_out[-1].str_summary = event.str_summary
                    l_CalEvents_out[-1].dt_start = datetime.combine(d_date,t_firstEventAmsterdamTime)
                    l_CalEvents_out[-1].dt_end = l_CalEvents_out[-1].dt_start + event.duration()
                
        return l_CalEvents_out

    def  findDTOfModifyingEvents(self,l_CalEvents_in):
        """For a repeating event <self>, this function returns a list of
        datetimes of the events that modify its repetitions. """  

        ldt_modifyingEvents = []
        for event in l_CalEvents_in:
            if (event.str_uid == self.str_uid)&(not event.str_rfreq):
                ldt_modifyingEvents.append(event.dt_recurrenceId)
        return ldt_modifyingEvents

    def findRepeatingDatesWithoutExceptions(event):
        """Based on RCOUNT and RUNTIL, this function obtains the list of dates
        where an event is to be repeated before exceptions have been accounted for"""
    
        if not event.str_rfreq=='WEEKLY': # the event is repeating but not weekly
            print('ERROR: only implemented for weekly repeating events')
            quit()
    
        d_now = event.dt_start.date()
        ld_dates = [] 
        if event.dt_runtil:
            while d_now <= event.dt_runtil.date():
                ld_dates.append(d_now)
                d_now = d_now + timedelta(7)

        elif  event.i_rcount:
            ld_dates.append(d_now)
            for i_count in range(1,event.i_rcount):
                d_now = d_now + timedelta(7)
                ld_dates.append(d_now)

        else: # repeats forever
            while d_now <= date.today():
                ld_dates.append(d_now)
                d_now = d_now + timedelta(7)

        return ld_dates


    def splitAtMidnight(l_CalEvents_in):

        """Returns a list of CalEvents objects where the events that starts
one day and end the following day are split into two events, the first
ending at UTC 00:00 and the second starting at UTC 00:00.
        """  
    
        l_CalEvents_out = []
        for node in l_CalEvents_in:
            if node.duration()>timedelta(1):
                print('----> ERROR: the event ')
                CalEvent.print(node)
                print('exceeds 24 hours')
                quit()
    
            if node.dt_start.date()  == node.dt_end.date():
                l_CalEvents_out.append(node)
            else:
                l_CalEvents_out.append(copy.copy(node))
                l_CalEvents_out[-1].dt_end = datetime(node.dt_end.year,node.dt_end.month,node.dt_end.day,tzinfo=UTC())
                
                # If event does not end at midnight, a new event is
                # added corresponding to the hours in the second day
                if node.dt_end > datetime(node.dt_end.year,node.dt_end.month,node.dt_end.day,tzinfo=UTC()):

                    l_CalEvents_out.append(copy.copy(node))
                    l_CalEvents_out[-1].dt_start = datetime(node.dt_end.year,node.dt_end.month,node.dt_end.day,tzinfo=UTC())
#                    print('splitting')
#                    CalEvent.print(l_CalEvents_out[-2])
#                    CalEvent.print(l_CalEvents_out[-1])
                        
        return l_CalEvents_out


    def readNodeList(str_fileName):

        f = open(str_fileName,'r')

        ld_nodes = [];

        for myline in f:
            if myline=='BEGIN:VEVENT\n':
                l_thisNode = [];
                break

        for myline in f:
            if myline=='BEGIN:VEVENT\n':
                l_thisNode = [];
            elif myline=='END:VEVENT\n':
                event = CalEvent.CalEventFromStringList(l_thisNode)
                if event != None: # event==None if it is a full day event
                    ld_nodes.append(event)
            else:
                l_thisNode.append(myline)

        f.close()

        return ld_nodes


    def saveAssignmentsToFile(l_calEvents,str_filename):

        with open(str_filename, 'wb') as output:
            pickle.dump(l_calEvents, output, pickle.HIGHEST_PROTOCOL)
        print('Saving to ',str_filename)


    def loadAssignmentsFromFile(l_calEvents,str_filename,d_startDate,d_endDate):
        """loads a list of events from the file with name
        <str_filename>. Then, for those events in that list that are within the
        indicated dates and finds a matching event (same dates and
        summary) in l_calEvents. Then, the property str_project of the
        event in l_calEvents is set equal to the property str_project
        in the read list. A list of events out of the interval is returned."""

        with open(str_filename, 'rb') as input:
            l_assignments = pickle.load(input)
            
        l_unusedAssignments = []
        for assignment in l_assignments:
            if (assignment.dt_start.date()<d_startDate)|(assignment.dt_end.date()>=d_endDate):
                l_unusedAssignments.append(assignment)
            else:
                # find an event in l_calEvents with same dates and summary as <assignment>
                for event in l_calEvents:
                    if (event.str_summary==assignment.str_summary)&(
                            event.dt_start==assignment.dt_start)&(
                            event.dt_end==assignment.dt_end):
                        event.str_project = assignment.str_project
                        break
        return l_unusedAssignments


