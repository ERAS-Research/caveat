# Copyright (C) 2025 ERAS Research Group
# Author(s): Murray Ferris, Torsten Reuschel

import os
import numpy as np
from pathlib import Path
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import plotly.graph_objects as go

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


def get_html_plot_data(testname, data_dict, axis_dict=None,
        header_size=3, rev_lookup=lambda x: str(x)):
    """Stringify plot data for HTML reporting
    """
    plot_data = "<h2>{:s}</h2>".format(testname)

    if axis_dict:
        df = []
        for key, pkgs in axis_dict.items():
            for pkg in pkgs:
                try:
                    header = rev_lookup(pkg[0][:header_size])
                except:
                        print(pkg[0][:header_size])
                        header = 'UNKNOWN'
                df.append(dict(Task=key, Start=str(pkg[1]), Finish=str(pkg[2]), pkg_header=header))

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
            names_list = []
            for key, values in data_dict.items():
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
                traces.append(go.Scatter(x=dt, y=[.5*xval/max(cx) - dict_index-.5 for xval in cx], mode='lines', line_shape='hv', name=key))
                names_list.append(key)

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
            for xx in range(len(names_list)):
                fig3.add_annotation(
                    text=names_list[xx],
                    xref='paper',
                    # yref=-.5,
                    x=-.015, y=-1-xx,
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
            if not any(isinstance(item, list) for item in dx):
                fig.add_trace(
                go.Scatter(x=dt, y=dx, mode='lines', line_shape='hv', name=key), row=dict_index+1, col=1, )
                annotations.append((key,dict_index+1))
                dict_index += 1
            else:
                for xx in range(len(dx[0])):
                                    # print(xx, type(xx))
                                    fig.add_trace(
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
