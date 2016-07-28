import numpy as np
import params
import matplotlib.pyplot as plt
import sys
import json

################### preprocess trace ##################
# time byte_size makeups largest_pause_sent packet_drops
trace_data = np.loadtxt(params.trace, delimiter=params.trace_delim)


################### plot queue length over time ##################
fig = plt.figure()
byte_size_offset = 1
plt.plot(trace_data[:,0], trace_data[:,byte_size_offset])
# axes = plt.gca()
# axes.set_xlim([0.4, 0.8])
# axes.set_ylim([0,100])
plt.title('Length of queue')
plt.xlabel('time (s)')
plt.ylabel('size (bytes)')
plt.show()


################### stackplot of queue makeup over time ##################
fig, axarr = plt.subplots(2, sharex=True)
makeup_offset = 2
for thresh in params.byte_thresholds:
    axarr[0].axhline(y=thresh)
axarr[0].stackplot(np.transpose(trace_data[:,0]), np.transpose(trace_data[:,makeup_offset:makeup_offset+len(params.priorities)]))

axarr[0].set_title('Makeup of queue')
axarr[0].set_ylabel('size (bytes)')


################### plot pause thresholds over time ##################
pauses_offset = 2 + len(params.priorities)
axarr[1].plot(trace_data[:,0], trace_data[:,pauses_offset])
axarr[1].set_ylim([-2,params.priorities[-1]+1])
axarr[1].set_title('Pauses sent')
axarr[1].set_xlabel('time (s)')
axarr[1].set_ylabel('Pause threshold')
plt.show()

################### plot drops over time ##################
fig = plt.figure()
drops_offset = 3 + len(params.priorities)
plt.plot(trace_data[:,0], trace_data[:,drops_offset])
# axes = plt.gca()
# axes.set_xlim([0.4, 0.8])
# axes.set_ylim([0,100])
plt.title('Drops')
plt.xlabel('time (s)')
plt.ylabel('Drops (packets)')
plt.show()

