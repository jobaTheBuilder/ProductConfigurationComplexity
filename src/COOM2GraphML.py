import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
import networkx as nx

from rdflib import Graph, Namespace, RDF, URIRef
from rdflib.namespace import split_uri


class COOM2GraphML:
    def __init__(self, input_path: Path):
        self.COOM = Namespace("http://www.denkbares.com/coomV2#")
        self.EX = Namespace("http://www.example.org/ns#")
        self.FEATURE = self.COOM["Feature"]
        self.COMPONENT = self.COOM["Structure"]
        self.COOM_TYPE = self.COOM["type"]
        self.COOM_COMBINATIONS = self.COOM["Combinations"]

        self.uri2graphml = {}
        self.id_counter = 0

        self.input_graph = Graph()
        self.input_graph.parse(input_path)

    def export(self, out_path: Path):
        output_graph = nx.Graph()
        self._generate_knowledge(output_graph)
        nx.write_graphml(output_graph, out_path)

    def _generate_knowledge(self, output_graph):
        color_blue = '#ADD8E6'
        color_orange = '#fe6f5e'
        constrains_feature = self.COOM["constrainsFeature"]
        for b in self.input_graph.subjects(RDF.type, self.COOM_COMBINATIONS):
            # Knowledge Node (CN): For each behaviour knowledge create a node with link to KNOWLEDGE type node
            namespace, behavior_name = split_uri(str(b))
            behavior_node = self._create_node(behavior_name, output_graph, color_blue)
            for cf in self.input_graph.objects(b, constrains_feature):
                namespace, feature_name = split_uri(str(cf))
                feature_node = self._create_node(feature_name, output_graph, color_orange)
                self._create_egde(behavior_name, feature_name, output_graph)

    def _create_node(self, name, graph, color='grey'):
        the_id = self._id_for(name)
        graph.add_node(the_id, label=name,color=color)

    def _create_egde(self, from_name, to_name, graph):
        from_id = self._id_for(from_name)
        to_name = self._id_for(to_name)
        graph.add_edge(from_id, to_name, weight=1.5)

    def _id_for(self, name):
        if name in self.uri2graphml:
            return self.uri2graphml[name]
        else:
            self.id_counter = self.id_counter + 1
            the_id = "id_" + str(self.id_counter)
            self.uri2graphml[name] = the_id
            return the_id

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Example app to convert COOM RDF to GraphML analysis graph.")
    parser.add_argument("-i", "--inputfile", help="Input COOM RDF file", required=True)
    parser.add_argument("-o", "--outfile", help="Output GraphML file.", required=True)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    app = COOM2GraphML(Path(args.inputfile))
    app.export(Path(args.outfile))
