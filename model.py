import simpy
import random
import bisect
import threading
from functools import total_ordering
from enum import Enum
import json
import params

@total_ordering
class Packet(object):
    """ A very simple class that represents a packet.
        This packet will run through a queue at a switch output port.

        Parameters
        ----------
        time : float
            the time the packet arrives at the output queue.
        size : float
            the size of the packet in bytes
        id : int
            an identifier for the packet
        src, dst : int
            identifiers for source and destination
        flow_id : int
            small integer that can be used to identify a flow
    """
    def __init__(self, time, size, id, src="a", dst="z", flow_id=0, priority=0):
        self.time = time
        self.size = size
        self.id = id
        self.src = src
        self.dst = dst
        self.flow_id = flow_id
        self.priority = priority

    def __eq__(self, other):
        return self.priority == other.priority

    def __lt__(self, other):
        return self.priority < other.priority

    def __repr__(self):
        return "id: {}, src: {}, time: {}, size: {}, priority: {}".\
            format(self.id, self.src, self.time, self.size, self.priority)

class PacketGenerator(object):
    """ Generates packets with given inter-arrival time distribution.
        Set the "out" member variable to the entity to receive the packet.

        Parameters
        ----------
        env : simpy.Environment
            the simulation environment
        adist : function
            a no parameter function that returns the successive inter-arrival times of the packets
        sdist : function
            a no parameter function that returns the successive sizes of the packets
        initial_delay : number
            Starts generation after an initial delay. Default = 0
        finish : number
            Stops generation at the finish time. Default is infinite


    """
    def __init__(self, env, id,  adist, sdist, initial_delay=0, finish=float("inf"), flow_id=0, priority=0):
        self.id = id
        self.env = env
        self.adist = adist
        self.sdist = sdist
        self.initial_delay = initial_delay
        self.finish = finish
        self.out = None
        self.packets_sent = 0
        self.action = env.process(self.run())  # starts the run() method as a SimPy process
        self.flow_id = flow_id
        self.priority = priority

    def run(self):
        """The generator function used in simulations.
        """
        yield self.env.timeout(self.initial_delay)
        while self.env.now < self.finish:
            # wait for next transmission
            yield self.env.timeout(self.adist())
            self.packets_sent += 1
            p = Packet(self.env.now, self.sdist(), self.packets_sent, src=self.id, flow_id=self.flow_id, priority=self.priority)
            self.out.put(p)

class PacketSink(object):
    """ Receives packets and collects delay information into the
        waits list. You can then use this list to look at delay statistics.

        Parameters
        ----------
        env : simpy.Environment
            the simulation environment
        debug : boolean
            if true then the contents of each packet will be printed as it is received.
        rec_arrivals : boolean
            if true then arrivals will be recorded
        absolute_arrivals : boolean
            if true absolute arrival times will be recorded, otherwise the time between consecutive arrivals
            is recorded.
        rec_waits : boolean
            if true waiting time experienced by each packet is recorded
        selector: a function that takes a packet and returns a boolean
            used for selective statistics. Default none.

    """
    def __init__(self, env, rec_arrivals=False, absolute_arrivals=False, rec_waits=True, debug=False, selector=None):
        self.store = simpy.Store(env)
        self.env = env
        self.rec_waits = rec_waits
        self.rec_arrivals = rec_arrivals
        self.absolute_arrivals = absolute_arrivals
        self.waits = []
        self.arrivals = []
        self.debug = debug
        self.action = env.process(self.run())  # starts the run() method as a SimPy process
        self.packets_rec = 0
        self.bytes_rec = 0
        self.selector = selector

    def run(self):
        last_arrival = 0.0
        while True:
            msg = (yield self.store.get())
            if not self.selector or self.selector(msg):
                now = self.env.now
                if self.rec_waits:
                    self.waits.append(self.env.now - msg.time)
                if self.rec_arrivals:
                    if self.absolute_arrivals:
                        self.arrivals.append(now)
                    else:
                        self.arrivals.append(now - last_arrival)
                    last_arrival = now
                self.packets_rec += 1
                self.bytes_rec += msg.size
                if self.debug:
                    print "{}: \t sink: \t\t{}".format(self.env.now, msg)

    def put(self, pkt):
        self.store.put(pkt)

class CheckpointAction(Enum):
    PAUSE = 1
    RESUME = 2
    NONE = 3

@total_ordering
class Checkpoint(object):

    def __init__(self, thresh, action):
        self.thresh = thresh
        self.action = action
        self.active = False

    def __lt__(self, other):
        return self.thresh < other.thresh

    def __eq__(self, other):
        return self.thresh == other.thresh

    def __repr__(self):
        return "thresh: {}, action: {}, active: {}".format(self.thresh, self.action, self.active)

