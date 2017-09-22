from __future__ import division # This imports Python 3 division so that Python 2 and 3 behave the same
import random
import time


class Ticket(object):
    """
    Each process holds a certain number of tickets. The process with the
    winning ticket is selected to run. In the future, tickets will have 
    differing values and currencies.
    """
    
    def __init__(self, amount = 1, currencyvalue = 0):

        # This represent the number of tickets.
        self.amount = amount

        # This reference a currency object.
        self.currencyvalue = currencyvalue

        # A ticket is "active" while it is being used by a thread to compete in a lottery
        self.active = False

        # The currency value multiplied by the ticket amount
        self.value = self.get_tickets_value()
        
    #Aljohrah: I defined a new method to calculate the tickets value
    def get_tickets_value(self):
        if self.currencyvalue.get_exchange_rate() == 0:
            print ('Error self.currencyvalue.get_exchange_rate = 0')
            self.value= ( self.amount * self.currencyvalue.get_exchange_rate() )
            return self.value
        else:
            self.value= ( self.amount * self.currencyvalue.get_exchange_rate() )
            return self.value
        
#----------------------------
        
class Currency(object):
    """
    Currencies define an exchange rate between tickets.
    """
    def __init__(self, name,Back_tick):
        
        """
        Creates a currency with a name.
        """
        
        # we are assuming that the base currency is fixed = 10000
        self.BaseCurrencyAmount=10000
         
        # Name of the currency
        self.name = name
          
        # Tickets that back this currency
        self.backing_tickets = Back_tick

        # the currency amount
        self.amount = 0

        # All tickets issued in this currency
        self.issued_tickets = [] 

        # All processes in this currency
        self.currency_processes = []
        
        #The active amount sum for all issued tickets 
        self.active_amount_sum = [p.tickets.amount for p in self.currency_processes if p.is_active == True]

        # Calculate the exchange rate
        self.exchange_rate = self.get_exchange_rate()

        # This is the sum of the value of the backing tickets
        #cuz every currency is funded by one backing ticket tis is nott needed
        #self.value = self.get_currency_value()
        
        
    def get_currency_value(self):
        """
        Sets the currency's value by summing the value of the currency's
        backing tickets.
        """
        self.value = sum([t.value for t in self.backing_tickets])
               
    def get_exchange_rate(self):
        """
        Calculate the currency's exchange rate by summing the issued tickets
        2amount and deviding it by the currency backing tickets.
        """
        
        self.exchange_rate = 0
        if self.amount != 0:
            self.exchange_rate = round(self.backing_tickets / float(self.amount))
            #print ('exchange_rate',self.exchange_rate)
        return self.exchange_rate

    def ptint_currency(self):
        """ Prints information about the currency """
        print("\n\t\tName:               %s" % self.name)
        print("\t\tBacking Tickets:    %d" % self.backing_tickets)
        print("\t\tAmount:             %d" % self.amount)
        print("\t\tCurrency processes:", [p.name for p in self.currency_processes])
        print("\t\tIssued Tickets:    ", [t.amount for t in self.issued_tickets])
        print("\t\tActive Amount Sum: ", self.active_amount_sum) 
        print("\t\tExchange Rate:     ",self.exchange_rate)
        #print("\t\tValue:             %d" % self.value) 
#----------------------------------------
        
class Node(object):
    """ A process to run with the Lottery Scheduler. """

    def __init__(self, name, tickets, arrival_time, burst_time):
        """
        Creates a node with a name, a certain number of tickets, and a specific
        arrival and burst time.
        """
        self.name = name
        # DONE: Eventually these will be Ticket objects, but for now, just a number
        self.tickets = tickets
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.orig_burst_time = burst_time
        self.is_active = False
        self.first_run = False
        self.start_time = None
        self.completion_time = None
        self.response_time = None
        self.waiting_time = None
        self.turnaround_time = None
        self.run_times = []

    def job_print(self):
        """ Prints information about the process """
        print("\n\t\tName:    %s" % self.name)
        print("\t\tTickets: %d" % self.tickets.amount)
        print("\t\tArrival: %d" % self.arrival_time)
        print("\t\tBurst:   %d" % self.burst_time)


