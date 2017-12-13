#!/usr/bin/env apython

import networkx as nx
import pandas as pd

from operator import itemgetter

from bokeh.io import show, output_file
from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, BoxSelectTool
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes, NodesOnly
from bokeh.models.sources import ColumnDataSource
from bokeh.models.mappers import LinearColorMapper
from bokeh.core.properties import ColumnData
from bokeh.palettes import Spectral4, Viridis256
from bokeh.plotting import figure

if __name__ == '__main__':
    G = nx.read_edgelist("email-Eu-core.txt")
    # Remove self loop edges and nodes
    G.remove_edges_from(G.selfloop_edges())
    del_nodes = [x[0] for x in G.adjacency() if not x[1]]
    G.remove_nodes_from(del_nodes)
    # Get attribute data for dept, degree
    depts = 'email-Eu-core-department-labels.txt'
    node_and_degree = G.degree()
    (largest_hub, degree) = sorted(node_and_degree, key=itemgetter(1))[-1]
    #hub_ego = nx.ego_graph(G, largest_hub)

    id_dict = {'id':[x[0] for x in node_and_degree]}
    degree_dict = {'degree':[x[1] for x in node_and_degree]}
    dept_lookup = {}
    with open(depts) as f:
        for line in f:
            (pid, dept_num) = line.split()
            dept_lookup[pid] = dept_num

    #nx.set_node_attributes(hub_ego, attrs)
    dept_dict = {'dept':[dept_lookup[x] for x in id_dict['id']]}

    graph = from_networkx(G, nx.spring_layout, scale=2, center=(0,0))

    TOOLS = "pan,wheel_zoom,reset"
    TOOLTIPS = [
        ("PersonID", "@id"),
        ("DeptID", "@dept"),
        ("Degree", "@degree")
        ]
    plot = figure(title="EU Email Network", x_range=(-1.05,1.05), y_range=(-1.05,1.05),
              tools=TOOLS)
    plot.add_tools(HoverTool(tooltips=TOOLTIPS), TapTool())

    mapper = LinearColorMapper(palette=Viridis256, low=0, high=41)

    graph.selection_policy = NodesAndLinkedEdges()
    graph.inspection_policy = NodesOnly()

    graph.edge_renderer.glyph.line_alpha = 0.08
    graph.edge_renderer.glyph.line_width = 0.2
    graph.edge_renderer.glyph.line_color = 'magenta'

    graph.node_renderer.glyph.fill_color = {'field': 'dept', 'transform': mapper}
    graph.node_renderer.glyph.line_width = 0.2
    graph.node_renderer.glyph.fill_alpha = 0.08
    graph.node_renderer.glyph.line_color = 'grey'
    graph.node_renderer.glyph.line_alpha = 0.1
    graph.node_renderer.glyph.size = 'degree'

    graph.node_renderer.data_source.add(degree_dict['degree'], 'degree')
    graph.node_renderer.data_source.add(id_dict['id'], 'id')
    graph.node_renderer.data_source.add(dept_dict['dept'], 'dept')

    graph.node_renderer.hover_glyph = Circle(size=10, fill_color={'field': 'dept', 'transform': mapper}, fill_alpha=0.5)
    graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[0], line_width = 1)

    graph.node_renderer.selection_glyph = graph.node_renderer.hover_glyph
    graph.edge_renderer.selection_glyph = graph.edge_renderer.hover_glyph

    plot.renderers.append(graph)
    show(plot)
