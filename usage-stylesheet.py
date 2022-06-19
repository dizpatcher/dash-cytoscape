import json
from typing import List, Any

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import dash_cytoscape as cyto
from demos import dash_reusable_components as drc

app = dash.Dash(__name__)
server = app.server

# ###################### DATA PREPROCESSING ######################
# Load data
with open('demos/data/sample_network.txt', 'r') as f:
    network_data = f.read().split('\n')

# We select the first 750 edges and associated nodes for an easier visualization
edges = network_data[:750]
nodes = set()

cy_edges = []
cy_nodes = []

for network_edge in edges:
    source, target = network_edge.split(" ")

    if source not in nodes:
        nodes.add(source)
        cy_nodes.append({"data": {"id": source, "label": "User #" + source[-5:]}})
    if target not in nodes:
        nodes.add(target)
        cy_nodes.append({"data": {"id": target, "label": "User #" + target[-5:]}})

    cy_edges.append({
        'data': {
            'source': source,
            'target': target
        }
    })

default_stylesheet = [
    {
        "selector": 'node',
        'style': {
            "opacity": 0.65,
        }
    },
    {
        "selector": 'edge',
        'style': {
            "curve-style": "bezier",
            "opacity": 0.65,
            "mid-target-arrow-shape": "tee",
        }
    },
]

styles = {
    'json-output': {
        'overflow-y': 'scroll',
        'height': 'calc(50% - 25px)',
        'border': 'thin lightgrey solid'
    },
    'tab': {
        'height': 'calc(98vh - 105px)'
    }
}

app.layout = html.Div([
    html.Div(className='eight columns', children=[
        cyto.Cytoscape(
            id='cytoscape',
            elements=cy_edges + cy_nodes,
            style={
                'height': '95vh',
                'width': '100%'
            }
        )
    ]),

    html.Div(className='four columns', children=[
        dcc.Tabs(id='tabs', children=[
            dcc.Tab(label='Control Panel', children=[
                drc.NamedDropdown(
                    name='Layout',
                    id='dropdown-layout',
                    options=drc.DropdownOptionsList(
                        'random',
                        'grid',
                        'circle',
                        'concentric',
                        'breadthfirst',
                        'cose'
                    ),
                    value='grid',
                    clearable=False
                ),

                drc.NamedDropdown(
                    name='Node Shape',
                    id='dropdown-node-shape',
                    value='ellipse',
                    clearable=False,
                    options=drc.DropdownOptionsList(
                        'ellipse',
                        'triangle',
                        'rectangle',
                        'diamond',
                        'pentagon',
                        'hexagon',
                        'heptagon',
                        'octagon',
                        'star',
                        'polygon',
                    )
                ),

                drc.NamedDropdown(
                    name='Засечка',
                    id='dropdown-edge-arrow',
                    value='tee',
                    clearable=False,
                    options=drc.DropdownOptionsList(
                        'triangle',
                        'triangle-tee',
                        'circle-triangle',
                        'triangle-cross',
                        'triangle-backcurve',
                        'vee',
                        'tee',
                        'square',
                        'circle',
                        'diamond',
                        'chevron',
                        'double-tee',
                        'test',
                        'none'
                    )
                ),

                drc.NamedInput(
                    name='Followers Color',
                    id='input-follower-color',
                    type='text',
                    value='#0074D9',
                ),

                drc.NamedInput(
                    name='Following Color',
                    id='input-following-color',
                    type='text',
                    value='#FF4136',
                ),
            ]),

            dcc.Tab(label='JSON', children=[
                html.Div(style=styles['tab'], children=[
                    html.P('Drag Node JSON:'),
                    html.Pre(
                        id='drag-node-json-output',
                        style=styles['json-output']
                    )
                ])
            ])
        ]),
    ])
])

@app.callback(Output('drag-node-json-output', 'children'),
              [Input('cytoscape', 'grabNodeData'),
               Input('cytoscape', 'dragNodeData')])
def display_drag_node(dragData, grabData):
    data = {}
    if grabData and dragData:
        data = {**grabData, **dragData}
    print(data)
    return json.dumps(data, indent=2)

# @app.callback(Output('cytoscape', 'stylesheet'),
#               Input('dropdown-edge-arrow', 'value'))
# def update_arrows(edge_arrow):
#     default_stylesheet.append({
#         "selector": 'edges',
#         "style": {
#             "mid-target-arrow-shape": edge_arrow
#         }
#     })
#
#     return default_stylesheet

@app.callback(Output('cytoscape', 'layout'),
              [Input('dropdown-layout', 'value')])
def update_cytoscape_layout(layout):
    return {'name': layout}


@app.callback(Output('cytoscape', 'stylesheet'),
              [Input('cytoscape', 'tapNode'),
               Input('input-follower-color', 'value'),
               Input('input-following-color', 'value'),
               Input('dropdown-edge-arrow', 'value'),
               Input('dropdown-node-shape', 'value')])
def generate_stylesheet(node, follower_color, following_color, edge_arrow, node_shape):
    if not node:
        return default_stylesheet

    stylesheet = [{
        "selector": 'node',
        'style': {
            'opacity': 0.3,
            'shape': node_shape
        }
    }, {
        'selector': 'edge',
        'style': {
            'opacity': 0.2,
            "mid-target-arrow-shape": edge_arrow,
            "curve-style": "bezier",
        }
    }, {
        "selector": 'node[id = "{}"]'.format(node['data']['id']),
        "style": {
            'background-color': '#B10DC9',
            "border-color": "purple",
            "border-width": 2,
            "border-opacity": 1,
            "opacity": 1,

            "label": "data(label)",
            "color": "#B10DC9",
            "text-opacity": 1,
            "font-size": 12,
            'z-index': 9999
        }
    }]

    for edge in node['edgesData']:
        if edge['source'] == node['data']['id']:
            stylesheet.append({
                "selector": 'node[id = "{}"]'.format(edge['target']),
                "style": {
                    'background-color': following_color,
                    'opacity': 0.9
                }
            })
            stylesheet.append({
                "selector": 'edge[id= "{}"]'.format(edge['id']),
                "style": {
                    "mid-target-arrow-color": following_color,
                    "mid-target-arrow-shape": edge_arrow,
                    "line-color": following_color,
                    'opacity': 0.9,
                    'z-index': 5000
                }
            })

        if edge['target'] == node['data']['id']:
            stylesheet.append({
                "selector": 'node[id = "{}"]'.format(edge['source']),
                "style": {
                    'background-color': follower_color,
                    'opacity': 0.9,
                    'z-index': 9999
                }
            })
            stylesheet.append({
                "selector": 'edge[id= "{}"]'.format(edge['id']),
                "style": {
                    "mid-target-arrow-color": follower_color,
                    "mid-target-arrow-shape": edge_arrow,
                    "line-color": follower_color,
                    'opacity': 1,
                    'z-index': 5000
                }
            })

    return stylesheet


if __name__ == '__main__':
    app.run_server(debug=True)
