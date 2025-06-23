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
        <title>CAVEAT Signal Capture</title>
    </head>
    <body>
        <h1>Captures each signal that does not remain a constant value or contain z values throughout the simulation</h1>

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
        plot_data+="<br>"
        plot_data+="<br>"
        wavedrom_dict={"signal":[] }

        for signal in axis_dict:

            data_list = axis_dict[signal]
            previous = 0

            datastring=""
            datalist=[]
            for datum in data_list:
                data, start, end, period = datum

                header = data[:header_size]
                if (start-previous>0):
                    datastring+="=...."
                    label="idle: {} ns".format(start-previous)
                    datalist.append(label)
                ##this will add a length of 5 to your data

                datastring_builder="="
                for __ in range(header_size-1):
                    datastring_builder+="."##FIXME: manual appending of header length
                label="H"
                datalist.append(label)
                datastring+=datastring_builder


                if len(data) > header_size:
                    datastring_builder="="
                    print("data length is ",len(data))
                    for __ in range(len(data)-(header_size+1)):
                        datastring_builder += "."
                    print("data is", data)
                    datastring+=datastring_builder
                    label="P"
                    datalist.append(label)
                previous = end
            wavedrom_dict["signal"].append({"name":signal, "wave": datastring, "data": datalist})




        wavedrom_dict_processed=json.dumps(wavedrom_dict)
        svg=wavedrom.render(wavedrom_dict_processed)
        plot_data+=svg.tostring()
        plot_data+="<br>"

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
                    dx[ii] = float('nan')
                else:
                    dx[ii] = float(xx)
            #plot data
            fig = plt.figure()
            plt.step(dt, dx, where='mid')
            plt.xlabel("Time (ns)")
            plot_data += key
            plot_data += mpld3.fig_to_html(fig)
        return plot_data

def make_report(testname: str, cfg_plot: dict, outfilepath: str='../results/dynamic/'):
    """Compile stringified matplotlib figures into HTML report
    """
    #create report
    plot_data = get_html_plot_data(testname, **cfg_plot)
    html_report = html_template.format(plot_divs = plot_data)

    #write report to file
    outfilesubdir = os.path.split(testname)[0]
    Path(os.path.join(outfilepath, outfilesubdir)).mkdir(parents=True, exist_ok=True)
    with open('{:s}/{:s}.html'.format(outfilepath, testname), 'w') as f:
        f.write(html_report)
