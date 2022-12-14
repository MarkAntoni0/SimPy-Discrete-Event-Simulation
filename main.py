########################################################################
#Discrete Event Simulation using SimPy and NumPy                       #
#AASTMT - Modelling and Simulation course                              #
#Written by: Mark Tharwat - 19200164                                   #
#                                                                      #
#numpy’s used distribuntions                                           #
#normal(mean, SD)                                                      #
#triangular(min, mean, max)                                            #
#lognormal(mean, SD)                                                   #
#exponential(lambda)                                                   #
########################################################################
import simpy
import random
import numpy
from statistics import mean


#Arrivals generator function
def newCustomerGenerator(env, interArrival_Mean, orderingStation_dist_mean, paymentWindow_dist_mean, pickUpWindows_dist_mean, orderStationSlots, paymentWindowsSlots, pickUpWindowsSlots):
    p_id = 0

    while True:
        #create a new instance of activity generator
        p = activity_generator(env, orderingStation_dist_mean, paymentWindow_dist_mean, pickUpWindows_dist_mean, orderStationSlots, paymentWindowsSlots, pickUpWindowsSlots, p_id)

        #run the activity generator
        env.process(p)

        #sample time for the next arrival
        t = random.expovariate(interArrival_Mean)

        yield env.timeout(t)

        p_id += 1

def activity_generator(env, orderingStation_dist_mean, paymentWindow_dist_mean, pickUpWindows_dist_mean, orderStationSlots, paymentWindowsSlots, pickUpWindowsSlots, p_id):
    global list_of_queueing_time_ordering
    global list_of_queueing_time_paying
    global list_of_queueing_time_pickingUp

    time_entered_for_ordering = env.now

    #request a slot for ordering
    with orderStationSlots.request() as req:
        yield req

        time_left_for_ordering = env.now
        time_inQueue_for_ordering = time_left_for_ordering - time_entered_for_ordering
        print("Customer ", p_id," queued for ordering for ", time_inQueue_for_ordering," seconds", sep="")

        #add the calculated time into the list to get the average 
        list_of_queueing_time_ordering.append(time_inQueue_for_ordering)
        #sample the time spent ordering
        sampled_ordering_time = numpy.random.normal(orderingStation_dist_mean, orderingStation_dist_sd)

        #freeze until that time is elapsed
        yield env.timeout(abs(sampled_ordering_time))

    #the ordering phase is completed and the customer can move to payment
    time_entered_for_payment = env.now
    # request a slot for payment
    with paymentWindowsSlots.request() as req:
        #freeze until there is a slot available
        yield req

        time_left_for_payment = env.now
        time_inQueue_for_payment = time_left_for_payment - time_entered_for_payment
        print("Customer ", p_id, " queued for payment for ", time_inQueue_for_payment, " seconds",sep="")

        # add the calculated time into the list to get the average
        list_of_queueing_time_paying.append(time_inQueue_for_payment)

        #sample time spent in payment
        sampled_payment_time = numpy.random.triangular(paymentWindow_dist_min, paymentWindow_dist_mean, paymentWindow_dist_max)

        #freeze until that time is elapsed
        yield env.timeout(sampled_payment_time)

    #the payment phase is completed and the customer can move to pickup
    time_entered_for_pickup = env.now
    # request a slot for pickup
    with pickUpWindowsSlots.request() as req:
        #freeze until there is a slot available
        yield req

        time_left_for_pickup = env.now
        time_inQueue_for_pickup = time_left_for_pickup - time_entered_for_pickup
        print("Customer ", p_id, " queued for pick up for ", time_inQueue_for_pickup, " seconds",sep="")

        # add the calculated time into the list to get the average
        list_of_queueing_time_pickingUp.append(time_inQueue_for_pickup)

        #sample time spent in pickup
        sampled_pickup_time = numpy.random.lognormal(pickUpWindows_dist_mean, pickUpWindows_dist_sd)

        # freeze until that time is elapsed
        yield env.timeout(sampled_pickup_time)

#setup the simulation environment
env = simpy.Environment()

#setup simulation resources (This represents the queue max length)
#this is the main study objective and these value are to be manipulated
orderStationSlots = simpy.Resource(env, capacity=6)
paymentWindowsSlots = simpy.Resource(env, capacity=2)
pickUpWindowsSlots = simpy.Resource(env, capacity=4) #1 on the windows and 3 parking slots


#Distribution characteristics
    #Customer Inter Arrival Time
interArrival_Mean = 40
    #Ordering Station Service Time
orderingStation_dist_min=3
orderingStation_dist_max=34
orderingStation_dist_mean=16.9
orderingStation_dist_sd=7.09
    #Payment Windows Service Time
paymentWindow_dist_min=7
paymentWindow_dist_max=35
paymentWindow_dist_mean=17.7
paymentWindow_dist_sd=6.95
    #PickUp Windows Service Time
pickUpWindows_dist_min=1
pickUpWindows_dist_max=63
pickUpWindows_dist_mean=17.5
pickUpWindows_dist_sd=17.9

interArrival_Mean=  40


#list to store queueing times
list_of_queueing_time_ordering=[]
list_of_queueing_time_paying=[]
list_of_queueing_time_pickingUp=[]

#start the customer arrival generator
env.process(newCustomerGenerator(env, interArrival_Mean, orderingStation_dist_mean, paymentWindow_dist_mean, pickUpWindows_dist_mean, orderStationSlots, paymentWindowsSlots, pickUpWindowsSlots))

#run the simulation
env.run(until=2000)

#calculate and print the queueing time
print("Mean - Ordering: ", (mean(list_of_queueing_time_ordering)))
print("Mean - Paying  : ", (mean(list_of_queueing_time_paying)))
print("Mean - Picking : ", (mean(list_of_queueing_time_pickingUp)))



