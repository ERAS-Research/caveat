# Copyright (C) 2025 ERAS Research Group
# Author(s): Murray Ferris, Torsten Reuschel

import matplotlib.pyplot as plt
import json
import mpld3
import os
import wavedrom
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


def get_html_plot_data(testname, data_dict, axis_dict=None, truncate=False, header_size=3):
    """Stringify plot data for HTML reporting
    """
    plot_data = "<h2>{:s}</h2>".format(testname)

    if axis_dict:
        plot_data += "AxiStream monitored packets"
        plot_data += "<br>"
        plot_data += "<br>"
        wavedrom_dict = {
                'signal': [],
                'config': {'hscale': 1.5}
            }
        datastrings = {}
        labels = {}
        counters = {}
        # iterate over all signals
        uptimes = []
        downtimes = []
        for signal in axis_dict:
            datastrings[signal] = ''
            labels[signal] = []
            data_list = axis_dict[signal]
            counters[signal] = 0
            for datum in data_list:
                data, start, end, period = datum
                uptimes.append([int(start), int(end), signal, data, int(period)])

        uptimes.sort(key=lambda x: x[0])

        for xx in range(len(uptimes)-1):
            if uptimes[xx+1][0] > (uptimes[xx][1]+4*uptimes[xx][4]):
                downtimes.append([uptimes[xx][1], uptimes[xx+1][0], [signal for signal in axis_dict], 0, uptimes[xx][4]]) #downtimes apply to all charts at once
        relevant_times = downtimes+uptimes
        relevant_times.sort(key= lambda x: x[0])
        for entry in relevant_times:
            signal = entry[2]
            if entry[3] == 0: #downtimes
                for xx in axis_dict:
                    if counters[xx] < entry[0]:
                        diff = int((entry[0]-counters[xx])/entry[4])
                        datastring = 'x'
                        for __ in range(diff-1):
                            datastring += '.'
                        datastrings[xx] += datastring
                        counters[xx] = entry[0]
                    datastrings[xx] += '=...'
                    labels[xx].append("idle: {} ns".format(entry[1]-entry[0]))
                    counters[xx] = entry[1]
            else: #uptime:
                if counters[signal] < entry[0]:
                    diff = int((entry[0]-counters[signal])/entry[4])
                    datastring = 'x'
                    for __ in range(diff-1):
                        datastring += '.'
                    datastrings[signal] += datastring
                    counters[signal] = entry[0]

                datastring = "="
                for __ in range(len(entry[3])-1):
                    datastring += "."
                label = "header {} bytes payload {} bytes".format(header_size, len(entry[3])-header_size)
                datastrings[signal] += datastring
                labels[signal].append(label)
                counters[signal] = entry[1]
        for signal in axis_dict:
            wavedrom_dict["signal"].append({"name":signal, "wave": datastrings[signal], "data": labels[signal]})
        wavedrom_dict_processed=json.dumps(wavedrom_dict)
        svg = wavedrom.render(wavedrom_dict_processed)
        svg = svg.tostring()

        font_sizing = "g[id^='wavelane_draw'] text { font-size: 12px; }"
        svg = svg.replace("</style>", f"{font_sizing}</style>")
        svg = svg.replace('height="60"', 'height="400"')
        svg = svg.replace('width="1220"', 'width="1600"')
        svg = svg.replace('viewBox="0,0,1220,60"', 'viewBox="0 0 1600 400"')
        svg = svg.replace('<svg ', '<svg id="waveform" ')
        plot_data+='<div style="width: 1600px; height: 400px; overflow: scroll;">'
        plot_data += svg
        plot_data += "</div>"
        plot_data += """
            <script src="https://unpkg.com/svg-pan-zoom@latest/dist/svg-pan-zoom.min.js"></script>
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                svgPanZoom('#waveform', {
                    zoomEnabled: true,
                    controlIconsEnabled: true,
                    fit: true,
                    center: true,
                    contain: true
                });
            });
            </script>
            """
        plot_data += "<br>"

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
                    dx[ii] = [float('nan')] * len(dx[ii])
                else:
                    if isinstance(dx[ii], str) or isinstance(dx[ii], int):
                        dx[ii] = float(xx)
                    else:
                        dx[ii] = [float(xx) for xx in dx[ii]]
            #plot data


            dt=[reverse_lookup_dt(xx, global_t) for xx in dt]
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