class LotteryScheduler(object):
    """
    A lottery scheduler chooses a process to run by holding a lottery and
    choosing the process holding the winning ticket.
    """

    def __init__(self, quantum_time = 100):
        """
        Creates a LotteryScheduler with an optional quantum time.
        """
        self.cpu_time = 0
        self.processes = []
        self.removed_processes = []
        self.quantum_time = quantum_time
        self.total_response = 0
        self.total_waiting = 0
        self.total_turnaround = 0
        self.total_burst = 0
        self.begin = None
        self.end = None
        self.elapsed_time = None
        self.percentage = None
        self.overhead = None

    def avg_response(self):
        """ Returns the average response time. """
        return self.total_response/len(self.removed_processes)

    def avg_waiting(self):
        """ Returns the average waiting time. """
        return self.total_waiting/len(self.removed_processes)

    def avg_turnaround(self):
        """ Returns the average turnaround time. """
        return self.total_turnaround/len(self.removed_processes)

    def add_process(self, node):
        """ Add a Node to the scheduler. """
        self.processes.append(node)
        print("\n\tADDED PROCESS:")
        node.job_print()

    def remove_process(self, job):
        """ Removes a Node from the scheduler. """
        job.completion_time = time.clock()*1000 - self.begin
        job.turnaround_time = job.completion_time - job.arrival_time
        self.total_turnaround += job.turnaround_time
        job.waiting_time = job.turnaround_time - job.orig_burst_time
        self.total_waiting += job.waiting_time
        self.removed_processes.append(job)
        self.processes.remove(job)
        print("\n\tCOMPLETED PROCESS:")
        job.job_print()

    def print_processes(self, active_only=False):
        """
        Prints the scheduler's processes.
        If active_only is True, only prints active processes.
        """
        if active_only:
            print("\n\tALL ACTIVE PROCESSES:")
            active_processes = [p for p in self.processes if p.is_active]
            if len(active_processes) > 0:
                for p in active_processes:
                    p.job_print()
            else:
                print("\tNo processes")
        else:
            print("\n\tALL PROCESSES:")
            if len(self.processes) > 0:
                for p in self.processes:
                    p.job_print()
            else:
                print("\tNo processes")


    def count_processes(self, active_only=False):
        """
        Returns the number of processes.
        If active_only is True, only counts active processes.
        """
        if active_only:
            return sum([p.is_active for p in self.processes])
        return len(self.processes)

    def count_tickets(self, active_only=False):
        """
        Counts the number of tickets given to processes.
        If active_only is True, only counts tickets for active processes.
        """
        if active_only:
            return sum([n.tickets.get_tickets_value() for n in self.processes if n.is_active])
        return sum([n.tickets.get_tickets_value() for n in self.processes])

    def increase_cpu_time(self, cpu_timer):
        """ Increases the CPU time for the scheduler by the quantum time. """
        sleep_ms = None
        if cpu_timer == None:
            sleep_ms = self.quantum_time
        else:
            sleep_ms = min(cpu_timer, self.quantum_time)

        time.sleep(sleep_ms/1000)
        self.cpu_time += sleep_ms

    def update_active_processes(self):
        """
        Sets a process to active once the CPU time has passed the process's
        arrival time.
        """
        
        for p in self.processes:

            # The process is active after its arrival time
            if p.arrival_time <= self.cpu_time:
                p.is_active = True

    def sum_lottery(self, winner_ticket):
        """
        The lottery scheduler searches for the (active) process holding the
        winning ticket and removes terminated processes from the list.
        """

        ticket_sum = 0
        
        for job in self.processes:

            if job.is_active:

                # Sum tickets to get the range of the winning ticket
                ticket_sum += job.tickets.get_tickets_value()
                
                # The winning ticket number must be less than or equal to the ticket sum
                if winner_ticket <= ticket_sum:

                    # get the start time of the process (when it was first run) and update the total response time
                    if job.first_run == False:
                        job.first_run = True
                        job.start_time = time.clock()*1000 - self.begin
                        job.response_time = job.start_time - job.arrival_time
                        self.total_response += job.response_time
                        self.total_burst += job.burst_time

                    #TODO: Should this be job.burst_time, or the difference between the current and old burst time?
                    cpu_timer = job.burst_time

                    # Update the burst time of the process
                    job.burst_time = max(0, job.burst_time - self.quantum_time)

                    # If the process has completed all its burst time (fully run), terminate the process
                    if job.burst_time == 0:
                        self.remove_process(job)

                    return job, cpu_timer
                

    def print_performance(self):
        print("\n\n~ PERFORMANCE:\n\n")
        print("\tTotal Processes = \t%d" % len(self.removed_processes))
        print("\tTotal Burst Time = \t%d ms" % self.total_burst)
        print("\tCPU Time = \t\t%d ms" % self.cpu_time)
        print("\tElapsed Time = \t\t%d ms" % self.elapsed_time)
        print("\tOverhead = \t\t%d ms" % self.overhead)
        print("\tOverhead Rate = \t" + str(round(self.percentage,2)) + "%")
        print("\tAvg. Response Time = \t%d ms" % self.avg_response())
        print("\tAvg. Waiting Time = \t%d ms" % self.avg_waiting())
        print("\tAvg. Turnaround Time = \t%d ms" % self.avg_turnaround())


    def run(self):
        """ Runs the lottery scheduler. """
        print("\n\n***** STARTING SCHEDULER *****\n")

        self.begin = time.clock()*1000

        lottery_num = 1

        # Run until all of the processes have been terminated
        while self.count_processes() > 0:

            cpu_timer = None

            # Bree: Keeping track of the number of lotteries for the moment
            print("\nLOTTERY %d:" % lottery_num)
            print("-----------------------------")
            lottery_num += 1

            self.update_active_processes()

            print("\n\tCPU TIME: %d" % self.cpu_time)

            print("\n\tTOTAL PROCESSES:  %d" % self.count_processes())
            print("\tTOTAL ACTIVE PROCESSES: %d" % self.count_processes(active_only=True))

            # Print the active processes
            self.print_processes(active_only=True)

            ########################
            # Get the total number of tickets for active processes
            total_active_tickets = round(self.count_tickets(active_only=True)) 
            
            # Print the total number of tickets
            print("\n\tTOTAL TICKETS:  %d" % self.count_tickets())
            print("\tACTIVE TICKETS: %d" % total_active_tickets)

            # If there are no active processes, increase the CPU time and continue with the next loop
            if self.count_processes(active_only=True) == 0:
                print("\n\tNo processes have arrived yet.")
            
            else:
                x = random.randint(1,total_active_tickets)
                winner, cpu_timer = self.sum_lottery(x)
                winner.run_times.append(time.clock())
                print("\n\tWINNING TICKET:  %d" % x)
                print("\tWINNING PROCESS: %s" % winner.name)
                winner.job_print()
            
            # Update the CPU time
            self.increase_cpu_time(cpu_timer)

        self.end = time.clock()*1000

        self.elapsed_time = self.end - self.begin
        if self.elapsed_time > self.cpu_time:
            self.overhead = self.elapsed_time - self.cpu_time
            self.percentage = (self.overhead/self.cpu_time) * 100

        self.print_performance()

