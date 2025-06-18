
import matplotlib.pyplot as plt
import mpld3
import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning, module='mpld3')##deprecation warning inherent to the mpld3 library; a patch has been
#made by both another individual and myself and so should be resolved by next release: https://github.com/mpld3/mpld3/issues/530

def plot(testname, dict, axis_dict=None, truncate=False ):

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Caveat Signal Capture</title>
    </head>
    <body>
        <h1>Captures each signal that does not remain a constant value or contain z values throughout the simulation</h1>

        {plot_divs}
    </body>
    </html>
    """
    plot_divs=""


    if axis_dict:
        fig=plt.figure()
        height=0

        for signal in axis_dict:
            print("signal in coded dict is", signal)
            data=axis_dict[signal]

            for key in data:

                signal_time=data[key]
                print("time for signal ", signal, "is ", key )
                signal_time, time_before,len_message,time_after,rgb=key,*data[key]
                print(signal_time, time_before,len_message,time_after,rgb)
                plt.text(0,height+0.3,signal)
                plt.step([signal_time,time_before],[height,height], color='tab:blue')

                plt.fill_between([time_before,time_before+3],height-0.2,[height+0.2,height+0.2], color=rgb, step='pre')

                if len_message>3:
                    plt.fill_between([time_before+3, time_before+len_message],height-0.2,[height+0.2,height+0.2],color='k', step='pre')
                height-=1
                # plt.step([time_before+len_message,time_after], [0,0], color='tab:blue')
        plt.ylim(height-1, 1)
        plot_divs += mpld3.fig_to_html(fig)
    if dict:
        for ii in range(len(dict)):
                truncation = 0

                handle_names = list(dict.keys())
                handle= list(dict.values())[ii]
                if not all(isinstance(item, (int)) for item in handle):
                    handle = [float('nan') if 'z' in val or 'x' in val else val.integer for val in handle]

                xrange = list(range(len(handle)))
                if truncate:
                    leading=handle[0]
                    truncation = next((i for i, v in enumerate(handle) if v != leading), None)
                if truncation is not None:
                    ##if truncate is on and truncation is None, implies the entire graph is constant, so assumedly the user wouldn't want it
                    fig = plt.figure()
                    plt.step(xrange[truncation:], handle[truncation:], where='mid')
                    plt.xlabel("Time (ns)")
                    plot_divs += handle_names[ii]
                    plot_divs += mpld3.fig_to_html(fig)

    html_content=html_content.format(plot_divs = plot_divs)
    filename=['../results/Caveat_signals_',testname,'.html']
    filename=''.join(filename)
    with open(filename, 'w') as f:
            f.write(html_content)

