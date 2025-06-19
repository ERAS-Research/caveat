# Copyright (C) 2025 ERAS Research Group
# Author(s): Murray Ferris, Torsten Reuschel

import matplotlib.pyplot as plt
import mpld3
import os
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


def get_html_plot_data(testname, data_dict, axis_dict=None, truncate=False):
    """Stringify plot data for HTML reporting
    """
    plot_data = "<h2>{:s}</h2>".format(testname)

    if axis_dict:
        fig = plt.figure()
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
        plot_data += mpld3.fig_to_html(fig)

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
                if ('z' in xx) or ('x' in xx):
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
