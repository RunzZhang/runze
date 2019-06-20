
import os

import matplotlib.pyplot as plt
import numpy as np
import scipy.integrate
from scipy.fftpack import fft

import SBCcode
from SBCcode.Tools import SBCtools

class SiPMTrigger(object):
    def __init__(self, trig=0):
        self.trig=trig

class SiPMPlotter(object):
    def __init__(self, pmt_data, left=None, right=None,
                 default_trigger=0, runid=None, ev=None, areas=None):
        self.pmt_data = pmt_data
        self.default_trigger = default_trigger
        self.trigger = SiPMTrigger(trig=self.default_trigger)
        self.fig, self.ax= plt.subplots(nrows=2, ncols=1)
        self.runid = runid
        self.ev = ev
        self.areas=areas
        self.left = left
        self.right = right
        self.update_title()
        cid = plt.gcf().canvas.mpl_connect("key_press_event", self.key_press)

        return

    def plot_SiPM_trace(self):
        # plt.cla()
        self.ax[0].clear()
        self.ax[1].clear()
        xd = 1e9 * np.arange(pmt_data["traces"].shape[2]) * pmt_data["dt"][self.trigger.trig, 0]
        yd_0 = pmt_data["traces"][self.trigger.trig, 0, :] * pmt_data["v_scale"][self.trigger.trig, 0] + \
                  pmt_data["v_offset"][self.trigger.trig, 0]
        yd_1 = pmt_data["traces"][self.trigger.trig, 1, :] * pmt_data["v_scale"][self.trigger.trig, 1] + \
                  pmt_data["v_offset"][self.trigger.trig, 1]
        #fig,ax = plt.subplots(nrows=2, ncols=1)
        self.ax[0].plot(xd, yd_0)
        self.ax[0].plot(xd, yd_1)
        self.ax[0].set_xlabel("Time (ns)")
        self.ax[0].set_ylabel("Amp (a.u.)")

        yf0 = fft(yd_0)
        yf1 = fft(yd_1)
        xf = np.linspace(0.0, 1e9*len(xd)/(2*xd[-1]), len(xd)//2)
        self.ax[1].semilogy(xf, 2.0 / len(xd) * np.abs(yf0[0:len(xd) // 2]))
        self.ax[1].semilogy(xf, 2.0 / len(xd) * np.abs(yf1[0:len(xd) // 2]))
        self.ax[0].axvline(self.left, color="k", linewidth=2)
        self.ax[0].axvline(self.right, color="k", linewidth=2)
        dt = pmt_data["dt"][self.trigger.trig, 0]
        #plt.specgram(yd_1, NFFT=256, Fs=1e-9 /dt, )
        self.ax[1].set_xlabel("Frequency")
        self.ax[1].set_ylabel("Amplitude")
        self.update_title()
        plt.tight_layout()
        plt.draw()
        return

    def key_press(self, mpl_event):
        if mpl_event.key == "left":
            self.trigger.trig -= 1 if self.trigger.trig else -(self.pmt_data["traces"].shape[0]-1)
        elif mpl_event.key == "right":
            self.trigger.trig += 1 if self.trigger.trig < self.pmt_data["traces"].shape[0] else -(self.pmt_data["traces"].shape[0]-1)
        else:
            return
        self.plot_SiPM_trace()
        return

    def update_title(self):
        plt.suptitle("Runid: {} || Event: {} || Trigger {}\nUse Left and Right arrows to navigate.\nArea={}"\
                     .format(self.runid, self.ev, self.trigger.trig, self.areas[self.trigger.trig]))

if __name__ == "__main__":
    #raw_directory = r"C:\Users\John\Documents\SBC-18-data"
    raw_directory = "/bluearc/storage/SBC-19-data/"
    bias515lightON   = os.path.join(raw_directory, "20190610_4")
    bias515lightOFF  = os.path.join(raw_directory, "20190607_25")
    bias505lightON = os.path.join(raw_directory, "20190610_0")
    bias505lightOFF = os.path.join(raw_directory, "20190610_1")

    labels = ["51.5V - Light ON",
              "52.5V - Light OFF",
              "50.5V - Light ON",
              "50.5V - Light OFF"]

    var_array = [bias515lightON,
                 bias515lightOFF,
                 bias505lightON,
                 bias505lightOFF
                 ]

    colors = ["darkorange",
              "yellow",
              "red",
              "blue"]

    active = np.array([0,
                       1,
                       0,
                       0], dtype=bool)

    labels = np.array(labels)[active]
    var_array = np.array(var_array)[active]
    colors = np.array(colors)[active]
    nbins = 2500
    #fig, ax = plt.subplots(1, 1)
    #plot_SiPM_trace(ax, SBCcode.get_event(active_event, 0, "PMTtraces")["PMTtraces"])

    # plt.ioff()

    #areas = []
    max_times = []
    n_runs =  len(var_array)
    plt.ioff()
       #left_lim = 800
       #right_lim = 1400
    for run_ix in range(n_runs):
           sub_areas_0 = []
           sub_areas_1=[]
           max_peak_0=[]
           max_peak_1=[]
           min_peak_0=[]
           min_peak_1=[]
           trace_0=[]
           trace_1=[]
           n_0=0
           n_1=0
           m=0
           trig_num = 1

           active_event = var_array[run_ix]
           events = SBCtools.BuildEventList(active_event)
           for ev in events:
               pmt_data = SBCcode.get_event(active_event, ev, "PMTtraces", max_file_size=1300)["PMTtraces"]
               n_triggers = pmt_data["traces"].shape[0]

               sing_level_1=0

               for trig in range(n_triggers):
               #     range(n_triggers)
               #     xd = 1e9 * np.arange(pmt_data["traces"].shape[2]) * pmt_data["dt"][trig, 0]
                   lost_cut_0=pmt_data["lost_samples"][trig,0].min()
                   lost_cut_1=pmt_data["lost_samples"][trig,1].min()

                   yd_0 = pmt_data["traces"][trig, 0, :lost_cut_0] * pmt_data["v_scale"][trig, 0] + \
                          pmt_data["v_offset"][trig, 0]
                   yd_1 = pmt_data["traces"][trig, 1, :lost_cut_1] * pmt_data["v_scale"][trig, 1] + \
                      pmt_data["v_offset"][trig, 1]
                   avr_0 = np.average(yd_0[:60])
                   avr_1=np.average(yd_1[:60])

                   yd_0_clr=yd_0-avr_0
                   yd_1_clr=yd_1-avr_1

                   sub_areas_el_0 = sum(yd_0_clr[:lost_cut_0])
                   sub_areas_el_1 = sum(yd_1_clr[:lost_cut_1])


                   maxpk_0 = yd_0_clr.max()
                   minpk_0 = yd_0_clr.min()
                   maxpk_1 = yd_1_clr.max()
                   minpk_1 = yd_1_clr.min()



                   if maxpk_0>0.005 and minpk_0>-0.011 and sub_areas_el_0>0.0:

                       trace_0.append(yd_0_clr)
                       n_0 = n_0 + 1
                       max_peak_0.append(maxpk_0)
                       min_peak_0.append(minpk_0)
                       sub_areas_0.append(sub_areas_el_0)

                   if maxpk_1>0.005 and minpk_1>-0.011 and sub_areas_el_1>0.0:

                       trace_1.append(yd_1_clr)
                       n_1 = n_1 + 1
                       max_peak_1.append(maxpk_1)
                       min_peak_1.append(minpk_1)
                       sub_areas_1.append(sub_areas_el_1)

               m=m+1
               print("now we are in event "+str(m)+" when " + str(labels[run_ix]))


           for i in range(n_0):
               plt.plot(trace_0[i])
           plt.title("when " + str(labels[run_ix])+" valid traces in channel 0")
           plt.xlabel("time unit")
           plt.ylabel("signal_v")
           plt.show()
           plt.clf()

           plt.hist(sub_areas_0,bins=nbins)
           plt.title("when " + str(labels[run_ix])+" areas histogram in channel 0")
           plt.xlabel("areas")
           plt.ylabel("counts")
           plt.show()
           plt.clf()

           plt.scatter(max_peak_0,sub_areas_0)
           plt.title("when " + str(labels[run_ix])+" max peak vs area in channel_0")
           plt.xlabel("max peak")
           plt.ylabel("areas per trigger")
           plt.show()
           plt.clf()

           plt.title("when " + str(labels[run_ix])+" max peak vs min peak in channel_0")
           plt.xlabel("min peak")
           plt.ylabel("max peak")
           plt.scatter(min_peak_0,max_peak_0)
           plt.show()

           plt.clf()

           for j in range(n_1):
               plt.plot(trace_1[j])
           plt.title("when " + str(labels[run_ix])+" valid traces in channel 1")
           plt.xlabel("time unit")
           plt.ylabel("signal_v")
           plt.show()
           plt.clf()

           plt.hist(sub_areas_1, bins=nbins)
           plt.title("when " + str(labels[run_ix])+" areas histogram in channel 1")
           plt.xlabel("areas")
           plt.ylabel("counts")
           plt.show()
           plt.clf()

           plt.scatter(max_peak_1,sub_areas_1)
           plt.title("when " + str(labels[run_ix])+" max peak vs area in channel_1")
           plt.xlabel("max peak")
           plt.ylabel("areas per trigger")
           plt.show()
           plt.clf()

           plt.scatter(min_peak_1,max_peak_1)
           plt.title("when " + str(labels[run_ix])+" max peak vs min peak in channel_1")
           plt.xlabel("min peak")
           plt.ylabel("max peak")
           plt.show()

           print("channel_0's valid count number are " + str(n_0)+" when " + str(labels[run_ix]))
           print("channel_1's valid count number are " + str(n_1)+" when " + str(labels[run_ix]))
           unit_t=16.5867
           rate_0=n_0/(m*unit_t)
           rate_1=n_1/(m*unit_t)
           print("total event number is " + str(m)+" when " + str(labels[run_ix]))
           print("dark count rate in channel 0 is "+str(rate_0)+ " Hz"+" when " + str(labels[run_ix]))
           print( "dark count rate in channel 1 is " + str(rate_1) + " Hz"+" when " + str(labels[run_ix]))
           # print(trig_num)


           # plt.hist(hist_1, bins=nbins, fill=False, color=colors, histtype="bar", stacked=False)
           # plt.scatter(min_peak,max_peak)
           # plt.show()
           #plt.hist(areas, bins=nbins, fill=False, color=colors, histtype="step", stacked=False, label=labels)
           #plt.legend(loc="upper right")
          # plt.suptitle("Areas")
           #plt.yscale("log")

       # plt.figure()
       # plt.hist(max_times, bins=nbins, fill=False, color=colors, histtype="step", stacked=False)
       # plt.legend(labels)
       # plt.suptitle("Time of max")
       # plt.ion()

    # plt.grid()
    # plt.show()
    #


    # areas = []
    # max_times = []
    # n_runs =  len(var_array)
    # plt.ioff()
    # left_lim = 800
    # right_lim = 1400
    # for run_ix in range(n_runs):
    #     sub_areas = []
    #     sub_max_times = []
    #     active_event = var_array[run_ix]
    #     events = SBCtools.BuildEventList(active_event)
    #     for ev in events:
    #         pmt_data = SBCcode.get_event(active_event, ev, "PMTtraces", max_file_size=1300)["PMTtraces"]
    #         n_triggers = pmt_data["traces"].shape[0]
    #         for trig in range(n_triggers):
    #             xd = 1e9 * np.arange(pmt_data["traces"].shape[2]) * pmt_data["dt"][trig, 0]
    #             yd_0 = pmt_data["traces"][trig, 0, :] * pmt_data["v_scale"][trig, 0] + \
    #                    pmt_data["v_offset"][trig, 0]
    #             yd_1 = pmt_data["traces"][trig, 1, :] * pmt_data["v_scale"][trig, 1] + \
    #                    pmt_data["v_offset"][trig, 1]
    #             good_indices = (xd < right_lim) & (xd > left_lim)
    #             avg = np.average(yd_0[:left_lim])
    #             #pmt_area = scipy.integrate.trapz(yd_1[good_indices]-avg,
    #             #                                 dx=1e9*pmt_data["dt"][trig, 1])
    #             # if np.any(yd_0 > 0.15):
    #             #     pmt_area = -1.
    #             # else:
    #             pmt_area = np.sum(yd_0[left_lim:right_lim]-avg)
    #             print(np.sum(yd_0))
    #             sub_areas.append(pmt_area)
    #             sub_max_times.append(1e9 * pmt_data["dt"][trig, 0] * np.argmax(pmt_data["traces"][trig, 0, :]))
    #
    #         plotter = SiPMPlotter(pmt_data, runid=os.path.basename(active_event), ev=ev,
    #                               areas=sub_areas,
    #                               left=left_lim, right=right_lim)
    #
    #         plotter.plot_SiPM_trace()
    #         plt.show()
    #     areas.append(sub_areas)
    #     max_times.append(sub_max_times)
    #
    # plt.hist(areas, bins=nbins, fill=False, color=colors, histtype="step", stacked=False, label=labels)
    # plt.legend(loc="upper right")
    # plt.suptitle("Areas")
    # plt.yscale("log")
    #
    # # plt.figure()
    # # plt.hist(max_times, bins=nbins, fill=False, color=colors, histtype="step", stacked=False)
    # # plt.legend(labels)
    # # plt.suptitle("Time of max")
    # #plt.ion()
    # plt.grid()
    # plt.show()
    #
    pass
