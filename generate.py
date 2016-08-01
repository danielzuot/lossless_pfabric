import simpy
import params
import numpy as np
from random import expovariate, seed
from model import PacketGenerator, PacketSink, PrioritySwitchPort, Checkpoint, CheckpointAction, PortMonitor

# def simulate(priorities, trace, burst_interval):
#     with open(trace, 'a') as tr:
#         tr.write(str(len(priorities)))
#         for i in range(params.repetitions):
#             print i
#             ## Setup experiment   ----------------------
#             env = simpy.Environment()  # Create the SimPy environment
#             # Create the packet generators and sink
#             ps = PacketSink(env, debug=False)  # debugging enable for simple output
#             pgs = []
#             for priority in priorities:
#                 pgs.append(PacketGenerator(env, priority, params.burst_size, lambda: expovariate(1.0/burst_interval), lambda: params.packet_size, flow_id=priority, priority=priority))

#             switch1 = PrioritySwitchPort(env, rate=params.input_rate, qlimit=None, pause=False, debug=False)
#             switch2 = PrioritySwitchPort(env, rate=params.output_rate, qlimit=params.qlimit * params.packet_size, pause=True, debug=False)

#             checkpoints = []
#             checkpoints.append(Checkpoint(-1, CheckpointAction.NONE))
#             checkpoints.append(Checkpoint(params.qlimit, CheckpointAction.NONE))
#             for r in range(0, len(params.packet_thresholds), 2):
#                 # start with the resumes
#                 checkpoints.append(Checkpoint(params.packet_thresholds[r] * params.packet_size, CheckpointAction.RESUME))
#             for p in range(1, len(params.packet_thresholds), 2):
#                 # then the pauses
#                 checkpoints.append(Checkpoint(params.packet_thresholds[p] * params.packet_size, CheckpointAction.PAUSE))

#             checkpoints.sort()
#             switch2.checkpoints = checkpoints
#             switch2.link_delay = params.link_delay
#             switch2.back = switch1

#             # pm1 = PortMonitor(env, switch1, lambda: trace_rate, tr1_file)
#             pm2 = PortMonitor(env, switch2, lambda: params.trace_rate, trace, True)

#             # Wire packet generators and sink together
#             for pg in pgs:
#                 pg.out = switch1
#             switch1.out = switch2
#             switch2.out = ps


#             ## Simulate  ----------------------------------
#             seed(params.seed[i])
#             while env.peek() < params.sim_duration:
#                 env.step()
#             tr.write(params.trace_delim)
#             tr.write(str(np.percentile(pm2.queue_sizes, params.percentile)))
#             tr.write(params.trace_delim)
#             tr.write(str(np.percentile(pm2.queue_sizes, 100)))
#         tr.write('\n')

# for num in params.exp_priorities:
#     burst_interval = (num * params.burst_size * params.packet_size) / (params.k * params.output_rate / 8)
#     simulate(range(num), params.exp_path + params.exp_trace, burst_interval)

def simulate(priorities, trace, burst_interval):
    ## Setup experiment   ----------------------
    env = simpy.Environment()  # Create the SimPy environment
    # Create the packet generators and sink
    ps = PacketSink(env, debug=False)  # debugging enable for simple output
    pgs = []
    for priority in priorities:
        pgs.append(PacketGenerator(env, priority, params.burst_size, lambda: expovariate(1.0/burst_interval), lambda: params.packet_size, flow_id=priority, priority=priority))

    switch1 = PrioritySwitchPort(env, rate=params.input_rate, qlimit=None, pause=False, debug=False)
    switch2 = PrioritySwitchPort(env, rate=params.output_rate, qlimit=params.qlimit * params.packet_size, pause=True, debug=False)

    checkpoints = []
    checkpoints.append(Checkpoint(-1, CheckpointAction.NONE))
    checkpoints.append(Checkpoint(params.qlimit, CheckpointAction.NONE))
    for r in range(0, len(params.packet_thresholds), 2):
        # start with the resumes
        checkpoints.append(Checkpoint(params.packet_thresholds[r] * params.packet_size, CheckpointAction.RESUME))
    for p in range(1, len(params.packet_thresholds), 2):
        # then the pauses
        checkpoints.append(Checkpoint(params.packet_thresholds[p] * params.packet_size, CheckpointAction.PAUSE))

    checkpoints.sort()
    switch2.checkpoints = checkpoints
    switch2.link_delay = params.link_delay
    switch2.back = switch1

    # pm1 = PortMonitor(env, switch1, lambda: trace_rate, tr1_file)
    pm2 = PortMonitor(env, switch2, lambda: params.trace_rate, trace, True)

    # Wire packet generators and sink together
    for pg in pgs:
        pg.out = switch1
    switch1.out = switch2
    switch2.out = ps


    ## Simulate  ----------------------------------
    seed(0)
    while env.peek() < params.sim_duration:
        env.step()

simulate(params.priorities, params.trace, params.burst_interval)

