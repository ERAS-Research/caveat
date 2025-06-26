# Copyright (C) 2025 ERAS Research Group
# Author(s): Murray Ferris, Torsten Reuschel

import matplotlib.pyplot as plt
import mpld3
import os
from pathlib import Path
import numpy as np
import plotly as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
### FIXME: ignore deprecation warnings from mpld3 library
# patch has been merged upstream, remove this section once released,
# cf. https://github.com/mpld3/mpld3/issues/530
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning, module='mpld3')
### FIXME-END ##

html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{report_title}</title>
    </head>
    <body>
        <h1>{report_title}</h1>

        {plot_divs}
    </body>
    </html>
    """


def get_html_plot_data(testname, data_dict, axis_dict=None, truncate=False):
    """Stringify plot data for HTML reporting
    """
    plot_data = "<h2>{:s}</h2>".format(testname)

    if axis_dict:
        fig = px.figure(figsize=(10,3))
        height = 0

        for signal in axis_dict:
            data = axis_dict[signal]

            for key in data:
                signal_time = data[key]
                print("time for signal ", signal, "is ", key )
                signal_time, time_before, len_message, time_after,rgb = key, *data[key]
                plt.text(0, height + .3, signal)
                plt.step(
                    [signal_time, time_before],
                    [height, height],
                    color='tab:blue')

                plt.fill_between(
                    [time_before, time_before + 3],
                    height - .2,
                    [height + .2, height + .2],
                    color=rgb,
                    step='pre')

                if len_message > 3:
                    plt.fill_between(
                        [time_before + 3, time_before + len_message],
                        height - .2,
                        [height + .2, height + .2],
                        color='k',
                        step='pre')
                height -= 1
        plt.ylim(height-1, 1)
        plot_data += fig.to_html()

    if data_dict:


        fig= make_subplots(rows=len(data_dict), cols=1)


        dict_index=0
        global_t=[]
        for key, data in data_dict.items():
            #sanity check: skip monitors that did not record events
            if len(data) < 2:
                continue
            #prepare data for plotting: extract and sanitize
            dt, dx = list(zip(*data))
            global_t += [dt]

        global_t = [elem for partlist in global_t for elem in partlist]
        #extract unique samples
        global_t = sorted(np.unique(global_t))


        for key, data in data_dict.items():
            #sanity check: skip monitors that did not record events
            if len(data) < 2:
                continue
            #prepare data for plotting: extract and sanitize
            dt, dx = list(zip(*data))
            dt = list(dt)
            dx = list(dx)
            for ii, xx in enumerate(dx):
                if ('z' in str(xx)) or ('x' in str(xx)):
                    dx[ii] = float('nan')
                else:
                    dx[ii] = float(xx)
            #plot data

            print("dT:", dt)
            dt=[reverse_lookup_dt(xx, global_t) for xx in dt]
            print('DT IS', dt)
            fig.add_trace(
            # go.Scatter(x=[reverse_lookup_dt(xx, global_t) for xx in dt], y=dx), row=dict_index+1, col=1)
            # hop = len(global_t)//
             go.Scatter(x=dt, y=dx, mode='lines', line_shape='hv', name=key), row=dict_index+1, col=1, )
            # ax[dict_index].set_xticks(range(len(global_t))[::hop], global_t[::hop])
            # plot_data += key
            dict_index+=1
        # plt.xlabel("Time (ns)")
        # plt.show()
        # ax[-1].set_xticklabels([str(xx) for xx in global_t])
        fig.update_layout(height=200*len(data_dict), title_text="CAVEAT")
        plot_data += fig.to_html()
        print(len)
        return plot_data


def make_report(testname: str, cfg_plot: dict,
        report_title: str='CAVEAT signal capture',
        outfilepath: str='../results/dynamic/'):
    """Compile stringified matplotlib figures into HTML report
    """
    #create report
    plot_data = get_html_plot_data(testname, **cfg_plot)
    html_report = html_template.format(
                    report_title=report_title,
                    plot_divs=plot_data)

    #write report to file
    outfilesubdir = os.path.split(testname)[0]
    Path(os.path.join(outfilepath, outfilesubdir)).mkdir(parents=True, exist_ok=True)
    with open('{:s}/{:s}.html'.format(outfilepath, testname), 'w') as f:
        f.write(html_report)







        # data_raw_dt = [[1,2,3,5],[100,101,106],[5000,5010,5011],range(10000,10010)]
def active_interval(data_in, max_skip=10):
            #flatten list
            data = [elem for partlist in data_in for elem in partlist]
            #extract unique samples
            data = sorted(np.unique(data))
            #find distinct intervals
            out = []
            out+= [data[0], data[1]]
            for elem in data[2:]:
                if elem <= out[-1] + max_skip:
                    out[-1] = elem
                else:
                    out+=[elem, elem]
            return list(zip(out[::2], out[1::2]))

# print( active_interval(data_raw_dt) )
def reverse_lookup_dt(dt, global_t):
    return np.where(np.array(global_t)==dt)[0][0]