class PrioritySwitchPort(object):
    """ Models a priority switch output port with a given rate and buffer size limit in bytes.
        Set the "out" member variable to the entity to receive the packet.

        Parameters
        ----------
        env : simpy.Environment
            the simulation environment
        rate : float
            the bit rate of the port
        link_delay: float
            units of time it takes a pause/resume to reach this switch
        qlimit : integer (or None)
            a buffer size limit in bytes for the queue (does not include items in service).

        out must be initialized before simulation
        if pause is set:
            link_delay, back, checkpoints must also be initialized

    """
    def __init__(self, env, rate, qlimit=None, pause=False, debug=False):
        self.queue = []
        self.store = simpy.Store(env) # used only for a count of items in the queue
        self.rate = rate
        self.link_delay = 0
        self.env = env
        self.out = None
        self.back = None
        self.packets_rec = 0
        self.packets_drop = 0
        self.drop_list = []
        self.qlimit = qlimit
        self.byte_size = 0  # Current size of the queue in bytes
        self.debug = debug
        self.pause = pause
        self.pause_sent = []
        self.pause_rec = []
        self.checkpoints = []
        self.prev_cp = 0
        self.next_cp = 1
        self.busy = 0  # Used to track if a packet is currently being sent
        self.unpause_check = env.event()
        self.action = env.process(self.run())  # starts the run() method as a SimPy process

    def run(self):
        while True:
            msg = (yield self.store.get())
            self.busy = 1
            pkt = self.queue[-1]
            if self.pause_rec:
                # something's paused, need to check
                if pkt.priority > self.pause_rec[-1]:
                    # alright, important enough to let through
                    self.send_pkt(pkt)
                    yield self.env.timeout(pkt.size*8.0/self.rate)
                else:
                    # can't let you through, putting token back into the store
                    self.store.put(pkt)
                    yield self.unpause_check
            else:
                self.send_pkt(pkt)
                yield self.env.timeout(pkt.size*8.0/self.rate)
            self.busy = 0

    def send_pkt(self, pkt):
        pkt = self.queue.pop()
        self.byte_size -= pkt.size
        if self.pause:
            prev_cp = self.checkpoints[self.prev_cp]
            next_cp = self.checkpoints[self.next_cp]
            if self.byte_size <= prev_cp.thresh:
                # dipped below a threshold
                if prev_cp.action == CheckpointAction.RESUME:
                    if next_cp.active:
                        # need to send resume upstream
                        self.checkpoints[self.next_cp].active = False
                        self.pause_sent.pop()
                        self.env.process(self.send_resume())
                # regardless need to update prev and next pointers
                self.prev_cp -= 1
                self.next_cp -= 1
        self.out.put(pkt)

    def put(self, pkt):
        self.packets_rec += 1
        self.byte_size += pkt.size
        bisect.insort_left(self.queue, pkt)
        self.store.put(pkt)
        self.unpause_check.succeed()
        self.unpause_check = self.env.event()

        if self.qlimit is None:
            return

        while (self.byte_size > self.qlimit):
            msg = self.store.get()
            self.packets_drop += 1
            self.byte_size -= self.queue[0].size
            self.drop_list.append(self.queue[0])
            del self.queue[0]

        if self.pause:
            prev_cp = self.checkpoints[self.prev_cp]
            next_cp = self.checkpoints[self.next_cp]
            if self.byte_size <= prev_cp.thresh:
                # dipped below a threshold
                # this is very unlikely
                if prev_cp.action == CheckpointAction.RESUME:
                    if next_cp.active:    
                        # need to send resume upstream
                        self.checkpoints[self.next_cp].active = False
                        self.pause_sent.pop()
                        self.env.process(self.send_resume())
                # regardless need to update pointers
                self.prev_cp -= 1
                self.next_cp -= 1
            elif self.byte_size > next_cp.thresh:
                # hit the next threshold
                if next_cp.action == CheckpointAction.PAUSE:
                    if not next_cp.active:
                        # need to send pause upstream:
                            # to determine the pause value, we need to determine what the highest remaining priority will be 
                            # when we eventually resume this pause
                            # so we check the value of the packet in the queue 'at' the resume threshold (with small technicalities)
                        resume_threshold = prev_cp.thresh
                        queue_size = 0
                        hrp = -1
                        for i in range(len(self.queue)):
                            queue_size += self.queue[i].size
                            if queue_size > resume_threshold:
                                # then this packet is the HRP
                                hrp = self.queue[i-1].priority
                                break
                        self.checkpoints[self.next_cp].active = True
                        self.pause_sent.append(hrp)
                        self.env.process(self.send_pause(hrp))
                # regardless need to update pointers
                self.prev_cp += 1
                self.next_cp += 1
        return

    def send_pause(self, priority):
        yield self.env.timeout(self.link_delay)
        self.back.pause_rec.append(priority)

    def send_resume(self):
        yield self.env.timeout(self.link_delay)
        self.back.pause_rec.pop()
        self.back.unpause_check.succeed()
        self.back.unpause_check = self.env.event()

class PortMonitor(object):
    """ A monitor for a SwitchPort. Looks at the number of items in the SwitchPort
        in service + in the queue and records that info in the sizes[] list. The
        monitor looks at the port at time intervals given by the distribution dist.

        Parameters
        ----------
        env : simpy.Environment
            the simulation environment
        port : SwitchPort
            the switch port object to be monitored.
        dist : function
            a no parameter function that returns the successive inter-lookup times
        trace : file
            the file where the trace will be recorded

    """
    def __init__(self, env, port, dist, trace):
        self.port = port
        self.env = env
        self.dist = dist
        self.trace = trace
        self.action = env.process(self.run())

    def run(self):
        with open(self.trace, 'w') as tr:
            # tr.write("time byte_size queue pause_sent pause_rec prev_cp next_cp drops\n")
            while True:
                yield self.env.timeout(self.dist())
                q_makeup = []
                for priority in params.priorities:
                    subqueue = [pkt.size if (pkt.priority == priority) else 0 for pkt in self.port.queue]
                    q_makeup.append(sum(subqueue))

                tr.write(str(self.env.now))
                tr.write(params.trace_delim)
                tr.write(str(self.port.byte_size))
                tr.write(params.trace_delim)
                for i in range(len(params.priorities)):
                    tr.write(str(q_makeup[i]))
                    tr.write(params.trace_delim)
                if self.port.pause_sent:
                    tr.write(str(self.port.pause_sent[-1]))
                else:
                    tr.write(str(-1))
                tr.write(params.trace_delim)
                tr.write(str(self.port.packets_drop))
                tr.write("\n")

            
            