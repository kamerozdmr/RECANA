import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def kernelPlot(cont_spot, kernel, nyquist, filtercorner, filtertype):
    fimp, timepoint, fimpX, hz = kernel
    

    if filtertype == "bandpass":
        xCorner = [0,filtercorner[0],filtercorner[0],filtercorner[1],filtercorner[1],nyquist]
        yCorner = [0,0,1,1,0,0]

    elif filtertype == "highpass":
        xCorner = [0,filtercorner[0],filtercorner[0],nyquist]
        yCorner = [0,0,1,1]

    elif filtertype == "lowpass":
        xCorner = [0,filtercorner[0],filtercorner[0],nyquist]
        yCorner = [1,1,0,0]
   
    kernelfig = make_subplots(rows=1, cols=3,
                            subplot_titles=("Filter Kernel", "Frequency Response with Corners", "Frequency Response(dB)"))

    kernelfig.add_trace(
                        go.Scatter(x=timepoint, y=fimp,
                        mode="lines",
                        name= "Filter Kernel",
                        showlegend=False,
                        legendgroup = "1"),
                        row=1, col=1,
                    )
    kernelfig.update_xaxes(title_text="Time Point(a.u)", row=1, col=1)
    

    kernelfig.add_trace(
                        go.Scatter(x=xCorner, y=yCorner,
                        mode="lines",
                        name= "Filter Corners", 
                        legendgroup = "2"),
                        row=1, col=2,
                    )

    kernelfig.add_trace(
                        go.Scatter(x=hz, y=fimpX[0:len(hz)],
                        mode="lines",
                        name= "Frequency Response",
                        legendgroup = "2"),
                        row=1, col=2,
                    )
    kernelfig.update_xaxes(title_text="Frequency(Hz)", row=1, col=2)
    kernelfig.update_yaxes(title_text=f"Attenuation", row=1, col=2)


    #plt.plot(hz,10*np.log10(fimpX[0:len(hz)]),'ks-')             -20 * np.log10(abs(h))
    kernelfig.add_trace(
                        go.Scatter(x=hz, y=20*np.log10(fimpX[0:len(hz)]),
                        mode="lines",
                        name= "Frequency Response (log)",
                        showlegend=False,
                        legendgroup = "3"),
                        row=1, col=3,
                    )
    kernelfig.update_xaxes(title_text="Frequency(Hz)", row=1, col=3)
    kernelfig.update_yaxes(title_text=f"Attenuation(dB)", row=1, col=3)


    kernelfig.update_yaxes(range=[-0.05, 1.3], row=1, col=2)

    kernelfig.update_layout(legend=dict(font = dict( size = 10), x=0.46, y=0.96), transition_duration=500)  

    cont_spot.plotly_chart(kernelfig, theme="streamlit", use_container_width=True, height= 150)



def detrendPlot():

    pass



