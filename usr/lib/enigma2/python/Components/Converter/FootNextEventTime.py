from Converter import Converter
from Poll import Poll
from time import time
from Components.Element import cached, ElementError
from time import localtime, strftime


class FootNextEventTime(Poll, Converter, object):
    STARTTIME = 0
    ENDTIME = 1
    REMAINING = 2
    PROGRESS = 3
    DURATION = 4
    STARTANDENDTIME = 5
    REMAININGANDRUNTIME = 6
    TITLESTARTANDENDTIME = 7

    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        if type == 'EndTime':
            self.type = self.ENDTIME
        elif type == 'Remaining':
            self.type = self.REMAINING
            self.poll_interval = 60000
            self.poll_enabled = True
        elif type == 'StartTime':
            self.type = self.STARTTIME
        elif type == 'StartAndEndTime':
            self.type = self.STARTANDENDTIME
        elif type == 'Duration':
            self.type = self.DURATION
        elif type == 'Progress':
            self.type = self.PROGRESS
            self.poll_interval = 30000
            self.poll_enabled = True
        elif type == 'TitleStartAndEndTime':
            self.type = self.TITLESTARTANDENDTIME
        else:
            raise ElementError("'%s' is not <StartTime|EndTime|Remaining|Duration|Progress> for EventTime converter" % type)

    @cached
    def getTime(self):
        event = self.source.event
        if event is None:
            return
        elif self.type == self.STARTTIME:
            return event.getBeginTime()
        elif self.type == self.ENDTIME:
            return event.getBeginTime() + event.getDuration()
        elif self.type == self.STARTANDENDTIME:
            return (event.getBeginTime(), event.getBeginTime() + event.getDuration())
        elif self.type == self.DURATION:
            return event.getDuration()
        else:
            if self.type == self.REMAINING:
                now = int(time())
                start_time = event.getBeginTime()
                duration = event.getDuration()
                end_time = start_time + duration
                if start_time <= now <= end_time:
                    return (duration, end_time - now)
                else:
                    return (duration, None)
            elif self.type == self.TITLESTARTANDENDTIME:
                t1 = localtime(event.getBeginTime())
                t2 = localtime(event.getBeginTime() + event.getDuration())
                return_str = '%s   %s - %s' % (event.getEventName(), strftime('%H:%M', t1), strftime('%H:%M', t2))
                return return_str.upper()
            return

    @cached
    def getValue(self):
        event = self.source.event
        if event is None:
            return
        else:
            now = int(time())
            start_time = event.getBeginTime()
            duration = event.getDuration()
            if start_time <= now <= start_time + duration and duration > 0:
                return (now - start_time) * 1000 / duration
            return
            return

    text = property(getTime)
    time = property(getTime)
    value = property(getValue)
    range = 1000

    def changed(self, what):
        Converter.changed(self, what)
        if self.type == self.PROGRESS and len(self.downstream_elements):
            if not self.source.event and self.downstream_elements[0].visible:
                self.downstream_elements[0].visible = False
            elif self.source.event and not self.downstream_elements[0].visible:
                self.downstream_elements[0].visible = True
