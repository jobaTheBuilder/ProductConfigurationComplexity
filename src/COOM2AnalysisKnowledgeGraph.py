import argparse
from pathlib import Path
from typing import List

from rdflib import BNode, Graph, Namespace, RDF, URIRef
from rdflib.namespace import split_uri
from rdflib.collection import Collection


class COOM2AnalysisKnowledgeGraph:
    def __init__(self, input_path: Path):
        """Load a COOM RDF graph that will be converted into the analysis graph."""
        self.COOM = Namespace("http://www.denkbares.com/coomV2#")
        self.EX = Namespace("http://www.example.org/ns#")
        self.FEATURE = self.COOM["Feature"]
        self.COMPONENT = self.COOM["Structure"]
        self.COOM_TYPE = self.COOM["type"]
        self.COOM_COMBINATIONS = self.COOM["Combinations"]
        self.COOM_KNOWLEDGE_TYPES = (
            self.COOM["Requirement"],
            self.COOM["Combinations"],
            self.COOM["DefaultValue"],
            self.COOM["InstanceExists"],
            self.COOM["Implication"],
        )

        self.EX_COMPONENT = self.EX["COMPONENT"]
        self.EX_FEATURE = self.EX["FEATURE"]
        self.EX_IN = self.EX["in"]
        self.EX_HAS = self.EX["has"]

        self.EX_VALUE = self.EX["VALUE"]
        self.EX_KNOWLEDGE = self.EX["KNOWLEDGE"]
        self.EX_CONSTRAINS = self.EX["constrains"]

        # maps the coom URIs to URI objects in the output knowledge graph
        self.coom2kg = {}

        self.input_graph = Graph()
        self.input_graph.parse(input_path)

    def _local_name_for(self, term) -> str:
        """Return a usable local identifier for URI refs and blank nodes."""
        if isinstance(term, BNode):
            return str(term)

        _, local_name = split_uri(str(term))
        return local_name

    def export(self, out_path: Path):
        """Build and serialize the analysis knowledge graph for the loaded COOM model."""
        output_graph = Graph()
        output_graph.bind("", self.EX)
        self._generate_features(output_graph)
        self._generate_components(output_graph)
        self._generate_knowledge(output_graph)
        output_graph.serialize(out_path)

    def _generate_components(self, output_graph):
        """Create component nodes and structural :has edges in the output graph."""
        for c in self.input_graph.subjects(RDF.type, self.COMPONENT):
            # BUILDING RULE Component Node (CN)
            local_name = self._local_name_for(c)
            cv = URIRef(self.EX + local_name)
            output_graph.add((cv, RDF.type, self.EX_COMPONENT))
            self.coom2kg[c] = cv

            # BUILDING RULE Hierarchy Edge (SE1 / SE2)
            feature_list_node = self.input_graph.value(c, self.COOM["hasFeature"])
            features = Collection(self.input_graph, feature_list_node)
            for feature in features:
                local_name = self._local_name_for(feature)
                fv = URIRef(self.EX + local_name)

                # check, is the feature a structure type itself?
                # then: connect the type in the objects of the triple, not the feature
                feature_type = self.input_graph.value(feature, self.COOM["type"])
                if feature_type:
                    type_of_feature_type = self.input_graph.value(feature_type, RDF.type)
                    if type_of_feature_type == self.COOM["Structure"]:
                        local_name = self._local_name_for(feature_type)
                        fv = URIRef(self.EX + local_name)

                output_graph.add((cv, self.EX_HAS, fv))
                self.coom2kg[feature] = fv

    def _generate_features(self, output_graph: Graph):
        """Create feature nodes and connect them to their admissible values."""
        for f in self.input_graph.subjects(RDF.type, self.FEATURE):
            # BUILDING RULE: FEATURE NODE (FN)
            local_name = self._local_name_for(f)
            fv = URIRef(self.EX + local_name)
            output_graph.add((fv, RDF.type, self.EX_FEATURE))
            self.coom2kg[f] = fv

            # BUILDING RULE Feature Value Edge (FE)
            feature_options = self._get_values_of(f)
            if feature_options:
                for option in feature_options:
                    option_uri = URIRef(self.EX + option)
                    output_graph.add((fv, self.EX_HAS, option_uri))
                    self.coom2kg[option] = option_uri

    def _generate_knowledge(self, output_graph: Graph):
        """Create knowledge nodes and link them to the features they constrain."""
        constrains_feature = self.COOM["constrainsFeature"]
        for knowledge_type in self.COOM_KNOWLEDGE_TYPES:
            for b in self.input_graph.subjects(RDF.type, knowledge_type):
                # Knowledge Node (CN): For each behaviour knowledge create a node with link to KNOWLEDGE type node
                local_name = self._local_name_for(b)
                knode = URIRef(self.EX + local_name)
                output_graph.add((knode, RDF.type, self.EX_KNOWLEDGE))
                for cf in self.input_graph.objects(b, constrains_feature):
                    # Constraints Edge(CE3)
                    cfeature = self.coom2kg[cf]
                    output_graph.add((knode, self.EX_CONSTRAINS, cfeature))

    def _get_values_of(self, f) -> List[str]:
        """Return the analysis-graph value nodes for one COOM feature."""
        the_type = self.input_graph.value(f, self.COOM_TYPE)
        if the_type == self.COOM["Boolean"]:
            return ["true", "false"]
        elif the_type == self.COOM["Numerical"]:
            return ["numerical_range"]
        elif the_type == self.COOM["Textual"]:
            return ["textual_range"]
        else:
            options_node = self.input_graph.value(the_type, self.COOM["hasOption"])
            options = Collection(self.input_graph, options_node)
            str_options = []
            for option in options:
                local_name = self._local_name_for(option)
                str_options.append(local_name)
            return str_options


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Example app to convert COOM RDF to Analysis Knowledge Graph.")
    parser.add_argument("-i", "--inputfile", help="Input COOM RDF file", required=True)
    parser.add_argument("-o", "--outfile", help="Output RDF file.", required=True)
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    app = COOM2AnalysisKnowledgeGraph(Path(args.inputfile))
    app.export(Path(args.outfile))