def RandomSplit (N, K): 
    """
    Split a given number N into K random parts.
    """
    # 1- generate k random numbers..
    random_numbers_List=[]
    for i in range(0,K):
        random_numbers_List.append(random.randint(1,15))

    # 2- get the random_numbers_List sum to scale the split ..
    list_sum = sum(random_numbers_List)

    # 3- Split..
    splits_list=[ int((i*N)/list_sum) for i in random_numbers_List]
    
    return splits_list

def create_processes_and_currencies ( count ):
    
    # Randomly Select a number of currencies in the range (1 - # of processes)
    # The enter processes will be assigned a currency randomly as they generated..
    total_currency_number = random.randint(1,count)

    currencies_name_list = [ "C%s" %(i+1) for i in range(total_currency_number) ]
        
    # disterbute the base currency between the sub currencies..
    splits = RandomSplit (10000, total_currency_number)

    # map curencies to corrosponding part of base (thier backing tickets)
    currency = list(zip (currencies_name_list, splits))
    
    # create a list of processes names and assigne currencies to them..
    process_name_list = [ "P%s"%(i+1) for i in range(count) ]

    #assign a currency for the processs..
    currency_processes_dict = {} # key = currency name , value = [processes in that currency]
    for i in range(count):
        if i < total_currency_number:
            currency_processes_dict["C%s" %(i+1)] = [process_name_list[i]]
        else:
            # randomly select a currency to add the process to..
            index = random.randint(1,len(currency))
            currency_processes_dict["C%s" %(index)].append(process_name_list[i])

    print ('currency_processes_dict =', currency_processes_dict)

    # For each currency reate a currency object so that process in the same currency hold the same currency obj..
    currency_obj_dict = {} # key = currency name , value = currency obj
    for cName in currencies_name_list:
        cbacking_tickets = currency[[y[0] for y in currency].index(cName)][1]
        currency_obj_dict[cName] = Currency(cName, cbacking_tickets)
    
    # initialize scheduler
    scheduler = LotteryScheduler()
    
    # insert processes into the processes list
    for i in range(count):
        arrival_time  = random.randrange(1,500)
        burst_time  = random.randrange(1,5000)
        name = "P%s"%(i+1)

        # Get the process currency ..
        currency_name = ''
        for c, p in currency_processes_dict.items():
            if name in p:
                currency_name = c
            
        # Create the ticket object..
        amount=random.randint(1,500)
        currencyobj = currency_obj_dict[currency_name]
        tickets = Ticket(amount, currencyobj)

        # create the process obj.
        job = Node(name, tickets, arrival_time, burst_time)
        scheduler.add_process(job)

        # Update the currency obj. info
        currencyobj.currency_processes.append(job)
        currencyobj.amount = currencyobj.amount + tickets.amount
        currencyobj.issued_tickets.append(tickets)
        currencyobj.get_exchange_rate()

        print('****************************************************')
         
    # To Check if assining currencies was done correctly .. print all infos ..
    for p in scheduler.processes:
        print ('process info..')
        p.job_print()
        print ('currency info..')
        p.tickets.currencyvalue.ptint_currency()


    return scheduler

if __name__ == "__main__":

    print("\nWELCOME TO THE LOTTERY SCHEDULER SIMULATOR")
    
    # Get total number of processes and lotteries from user
    count = int(input("\nEnter total number of processes: "))

    scheduler = create_processes_and_currencies(count)
        
    scheduler.run()

    print("\n\n***** SCHEDULER FINISHED *****\n")

    

    
    
