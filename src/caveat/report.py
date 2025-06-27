# Copyright (C) 2025 ERAS Research Group
# Author(s): Murray Ferris, Torsten Reuschel

import matplotlib.pyplot as plt
import json
import mpld3
import os
import wavedrom
from pathlib import Path

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
                    dx[ii] = [float('nan')]*len(dx[ii])
                else:
                    if isinstance(dx[ii], str):
                        dx[ii]=float(xx)
                    else:
                        dx[ii] = [float(xx) for xx in dx[ii]]
            #plot data
            fig = plt.figure()
            plt.step(dt, dx, where='mid')
            plt.xlabel("Time (ns)")
            plot_data += key
            plot_data += mpld3.fig_to_html(fig)
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
