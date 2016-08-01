## Experiment parameters -------------------------

sim_duration = 2.0
packet_size = 1460 #bytes
num_priorities = 5
priorities = range(num_priorities)
qlimit = 1000
first_pause = 0.1
B = 10
packet_thresholds = range(int(first_pause * qlimit), qlimit, 2*B)
byte_thresholds = [packet_size * x for x in packet_thresholds]

burst_size = 1 #packets
k = 0.9
output_rate = 800000000 #bits/s = 0.1 Gb/s
input_rate = output_rate * 1000
burst_interval = (len(priorities) * burst_size * packet_size) / (k * output_rate / 8)



link_delay = (B * packet_size * 8) / input_rate
trace_rate = 0.0001
percentile = 95.0
repetitions = 10
trace = "queue.tr"
exp_path = "results/exp8/"
exp_trace = "exp.tr"
exp_priorities = [1, 5, 10, 50, 100, 500, 1000, 5000, 10000]
trace_delim = "\t"
seed = range(repetitions)