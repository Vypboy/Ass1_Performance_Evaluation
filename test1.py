import simpy
#import random
import numpy.random as random

''' ------------------------ '''
''' Parameters               '''
''' ------------------------ '''
MAXSIMTIME = 5000
VERBOSE = False
LAMBDA = 5.0
MU1 = 8.0
MU2 = 8.0
MU3 = 8.0
p12 = 0.8 #type 1
p13 = 0.2 #type 2
POPULATION = 50000000
SERVICE_DISCIPLINE = 'FIFO'
LOGGED = True
NUM_SERVERS = 3  # Số máy chủ
TIME_OUT = 60  # Thời gian chờ tối đa của một job
''' ------------------------ '''
''' DES model                '''
''' ------------------------ '''
class Job:
    def __init__(self, name, arrtime, duration):
        self.name = name
        self.arrtime = arrtime
        self.duration = duration

    def __str__(self):
        return '%s at %d, length %d' %(self.name, self.arrtime, self.duration)

def SJF(job):
    return job.duration

def Do_Task(self, Jobs):
    ''' do nothing, just change server to idle
        and then yield a wait event which takes infinite time
    '''
    self.Jobs = Jobs
    if len(self.Jobs) == 0:
        self.serversleeping = env.process(self.waiting(self.env))
        t1 = self.env.now
        yield self.serversleeping
        ''' accumulate the server idle time'''
        self.idleTime += self.env.now - t1
    else:
        ''' get the first job to be served'''
        if self.strat == 'SJF':
            self.Jobs.sort(key=SJF)
            j = self.Jobs.pop(0)
        else:  # FIFO by default
            j = self.Jobs.pop(0)
        if LOGGED:
            qlog.write('%.4f\t%d\t%d\n'
                        % (self.env.now, 1 if len(self.Jobs) > 0 else 0, len(self.Jobs)))

        ''' sum up the waiting time'''
        self.waitingTime += self.env.now - j.arrtime
        ''' yield an event for the job finish'''
        # Check timeout from begginning
        '''
        if j.duration > TIME_OUT:
            # yield self.env.timeout(TIME_OUT)
            # error
            continue
        else:
            yield self.env.timeout(j.duration)
        '''

        ''' sum up the jobs done '''
        self.jobsDone += 1


''' A server
 - env: SimPy environment
 - strat: - FIFO: First In First Out
          - SJF : Shortest Job First
'''
class Server:
    def __init__(self, env, strat='FIFO'):
        self.env = env
        self.strat = strat
        self.Jobs = list(())
        self.serversleeping = None
        ''' statistics '''
        self.waitingTime = 0
        self.idleTime = 0
        self.jobsDone = 0
        ''' register new server processes '''
        for i in range(NUM_SERVERS):
            env.process(self.serve(i))

    def serve(self):
        while True:
            ''' do nothing, just change server to idle
              and then yield a wait event which takes infinite time
            '''
            if len(self.Jobs) == 0:
                self.serversleeping = env.process(self.waiting(self.env))
                t1 = self.env.now
                yield self.serversleeping
                ''' accumulate the server idle time'''
                self.idleTime += self.env.now - t1
            else:
                ''' get the first job to be served'''
                if self.strat == 'SJF':
                    self.Jobs.sort(key=SJF)
                    j = self.Jobs.pop(0)
                else:  # FIFO by default
                    j = self.Jobs.pop(0)
                if LOGGED:
                    qlog.write('%.4f\t%d\t%d\n'
                                % (self.env.now, 1 if len(self.Jobs) > 0 else 0, len(self.Jobs)))

                ''' sum up the waiting time'''
                self.waitingTime += self.env.now - j.arrtime
                ''' yield an event for the job finish'''
                # Check timeout from begginning
                '''
                if j.duration > TIME_OUT:
                    # yield self.env.timeout(TIME_OUT)
                    # error
                    continue
                else:
                    yield self.env.timeout(j.duration)
                '''

                ''' sum up the jobs done '''
                self.jobsDone += 1

                # Random to choose next server
                Random()

    def waiting(self, env):
        try:
            if VERBOSE:
                print('Server is idle at %.2f' % self.env.now)
            yield self.env.timeout(MAXSIMTIME)
        except simpy.Interrupt as i:
            if VERBOSE:
                print('Server waken up and works at %.2f' % self.env.now)



class Multi_Queues:
     def __init__(self, env, num_queues, queue_capacity, server_capacity, lam, mu1, mu2, mu3, p12, p13):
        self.env = env
        self.num_queues = num_queues
        self.queue_capacity = queue_capacity
        self.server_capacity = server_capacity
        self.lam = lam
        self.mu1 = mu1
        self.mu2 = mu2
        self.mu3 = mu3
        self.p12 = p12
        self.p13 = p13

    def do_task(self, server_id):
        while True:
            # Do task queue1 -> details

            # Run Random() follow p12, p13 to choose next queue

            # Do task queue2:
                # - update duration -> check timeout 

            # Do task queue3:
                # - update duration -> check timeout 


class Customer_Requests:
    def __init__(self, env, server, nrjobs=10000000, lam=5, mu=8):
        self.server = server
        self.nrjobs = nrjobs
        self.interarrivaltime = 1 / lam
        self.servicetime = 1 / mu
        env.process(self.generatejobs(env))

    def generate_customers(self, env):
        i = 1
        while True:
            '''yield an event for new job arrival'''
            job_interarrival = random.exponential(self.interarrivaltime)
            yield env.timeout(job_interarrival)

            ''' generate service time and add job to the list'''
            job_duration = random.exponential(self.servicetime)
            self.server.Jobs.append(Job('Job %s' % i, env.now, job_duration))
            if VERBOSE:
                print('job %d: t = %.2f, l = %.2f, dt = %.2f'
                      % (i, env.now, job_duration, job_interarrival))
            i += 1

            ''' if server is idle, wake it up'''
            if not self.server.serversleeping.triggered:
                self.server.serversleeping.interrupt('Wake up, please.')

''' open a log file '''
if LOGGED:
    qlog = open('mm1-l%d-m%d.csv' % (LAMBDA, MU), 'w')
    qlog.write('0\t0\t0\n')

''' start SimPy environment '''
env = simpy.Environment()

'''
MyServer = Server(env, SERVICE_DISCIPLINE)
MyJobGenerator = JobGenerator(env, MyServer, POPULATION, LAMBDA, MU)

MyServer2 = Server(env, SERVICE_DISCIPLINE)
MyServer3 = Server(env, SERVICE_DISCIPLINE)
MyJobGenerator = JobGenerator(env, MyServer2, POPULATION, LAMBDA, MU)
'''
# num_servers_third_queue = 3
# phone_teller_third_queue = PhoneTeller(env, num_servers_third_queue)

''' start simulation '''
env.run(until=MAXSIMTIME)

''' close log file '''
if LOGGED:
    qlog.close()

''' print statistics '''
RHO = LAMBDA / (MU * NUM_SERVERS)  # Tính số Utilization cho M/M/3
print('Arrivals               : %d' % (MyServer.jobsDone))
print('Utilization            : %.2f/%.2f'
      % (1.0 - MyServer.idleTime / MAXSIMTIME, RHO))
print('Mean waiting time      : %.2f/%.2f'
      % (MyServer.waitingTime / MyServer.jobsDone, (RHO ** 2) / ((1 - RHO) * LAMBDA)))
