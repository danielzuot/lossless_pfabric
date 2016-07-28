## Experiment parameters -------------------------
seed = 4
sim_duration = 500
packet_size = 1460 #bytes
generate_rate = 0.1 #=> 10 pkt/s for each generator
input_rate = 23360*5 #bits/s = 2920*5 bytes/s
output_rate = 11680 #bits/s = 1460 bytes/s
qlimit = 100*packet_size
link_delay = 2.5 #seconds => B = 5 pkts
trace_rate = 0.5
trace = "queue.tr"
trace_delim = "\t" # can't be anything in a json
priorities = [0, 1, 2, 3, 4]
packet_thresholds = [45, 55, 60, 65, 70, 75, 80, 85, 90, 95]
byte_thresholds = [packet_size * x for x in packet_thresholds]