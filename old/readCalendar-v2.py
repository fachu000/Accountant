# Version 2
#   - Events are objects of class CalEvent

# NEXT DAY
# - modify dateStrToDateTime to take just one sting and identify the time zone for it. Modify the functions invoking it accordingly.
# - modify CalEventFromStringList to parse RRULE and store that info in multiple fields of CalEvent. Also modify expandRepeatingEvents accordingly.
# - Read UID and Recurrence-ID
# - Use the field UID and RECURRENCE-ID to modify repeating events 
#   (currently there are replicates):
#       - option A (preferred): in expandRepeatingEvents, repeat for each event E with a field RRULE: find all other events with the same UID (they are modified versions of repeated instances of E) and add their RECURRENCE-ID to the list of EXDATES before expanding E. In this way, E will not be replicated in days whereit has been modified.  
#       - option B: after expandRepeatingEvents, process the list to remove duplicates as follows: every time you find an event with a field RECURRENCE-ID, erase the event with the same UID on the date/time indicated by RECURRENCE-ID (such an event is an instance of a repeating event)
# - Compute monthly totals  and compare with google sheets 
# - Obtain monthly totals per category, e.g. ORG, email...


# Important information:
# 
# The format of calendar files specifies time in terms of UTC. The
# local time in Central Europe is CET in winter (UTC +1) and CEST in
# summer (UTC+2). Note that some repeating events start in CET and end
# in CEST or viceversa.
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



########################################################################

def readNodeList():

    f = open('caltest.txt','r')
#    f = open('calfull.txt','r')
#    f = open('new_test_calendar2.ics','r')

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



########################################################################
# def computeDuration(ld_nodes):
#     for node in ld_nodes:
#         str_start = node['DTSTART']            
#         str_end = node['DTEND']
#         datetime_start = datetime.datetime(int(str_start[0:4]),int(str_start[4:6]),int(str_start[6:8]),int(str_start[9:11]),int(str_start[11:13]),int(str_start[13:15]))
#         datetime_end = datetime.datetime(int(str_end[0:4]),int(str_end[4:6]),int(str_end[6:8]),int(str_end[9:11]),int(str_end[11:13]),int(str_end[13:15]))
#         node['DELTA_DURATION'] = datetime_end - datetime_start

#     return ld_nodes

########################################################################

# def dictByDates(ld_nodes):
#     """Creates a dictionary where each field name is a date and the contents of that field is a list of events ocurring on that date."""
#     d_nodes = {};
#     for node in ld_nodes:
#         if 'DTSTART' in node:
#             str_start = node['DTSTART']
#             str_dtstart = str_start[0:8]            
#             if str_dtstart not in d_nodes:
#                 d_nodes[str_dtstart] = [];
#             d_nodes[str_dtstart].append(node)

#     return d_nodes


########################################################################

# def sumHours(l_events):
#     """adds the hours of all events in the list l_events"""
#     delta_totalHours = datetime.timedelta();
#     for node in l_events:
#         delta_totalHours = delta_totalHours + node['DELTA_DURATION']
    
#     return delta_totalHours



########################################################################

def date_range(start_date, end_date):
    for ordinal in range(start_date.toordinal(), end_date.toordinal()):
        yield datetime.date.fromordinal(ordinal)

########################################################################

