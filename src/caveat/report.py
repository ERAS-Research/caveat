# Copyright (C) 2025 ERAS Research Group
# Author(s): Murray Ferris, Torsten Reuschel

import matplotlib.pyplot as plt
import mpld3

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
    plot_data = ""

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
        for ii in range(len(data_dict)):
            truncated_plot_data = None
            handle_names = list(data_dict.keys())
            handle = list(data_dict.values())[ii]
            if not all(isinstance(item, (int)) for item in handle):
                handle = [float('nan') if 'z' in val or 'x' in val else val.integer for val in handle]

            xrange = list(range(len(handle)))
            if truncate:
                leading = handle[0]
                truncated_plot_data = next((i for i, v in enumerate(handle) if v != leading), None)
            #skip plot, if truncated_plot_data is empty #FIXME: what if truncate if not enabled?
            if truncated_plot_data is None:
                continue

            fig = plt.figure()
            plt.step(xrange[truncation:], handle[truncation:], where='mid')
            plt.xlabel("Time (ns)")
            plot_data += handle_names[ii]
            plot_data += mpld3.fig_to_html(fig)


def make_report(testname: str, cfg_plot: dict, outfilepath: str='../results/'):
    """Compile stringified matplotlib figures into HTML report
    """
    plot_data = get_html_plot_data(testname, **cfg_plot)

    html_report = html_template.format(plot_divs = plot_data)
    outfilename = '{:s}/caveat_signals_{:s}.html'.format(outfilepath, testname)
    with open(outfilename, 'w') as f:
        f.write(html_report)
