from pathlib import Path
import unittest


try:
    from rdflib import Graph
except ImportError:  # pragma: no cover - depends on local environment
    Graph = None


class TextFeatureCountRegressionTest(unittest.TestCase):
    def test_counts_features_with_textual_range(self) -> None:
        if Graph is None:
            self.skipTest("rdflib is not installed")

        root = Path(__file__).resolve().parents[1]
        graph = Graph()
        graph.parse(root / "resources" / "examples" / "coom_minfull_example_analysis.ttl", format="turtle")
        query = (root / "resources" / "measures" / "text_feature_count.sparql").read_text(
            encoding="utf-8"
        )

        rows = list(graph.query(query))

        self.assertEqual(1, len(rows))
        self.assertEqual(1, rows[0]["count"].toPython())


if __name__ == "__main__":
    unittest.main()
