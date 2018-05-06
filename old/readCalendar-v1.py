# NEXT DAY
# - Introduce check to ensure that there are no events overlapping in time 
# - Replicate events with RRULE:FREQ=WEEKLY
# - Compute monthly totals  and compare with google sheets 
# - Obtain monthly totals per category, e.g. ORG, email...


# Important information:
# 
# The format of calendar files specifies time in terms of UTC, which
# in winter is one hour less than the central european time.
#
# Events that span the entire day ("all day") or multiple entire days
# do not have a field of the form "DTSTART:19700329T020000"; instead,
# they have a field of the form
# "DTSTART;VALUE=DATE:20170906". (similar for DTEND)
#


def dictionaryFromListOfStrings(l_Node):
    """Returns a dictionary corresponding to the event with fields specified by the list of strings l_Node"""
    d_node = {};
    for str in l_Node:
        indColon = str.find(':')        
        d_node[str[0:indColon]] = str[indColon+1:len(str)-1]
    return d_node


########################################################################

def readNodeList():

   # f = open('caltest.txt','r')
    f = open('calfull.txt','r')

    ld_nodes = [];

    for myline in f:
        if myline=='BEGIN:VEVENT\n':
            l_thisNode = [];
            break

    for myline in f:
        if myline=='BEGIN:VEVENT\n':
            l_thisNode = [];
        elif myline=='END:VEVENT\n':
            ld_nodes.append(dictionaryFromListOfStrings(l_thisNode))
        else:
            l_thisNode.append(myline)

    f.close()

    return ld_nodes


########################################################################

def splitAtMidnight(ld_nodes_in):
    """If an event starts one day and ends the following day, then it is split into two events, the first ends at UTC 00:00 and the second starts at UTC 00:00. Moreover, the output list does not contain *all day* events"""  
    
    ld_nodes_out = []
    for node in ld_nodes_in:
        if 'DTSTART' in node:
            str_start = node['DTSTART']
            str_dtstart = str_start[0:8]
            str_end = node['DTEND']
            str_dtend = str_end[0:8]
            if str_dtend == str_dtstart:
                ld_nodes_out.append(node)
            else:
                print('splitting')
                node1 = copy.copy(node)
                node1['DTEND'] = str_dtend + 'T000000Z'
                node2 = copy.copy(node)
                node2['DTSTART'] = str_dtend + 'T000000Z'
                ld_nodes_out.append(node1)
                ld_nodes_out.append(node2)

    return ld_nodes_out

########################################################################
def computeDuration(ld_nodes):
    for node in ld_nodes:
        str_start = node['DTSTART']            
        str_end = node['DTEND']
        datetime_start = datetime.datetime(int(str_start[0:4]),int(str_start[4:6]),int(str_start[6:8]),int(str_start[9:11]),int(str_start[11:13]),int(str_start[13:15]))
        datetime_end = datetime.datetime(int(str_end[0:4]),int(str_end[4:6]),int(str_end[6:8]),int(str_end[9:11]),int(str_end[11:13]),int(str_end[13:15]))
        node['DELTA_DURATION'] = datetime_end - datetime_start

    return ld_nodes

########################################################################

def dictByDates(ld_nodes):
    """Creates a dictionary where each field name is a date and the contents of that field is a list of events ocurring on that date."""
    d_nodes = {};
    for node in ld_nodes:
        if 'DTSTART' in node:
            str_start = node['DTSTART']
            str_dtstart = str_start[0:8]            
            if str_dtstart not in d_nodes:
                d_nodes[str_dtstart] = [];
            d_nodes[str_dtstart].append(node)

    return d_nodes


########################################################################

def sumHours(l_events):
    """adds the hours of all events in the list l_events"""
    delta_totalHours = datetime.timedelta();
    for node in l_events:
        delta_totalHours = delta_totalHours + node['DELTA_DURATION']
    
    return delta_totalHours



########################################################################

def date_range(start_date, end_date):
    for ordinal in range(start_date.toordinal(), end_date.toordinal()):
        yield datetime.date.fromordinal(ordinal)

########################################################################

import copy
import datetime
from datetime import timedelta, date

print('Read calendar v1.0')

# Create dictionary of events per date
ld_nodes = readNodeList()
ld_nodes = splitAtMidnight(ld_nodes)
ld_nodes = computeDuration(ld_nodes)
d_nodes = dictByDates(ld_nodes)

#for str_date in list(d_nodes.keys()):
#    print(str_date,' ',len(d_nodes[str_date]))

start_date = date(2017, 4, 24)
end_date = date(2017, 4, 25)
for single_date in date_range(start_date, end_date):
    str_date_now = single_date.strftime("%Y%m%d")
    if str_date_now in d_nodes:
        print(str_date_now,', ',len(d_nodes[str_date_now]),' events, total hours =',sumHours(d_nodes[str_date_now]))
        for nn in d_nodes[str_date_now]:
            print(nn)
        


quit()


start_datetime = datetime.datetime(2017, 1, 1,12,30,00)
end_datetime = datetime.datetime(2017, 1, 15,13,15,00)
delta1 = end_datetime-start_datetime
print(delta1)
print(delta1+delta1)

quit()



# how to iterate over dates




