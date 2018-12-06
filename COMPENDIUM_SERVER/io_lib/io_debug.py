import time
import os
import datetime
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

class io_debug:
    IO_PRINT  = False
    IO_LOG    = None
    IO_OUTPUT = None
    def __init__(self, io_print=False, io_log=None, buffTxt=False):
        # io_print ---> just printing in the console
        # io_log   ---> don't print but log in to a text file
        # buffTxt  ---> buffer all print's to use io_getbuffer to retrieve the buffer
        # We are setting everything here but we only support one at a time. This means the
        # priority of flags is as follows:
        #    1) IO_PRINT
        #    2) IO_LOG
        #    3) IO_OUTPUT
        #
        # Be sure to just turn on what you want to use when calling this class.
        self.IO_PRINT  = io_print
        self.IO_LOG    = io_log
        if buffTxt:
            self.IO_PRINT = False
            self.IO_OUTPUT = StringIO()

    def io_getbuffer(self):
        return self.IO_OUTPUT.getvalue()

    def io_print(self, text = ''):
        # Priority is as follows,
        if self.IO_PRINT:
            print text
        elif self.IO_LOG != None:
            if os.path.exists(self.IO_LOG):
                last_modify = os.path.getmtime(self.IO_LOG)
                last_modify_day = datetime.datetime.fromtimestamp(last_modify).strftime('%d')
                today_day =  datetime.datetime.today().day
                if last_modify_day < today_day:
                    file = open(self.IO_LOG,"a")
                    file.write('\n\n'+time.strftime("%d/%m/%Y")+'\n'+text)
                    file.close()
                else:
                    file = open(self.IO_LOG,"a")
                    file.write('\n'+text)
                    file.close()
            else:
                file = open(self.IO_LOG,"a")
                file.write('\n\n'+time.strftime("%d/%m/%Y")+'\n'+text)
                file.close()
            return
        elif self.IO_OUTPUT != None:
            self.IO_OUTPUT.write(str(text) + '\n')
            return
