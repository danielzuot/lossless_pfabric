import simpy
import params
from random import expovariate, seed
from model import PacketGenerator, PacketSink, PrioritySwitchPort, Checkpoint, CheckpointAction, PortMonitor

## Setup experiment   ----------------------
env = simpy.Environment()  # Create the SimPy environment
# Create the packet generators and sink
ps = PacketSink(env, debug=False)  # debugging enable for simple output

pg0 = PacketGenerator(env, "A", lambda: expovariate(params.generate_rate), lambda: params.packet_size, flow_id=0, priority=0)
pg1 = PacketGenerator(env, "B", lambda: expovariate(params.generate_rate), lambda: params.packet_size, flow_id=1, priority=1)
pg2 = PacketGenerator(env, "C", lambda: expovariate(params.generate_rate), lambda: params.packet_size, flow_id=2, priority=2)
pg3 = PacketGenerator(env, "D", lambda: expovariate(params.generate_rate), lambda: params.packet_size, flow_id=3, priority=3)
pg4 = PacketGenerator(env, "E", lambda: expovariate(params.generate_rate), lambda: params.packet_size, flow_id=4, priority=4)


switch1 = PrioritySwitchPort(env, rate=params.input_rate, qlimit=None, pause=False, debug=False)
switch2 = PrioritySwitchPort(env, rate=params.output_rate, qlimit=params.qlimit, pause=True, debug=False)

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
pm2 = PortMonitor(env, switch2, lambda: params.trace_rate, params.trace)

# Wire packet generators and sink together
pg0.out = switch1
pg1.out = switch1
pg2.out = switch1
pg3.out = switch1
pg4.out = switch1
switch1.out = switch2
switch2.out = ps


## Simulate  ----------------------------------
seed(params.seed)
while env.peek() < 500:
    # print env.peek()
    env.step()



