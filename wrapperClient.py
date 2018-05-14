import threading
import Queue
import time
import subprocess, datetime

# thread class to run a command
class LeelaThread(threading.Thread):
    def __init__(self, cmd, queue, index):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.queue = queue
        self.index = index
        

    def run(self):
        # execute the command, queue the result
        p = subprocess.Popen(cmd, stdout = subprocess.PIPE,  stderr = subprocess.STDOUT, shell = True)
        while True:
            line = p.stdout.readline()
            if line:
                self.queue.put((self.cmd, line, self.index))
            

# queue where results are placed
result_queue = Queue.Queue()

# define the commands to be run in parallel, run them
cmd = 'client.exe'
singleLoggingFilename = "wrapper-logs.txt"
singleLoggingFile = open(singleLoggingFilename,"w")



baseNumberOfClient = 3
baseMinuteForStats = 5.0
baseDelta = datetime.timedelta(0,60*baseMinuteForStats)

movePlayedLastxMinutes=0
previousmovePlayedLastxMinutes=0
theNow = datetime.datetime.now()


for i in range(0,baseNumberOfClient):
    thread = LeelaThread(cmd, result_queue, i)
    thread.start()
    
print baseNumberOfClient, "client.exe are successfully running, check log file",  singleLoggingFilename
futureNextIndex = baseNumberOfClient

# print results as we get them
while threading.active_count() > 1 or not result_queue.empty():
    while not result_queue.empty():
        (cmd, output, index) = result_queue.get()
        singleLoggingFile.write('client['+str(index)+"]:"+output)
        if "move played" in output:
            movePlayedLastxMinutes+=1
        
        
    if (datetime.datetime.now()-theNow) >  baseDelta:
        #flush the logs
        singleLoggingFile.flush()
        theNow = datetime.datetime.now()  
        print "move played per minutes :" , movePlayedLastxMinutes/baseMinuteForStats, "previous:",previousmovePlayedLastxMinutes/baseMinuteForStats
        #add a client or not ?
        if movePlayedLastxMinutes > previousmovePlayedLastxMinutes:
            print "let's add a thread"
            thread = LeelaThread(cmd, result_queue, futureNextIndex)
            thread.start()
            futureNextIndex+=1
        previousmovePlayedLastxMinutes = movePlayedLastxMinutes
        movePlayedLastxMinutes=0
        
        
    time.sleep(2)
    print futureNextIndex, "clients are running, next status check in ", theNow+baseDelta-datetime.datetime.now(),"\r",
    
    
singleLoggingFile.close()