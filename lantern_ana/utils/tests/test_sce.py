import lantern_ana.utils.spacecharge as sce
import plotly.graph_objects as go
import numpy as np

from dash import Dash, html, dcc, callback, Output, Input
import lardly
from lardly.detectoroutline import DetectorOutline


def make_offset_array():
    nx = 10
    ny = 10
    nz = 20
    xpoints = np.linspace(5,245,nx)
    ypoints = np.linspace(-115,115,ny)
    zpoints = np.linspace(5,1020,nz)

    ntot = nx*ny*nz
    pos = np.zeros( (ntot,3) )
    offsets = np.zeros( (ntot,3) )

    ii = 0
    for ix,x in enumerate(xpoints):
        for iy,y in enumerate(ypoints):
            for iz,z in enumerate(zpoints):
                pos[ii,0] = x
                pos[ii,1] = y
                pos[ii,2] = z
                offsets[ii,0], offsets[ii,1], offsets[ii,2] = sce.apply_sce_correction( (x, y, z) )
                ii += 1
    

    plot3d_layout = {
        "title": "Detector View",
        "height":800,
        "margin": {"t": 0, "b": 0, "l": 0, "r": 0},
	    "font": {"size": 12, "color": "black"},
        "showlegend": False,
        "paper_bgcolor": "rgb(255,255,255)",
        "scene": {
            # "xaxis": axis_template,
            # "yaxis": axis_template,
            # "zaxis": axis_template,
	        "aspectratio": {"x": 1, "y": 1, "z": 4},
            "camera": {"eye": {"x": -4.0, "y": 0.25, "z": 0.0},
	        "center":{"x":0.0, "y":0.0, "z":0.0},
                "up":dict(x=0, y=1, z=0)},
            "annotations": [],
	    },
    }

    sce_plot = go.Cone(
        x=pos[:,0],
        y=pos[:,1],
        z=pos[:,2],
        u=offsets[:,0],
        v=offsets[:,1],
        w=offsets[:,2],
        sizemode="raw",
        sizeref=2,
        anchor="tip")

    
    detlines = DetectorOutline().getlines(color=(0,0,0))
    traces = [sce_plot]+detlines

    fig = go.Figure(data=traces,
        layout=plot3d_layout)
    
    return fig

if __name__=="__main__":
    app = Dash()

    app.layout = [
        html.H1(children='(Inverse) Space Charge Effect', style={'textAlign':'center'}),
        dcc.Graph(id='graph-content',figure=make_offset_array())
    ]

    app.run(debug=True)



