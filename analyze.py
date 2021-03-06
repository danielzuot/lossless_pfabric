import numpy as np
import params
import matplotlib.pyplot as plt
import sys
import json

################### preprocess trace ##################
# time byte_size makeups largest_pause_sent packet_drops
trace_data = np.loadtxt(params.trace, delimiter=params.trace_delim)
# exp_data = np.loadtxt(params.exp_path + params.exp_trace, delimiter=params.trace_delim)

# ################### plot queue length over time ##################
# fig = plt.figure()
# byte_size_offset = 1
# plt.plot(trace_data[:,0], trace_data[:,byte_size_offset])
# for thresh in params.byte_thresholds:
#     plt.axhline(y=thresh)
# # axes = plt.gca()
# # axes.set_xlim([0.4, 0.8])
# # axes.set_ylim([0,100])
# plt.title('Length of queue')
# plt.xlabel('time (s)')
# plt.ylabel('size (bytes)')
# plt.show()


################# stackplot of queue makeup over time ##################
fig, axarr = plt.subplots(2, sharex=True)
makeup_offset = 2
for thresh in params.byte_thresholds[1::2]:
    axarr[0].axhline(y=thresh, linewidth=1, alpha=0.4)
axarr[0].stackplot(np.transpose(trace_data[:,0]), np.transpose(trace_data[:,makeup_offset:makeup_offset+len(params.priorities)]))

# Put a legend to the right of the current axis
# axarr[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
axarr[0].set_ylim([0,600000])
axarr[0].set_title('Makeup of queue')
axarr[0].set_ylabel('size (bytes)')


################## plot pause thresholds over time ##################
pauses_offset = 2 + len(params.priorities)
axarr[1].plot(trace_data[:,0], trace_data[:,pauses_offset])
axarr[1].set_ylim([-2,params.priorities[-1]+1])
axarr[1].set_title('Pauses sent')
axarr[1].set_xlabel('time (s)')
axarr[1].set_ylabel('Pause threshold')
plt.show()

################### plot drops over time ##################
# fig = plt.figure()
# drops_offset = 3 + len(params.priorities)
# plt.plot(trace_data[:,0], trace_data[:,drops_offset])
# # axes = plt.gca()
# # axes.set_xlim([0.4, 0.8])
# # axes.set_ylim([0,100])
# plt.title('Drops')
# plt.xlabel('time (s)')
# plt.ylabel('Drops (packets)')
# plt.show()

################### 95th percentile queue size vs number of priority levels ##################
# fig = plt.figure()
# percentile_data = exp_data[:,1::2]
# print percentile_data
# percentile_means = np.mean(percentile_data, axis=1)
# percentile_std = np.std(percentile_data, axis=1)
# plt.errorbar(np.log(exp_data[:,0]), percentile_means, yerr=percentile_std)

# for thresh in params.byte_thresholds[1::2]:
#     plt.axhline(y=thresh, linewidth=1, alpha=0.4)
# # axes = plt.gca()
# # axes.set_xlim(0, params.exp_priorities[-1]+300)
# # axes.set_ylim([0,100])
# plt.title('Queue occupancies across priority levels')
# plt.xlabel('Priority levels')
# plt.ylabel('95th percentile queue size (bytes)')
# plt.savefig(params.exp_path+'/log_percentile_queue_sizes.png', bbox_inches='tight')
# plt.show()

# ################### plot max queue size vs number of priority levels ##################

# fig = plt.figure()
# max_data = exp_data[:,2::2]
# max_means = np.mean(max_data, axis=1)
# max_std = np.std(max_data, axis=1)
# plt.errorbar(np.log(exp_data[:,0]), max_means, yerr=max_std)

# for thresh in params.byte_thresholds[1::2]:
#     plt.axhline(y=thresh, linewidth=1, alpha=0.4)
# # axes = plt.gca()
# # axes.set_xlim(0, params.exp_priorities[-1]+300)
# # axes.set_ylim([0,100])
# plt.title('Queue occupancies across priority levels')
# plt.xlabel('Priority levels')
# plt.ylabel('Max queue size (bytes)')
# plt.savefig(params.exp_path+'/log_max_queue_sizes.png', bbox_inches='tight')
# plt.show()


