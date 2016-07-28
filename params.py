## Experiment parameters -------------------------
seed = 4
sim_duration = 0.2
packet_size = 1460 #bytes
num_priorities = 200
priorities = range(num_priorities)
qlimit = 1000
first_pause = 0.1
B = 10
packet_thresholds = range(int(first_pause * qlimit), qlimit, 2*B)
byte_thresholds = [packet_size * x for x in packet_thresholds]

burst_size = 1000 #packets
k = 0.9
output_rate = 8000000000 #bits/s = 1 Gb/s
input_rate = output_rate * 1000
burst_interval = (len(priorities) * burst_size * packet_size) / (k * output_rate / 8)



link_delay = (B * packet_size * 8) / input_rate
trace_rate = 0.00001
trace = "queue.tr"
trace_delim = "\t"