class CalEvent:
    """Each instance is an event in a calendar"""

    def __init__(self):
        self.dt_start = datetime(1900,1,1,tzinfo=UTC())
        self.dt_end = datetime(1900,1,1,tzinfo=UTC())
        self.str_summary = ''
        self.str_rrule = ''
        self.ldt_exdates = [] # exception dates

    def CalEventFromStringList(l_strings):
        newEvent = CalEvent()
        for str in l_strings:
            i_indColon = str.find(':')        
            if str[0:i_indColon] == 'SUMMARY':
                newEvent.str_summary = str[i_indColon+1:len(str)-1]
            elif str[0:i_indColon] == 'DTSTART;VALUE=DATE': # whole-day events
                return None
            elif str[0:i_indColon] == 'DTSTART':
                str_start = str[i_indColon+1:len(str)-1]
                newEvent.dt_start = CalEvent.dateStrToDateTime(str_start,UTC()) 
            elif str[0:i_indColon] == 'DTSTART;TZID=Europe/Amsterdam':
                str_start = str[i_indColon+1:len(str)-1]
                newEvent.dt_start = CalEvent.dateStrToDateTime(str_start,AmsterdamTime())       
            elif str[0:i_indColon] == 'DTEND':
                str_end = str[i_indColon+1:len(str)-1]
                newEvent.dt_end =  CalEvent.dateStrToDateTime(str_end,UTC()) 
            elif str[0:i_indColon] == 'DTEND;TZID=Europe/Amsterdam':
                str_end = str[i_indColon+1:len(str)-1]
                newEvent.dt_end = CalEvent.dateStrToDateTime(str_end,AmsterdamTime())       
            elif str[0:i_indColon] == 'RRULE':
                newEvent.str_rrule = str[i_indColon+1:len(str)-1]
            elif str[0:i_indColon] == 'EXDATE;TZID=Europe/Amsterdam':
                str_exdate = str[i_indColon+1:len(str)-1]
                newEvent.ldt_exdates.append( CalEvent.dateStrToDateTime(str_exdate,AmsterdamTime()))

        return newEvent




    def dateStrToDateTime(str_date,tzinfo_in):
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
        if self.str_rrule:
            print(' RRULE = ',self.str_rrule)        
        for str_exdate in self.ldt_exdates:        
            print('  EXDATE = ',str_exdate.astimezone(tz=UTC()))
        print('\n')

    def expandRepeatingEvents(l_CalEvents_in):
        """Returns a list with the same events  as l_CalEvents_in but no 
        repeating events are present, they are replaced with as many 
        non-repeating events as needed"""  

        l_CalEvents_out = []
        for event in l_CalEvents_in:
            if event.str_rrule == '':
                l_CalEvents_out.append(event)
            elif event.str_rrule.find('FREQ=WEEKLY') == -1:
                print('---> ERROR: ONLY IMPLEMENTED FOR EVENTS REPEATING WEEKLY')
                event.print()
                quit()
            else:
                # dates where the event should in principle be replicated
                str_pattern = 'FREQ=WEEKLY;'
                str_dateEndRepeating = event.str_rrule[event.str_rrule.find(str_pattern)+len(str_pattern):]
                str_untilPattern = 'UNTIL='
                str_countPattern = 'COUNT='
                if str_dateEndRepeating.find(str_untilPattern)>=0:
                    str_untilDate = str_dateEndRepeating[str_dateEndRepeating.find(str_untilPattern)+len(str_untilPattern):]
                    dt_endRepeating = CalEvent.dateStrToDateTime(str_untilDate,UTC())
                    d_now = event.dt_start.date()
                    ld_dates = [] # list of dates for which the event will be replicated
                    while d_now <= dt_endRepeating.date():
                        ld_dates.append(d_now)
                        d_now = d_now + timedelta(7)

                elif  str_dateEndRepeating.find(str_countPattern)>=0:
                    print('============-----')
                    event.print()
                    print('============-----')
                    str_countNumber = str_dateEndRepeating[str_dateEndRepeating.find(str_countPattern)+len(str_countPattern):str_dateEndRepeating.find(';')]           
                    print('ooo ',str_countNumber)         
                    d_now = event.dt_start.date()
                    ld_dates = []
                    for i_count in range(1,int(str_countNumber)):
                        d_now = d_now + timedelta(7)
                        ld_dates.append(d_now)
                        
                    
                else:
                    d_now = event.dt_start.date()
                    ld_dates = []
                    while d_now <= date.today():
                        ld_dates.append(d_now)
                        d_now = d_now + timedelta(7)
                                
                # dates remaining after the exceptions (EXDATES) have been removed
                for dt_exdate in event.ldt_exdates:
                    ld_dates.remove(dt_exdate.date())

                # dates remaining after the dates of modified events have been removed

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


class Calendar:
    """Objects of this class contain a list of CalEvents for each day"""

    # ordinal of the first day in the calendar
    i_firstDay = 736330 # = date(2017,1,1).toordinal()

    def __init__(self,l_CalEvents):
        """With the CalEvents in the list l_CalEvents, this constructor forms
        a list of lists called self.ll_CalEvents, where the n-th list
        contains the CalEvents corresponding to the events in the n-th
        day. The 0-th day is CalEvents.d_firstDay.

        """ 

        l_CalEvents = CalEvent.expandRepeatingEvents(l_CalEvents)
        l_CalEvents = CalEvent.splitAtMidnight(l_CalEvents)

        self.ll_CalEvents = Calendar.ll_CalEvents_from_l_CalEvents(l_CalEvents)
        self.ensureNoOverlappingEvents()

            
    def ll_CalEvents_from_l_CalEvents(l_CalEvents):
        ll_CalEvents = [None]*( date.today().toordinal()-Calendar.i_firstDay)
        for event in l_CalEvents:
            i_dayRelInd = event.dt_start.date().toordinal()-Calendar.i_firstDay
            if i_dayRelInd < 0:
                print('ERROR: event before the beginning of the calendar')
                event.print()
                quit()

            elif i_dayRelInd >= len(ll_CalEvents):
                print('omitting future event')
            elif ll_CalEvents[i_dayRelInd]==None:
                ll_CalEvents[i_dayRelInd]=[event]
            else:
                ll_CalEvents[i_dayRelInd].append(event)
        return(ll_CalEvents)

    def sortDays(self):
        for i_day in range(0,len(self.ll_CalEvents)-1):
            if self.ll_CalEvents[i_day] != None:
                self.ll_CalEvents[i_day] = sorted(self.ll_CalEvents[i_day],key=lambda evt:evt.dt_start)

    def ensureNoOverlappingEvents(self):
        """produces a warning if there are distinct overlapping events"""
        self.sortDays()
        for i_day in range(0,len(self.ll_CalEvents)-1):
            if self.ll_CalEvents[i_day] != None:
                for i_eventInd in range(0,len(self.ll_CalEvents[i_day])-1):
                    evt1 = self.ll_CalEvents[i_day][i_eventInd]
                    evt2 = self.ll_CalEvents[i_day][i_eventInd+1]
                    

                    if evt1.dt_end > evt2.dt_start:
                        print('---> WARNING: the following events are overlapping')
                        evt1.print()
                        evt2.print()
                        


    def print(self):
        for i_day in range(0,len(self.ll_CalEvents)-1):
            if self.ll_CalEvents[i_day] != None:
                print('=== Day ',date.fromordinal(Calendar.i_firstDay+i_day),' ===')
                for event in self.ll_CalEvents[i_day]:
                    event.print()
        

        

########################################################################

from AmsterdamTime import AmsterdamTime, UTC
from datetime import datetime,timedelta,time,date
import copy

l_CalEvents = readNodeList()

for it_ce in l_CalEvents:
    it_ce.print()



#for it_ce in l_CalEvents:
#    it_ce.print()

cal = Calendar(l_CalEvents)
#cal.print()



quit()







