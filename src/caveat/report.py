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
import plotly.figure_factory as ff
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


def get_html_plot_data(testname, data_dict, axis_dict=None, truncate=False,
        header_size=3, rev_lookup=lambda x: str(x)):
    """Stringify plot data for HTML reporting
    """
    plot_data = "<h2>{:s}</h2>".format(testname)

    if axis_dict:
        df = []
        colors = {}
        for key, pkgs in axis_dict.items():
            for pkg in pkgs:
                try:
                    header = rev_lookup(pkg[0][:3])
                except:
                    if pkg[0][:3] == [0,32,0]:
                        header = 'DATA'
                    else:
                        print(pkg[0][:3])
                        header = 'UNKNOWN'
                df.append(dict(Task=key, Start=str(pkg[1]), Finish=str(pkg[2]), pkg_header=header))
                # colors[header] = 'rgb({:})'.format(','.join([str(x) for x in pkg[0]])) #use to turn header into RGB color

        fig2 = ff.create_gantt(
                    df,
                    index_col='pkg_header',
                    show_colorbar=True,
                    group_tasks=True,
                    bar_width=.3,)
        fig2.update_layout(
            # autosize=True,
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(size=18, color='black'),
            yaxis={
                'showgrid': False,
                'range':[-.5,len(axis_dict)-.5],
                },
            xaxis={
                'gridcolor':'lightgray',
                'showgrid': True,
                'zeroline': False,
                'rangeselector': {},
                'type': 'linear',
                'title':'Time (ns)',
                'showline':True,
                'linewidth':1.5,
                'linecolor':'black',
                'mirror':True,}
            )
        # fig2.update_layout(height=200*(len(axis_dict)+1), title_text="CAVEAT- Dynamic Test Reporting")
        fig2.update_layout(
            height=150*(len(axis_dict)),
            width=3000,
            # title_text="CAVEAT- Dynamic Test Reporting"
            title_text=None
            )

        outfilepath = '../results/dynamic/'
        outfilesubdir = os.path.split(testname)[0]
        Path(os.path.join(outfilepath, outfilesubdir)).mkdir(parents=True, exist_ok=True)
        fig2.write_image(
            outfilepath+testname+"_v2.pdf",
            height=150*(len(axis_dict)),
            width=3000,)

        plot_data += fig2.to_html()


        ##--- joined plotting of AXIS and custom busses -------
        if data_dict:
            traces = []
            dict_index = 0
            for key, values in data_dict.items():
                if not ('RF' in key):
                    continue
                dict_index += 1

                #sanity check: skip monitors that did not record events
                if len(values) < 2:
                    continue
                #prepare data for plotting: extract and sanitize
                dt, dx = list(zip(*values))
                dt = list(dt)
                dx = list(dx)
                for ii, xx in enumerate(dx):
                    if ('z' in str(xx)) or ('x' in str(xx)):
                        dx  += [float('nan') * len(dx[ii])]
                    else:
                        if isinstance(dx[ii], list):
                            dx[ii] = [float(xx) for xx in dx[ii]]
                        else:
                            dx[ii] = float(xx)

                cx = []
                for xx in dx:
                    # if ('x' in str(xx)) or ('z' in str(xx)):
                        # cx.append( np.nan )
                    # else:
                    try:
                        cx.append( complex(xx[0], xx[1]) )
                    except:
                        try:
                            cx.append( float(xx) )
                        except:
                            # cx.append( float('nan') )
                            cx.append( 0. )
                cx = abs(np.array(cx))
                # print(key, [complex(a, b) for a, b in zip(*dx)])
                if 'Tx' in key:
                    dt = [(ddt - dt[0] + 2600) for ddt in dt] #manual delay
                elif 'Rx' in key:
                    dt = [(ddt - dt[0] ) for ddt in dt] #manual delay, no global-time and quiet time extraction at this time
                traces.append(go.Scatter(x=dt, y=[.5*xval/max(cx) - dict_index-.5 for xval in cx], mode='lines', line_shape='hv', name=key))

            Ntraces = dict_index
            #export axis+data plot
            new_data = traces
            new_data.extend(list(fig2.data))
            fig3 = go.Figure(data=new_data, layout=fig2.layout)
            fig3.update_layout(
                    height=100*(len(axis_dict) + Ntraces),
                    width=4000,
                    # title_text="CAVEAT- Dynamic Test Reporting"
                    title_text=None,
                    yaxis={
                        'showgrid': False,
                        'range':[-1 - Ntraces, len(axis_dict)-.5],
                        },
                )
            fig3.add_annotation(
                text='RF-Tx',
                xref='paper',
                # yref=-.5,
                x=-.015, y=-1,
                showarrow=False,
                font=dict(color='black', size=18),)
            fig3.add_annotation(
                text='RF-Rx',
                xref='paper',
                # yref=-1.5,
                x=-.015, y=-2,
                showarrow=False,
                font=dict(color='black', size=18),)

            outfilepath = '../results/dynamic/'
            outfilesubdir = os.path.split(testname)[0]
            Path(os.path.join(outfilepath, outfilesubdir)).mkdir(parents=True, exist_ok=True)
            fig3.write_image(
                outfilepath+testname+"_v3.pdf",
                height=100*(len(axis_dict) + Ntraces),
                width=4000,)
            plot_data += fig3.to_html()



    # if axis_dict:
        # plot_data += "AxiStream monitored packets"
        # plot_data += "<br>"
        # plot_data += "<br>"
        # wavedrom_dict = {
                # 'signal': [],
                # 'config': {'hscale': 1.5}
            # }
        # datastrings = {}
        # labels = {}
        # counters = {}
        # # iterate over all signals
        # uptimes = []
        # downtimes = []
        # for signal in axis_dict:
            # datastrings[signal] = ''
            # labels[signal] = []
            # data_list = axis_dict[signal]
            # counters[signal] = 0
            # for datum in data_list:
                # data, start, end, period = datum
                # uptimes.append([int(start), int(end), signal, data, int(period)])

        # uptimes.sort(key=lambda x: x[0])

        # for xx in range(len(uptimes)-1):
            # if uptimes[xx+1][0] > (uptimes[xx][1]+4*uptimes[xx][4]):
                # downtimes.append([uptimes[xx][1], uptimes[xx+1][0], [signal for signal in axis_dict], 0, uptimes[xx][4]]) #downtimes apply to all charts at once
        # relevant_times = downtimes+uptimes
        # relevant_times.sort(key= lambda x: x[0])
        # for entry in relevant_times:
            # signal = entry[2]
            # if entry[3] == 0: #downtimes
                # for xx in axis_dict:
                    # if counters[xx] < entry[0]:
                        # diff = int((entry[0]-counters[xx])/entry[4])
                        # datastring = 'x'
                        # for __ in range(diff-1):
                            # datastring += '.'
                        # datastrings[xx] += datastring
                        # counters[xx] = entry[0]
                    # datastrings[xx] += '=...'
                    # labels[xx].append("idle: {} ns".format(entry[1]-entry[0]))
                    # counters[xx] = entry[1]
            # else: #uptime:
                # if counters[signal] < entry[0]:
                    # diff = int((entry[0]-counters[signal])/entry[4])
                    # datastring = 'x'
                    # for __ in range(diff-1):
                        # datastring += '.'
                    # datastrings[signal] += datastring
                    # counters[signal] = entry[0]

                # datastring = "="
                # for __ in range(len(entry[3])-1):
                    # datastring += "."
                # label = "header {} bytes payload {} bytes".format(header_size, len(entry[3])-header_size)
                # datastrings[signal] += datastring
                # labels[signal].append(label)
                # counters[signal] = entry[1]
        # for signal in axis_dict:
            # wavedrom_dict["signal"].append({"name":signal, "wave": datastrings[signal], "data": labels[signal]})
        # wavedrom_dict_processed=json.dumps(wavedrom_dict)
        # svg = wavedrom.render(wavedrom_dict_processed)
        # svg = svg.tostring()

        # font_sizing = "g[id^='wavelane_draw'] text { font-size: 12px; }"
        # svg = svg.replace("</style>", f"{font_sizing}</style>")
        # svg = svg.replace('height="60"', 'height="400"')
        # svg = svg.replace('width="1220"', 'width="1600"')
        # svg = svg.replace('viewBox="0,0,1220,60"', 'viewBox="0 0 1600 400"')
        # svg = svg.replace('<svg ', '<svg id="waveform" ')
        # plot_data+='<div style="width: 1600px; height: 400px; overflow: scroll;">'
        # plot_data += svg
        # plot_data += "</div>"
        # plot_data += """
            # <script src="https://unpkg.com/svg-pan-zoom@latest/dist/svg-pan-zoom.min.js"></script>
            # <script>
            # document.addEventListener('DOMContentLoaded', function() {
                # svgPanZoom('#waveform', {
                    # zoomEnabled: true,
                    # controlIconsEnabled: true,
                    # fit: true,
                    # center: true,
                    # contain: true
                # });
            # });
            # </script>
            # """
        # plot_data += "<br>"

    if data_dict:
        fig= make_subplots(rows=len(data_dict), cols=1, shared_xaxes=True)
        fig.update_layout(showlegend=False)

        annotations=[]
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
                    dx  += [float('nan') * len(dx[ii])]
                else:
                    if isinstance(dx[ii], list):
                        dx[ii] = [float(xx) for xx in dx[ii]]
                    else:
                        dx[ii] = float(xx)

            #plot data

            # dt=[reverse_lookup_dt(xx, global_t) for xx in dt]

            if not any(isinstance(item, list) for item in dx):
                fig.add_trace(
                # go.Scatter(x=[reverse_lookup_dt(xx, global_t) for xx in dt], y=dx), row=dict_index+1, col=1)
                # hop = len(global_t)//
                go.Scatter(x=dt, y=dx, mode='lines', line_shape='hv', name=key), row=dict_index+1, col=1, )
                annotations.append((key,dict_index+1))
                # ax[dict_index].set_xticks(range(len(global_t))[::hop], global_t[::hop])
                # plot_data += key
                dict_index += 1
            else:
                for xx in range(len(dx[0])):
                                    # print(xx, type(xx))
                                    fig.add_trace(
                # go.Scatter(x=[reverse_lookup_dt(xx, global_t) for xx in dt], y=dx), row=dict_index+1, col=1)
                # hop = len(global_t)//
                go.Scatter(x=dt, y=[data[xx] for data in dx], mode='lines', line_shape='hv', name=key), row=dict_index+1, col=1, )
                annotations.append((key,dict_index+1))
                dict_index += 1

        for name, row in annotations:
            yref = 'y domain' if row == 1 else f'y{row} domain'
            fig.add_annotation(
                text=name,
                xref='paper', yref=yref,
                x=0.01, y=1.10,
                showarrow=False,
                font=dict(color='black', size=14),
            )
        # fig.update_layout(legend=dict(
            # yanchor="top",
            # y=0.99,
            # xanchor="left",
            # x=0.01
        # ))

        # plt.xlabel("Time (ns)")
        # plt.show()
        # ax[-1].set_xticklabels([str(xx) for xx in global_t])
        fig.update_layout(height=200*(len(data_dict)+1), title_text="CAVEAT- Dynamic Test Reporting")
        plot_data += fig.to_html()
        outfilepath = '../results/dynamic/'
        outfilesubdir = os.path.split(testname)[0]
        Path(os.path.join(outfilepath, outfilesubdir)).mkdir(parents=True, exist_ok=True)

        fig.write_image(outfilepath+testname+".pdf")

        return plot_data


def make_report(testname: str, cfg_plot: dict,
        report_title: str='CAVEAT signal capture',
        outfilepath: str='../results/dynamic/', rev_lookup=lambda x: str(x)):
    """Compile stringified matplotlib figures into HTML report
    """
    #create report
    plot_data = get_html_plot_data(testname, **cfg_plot, rev_lookup=rev_lookup)
    html_report = html_template.format(
                        report_title=report_title,
                        plot_divs=plot_data
                    )

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
