# ProductConfigurationComplexity

Measure the complexity for product configuration knowledge. Scripts for reference implementation.

## Important Classes

### COOM2AnalysisKnowledgeGraph

Usually, the first step:
Convert a COOM RDF model into an _analysis knowledge graph_. 
The _analysis knowledge graph_ is then the basis for the complexity measures, e.g., target of the SPARQL queries.
You may rename the generated graph using `Tooling.rename_files` (this will give the filenames a anonamized version).

### KGDescribe

The second step: 
Loads _analysis knowledge graphs_ from a given directory, runs the configured SPARQL measures, and returns or prints the results. 
The used measures are configured by a YAML file, e,.g., `src/resources/measures/all_measures.yaml`.
The actual reference implementation of measures can be found in `src/resources/measures` .

### COOMDescribe

Helpoer class to combines `COOM2AnalysisKnowledgeGraph` and `KGDescribe` and  into a single run.

## Helper Classes
- `ResultPrinter`: Formats collected measure results as a compact Markdown table.
- `RadarData`: Stores aggregated measure values across multiple graphs and can render them as a Markdown table or radar plot.
- `RadarVisualizer`: Runs the full comparison pipeline by converting input models, executing measures, and aggregating the results.
- `COOM2GraphML`: Exports selected COOM knowledge relations as a GraphML graph for external graph visualization tools.


## Complexity Queries

The SPARQL queries live in `src/resources/measures` and all return a single value as `?count`.

- `component_count.sparql`: Counts all `:COMPONENT` nodes in the analysis knowledge graph.
- `component_count_avg.sparql`: Computes the average number of direct `:has` successors per component.
- `component_count_min.sparql`: Computes the minimum number of direct `:has` successors of any component.
- `component_count_max.sparql`: Computes the maximum number of direct `:has` successors of any component.
- `component_count_as_str.sparql`: Returns the component count together with average, minimum, and maximum successor counts as a formatted string.
- `choice_feature_count.sparql`: Counts all choice features, meaning features whose children are explicit options rather than `:numerical_range` or `:textual_range`.
- `choice_feature_count_avg.sparql`: Computes the average number of options per choice feature.
- `choice_feature_count_min.sparql`: Computes the minimum number of options among all choice features.
- `choice_feature_count_max.sparql`: Computes the maximum number of options among all choice features.
- `choice_feature_count_as_str.sparql`: Returns the number of choice features together with average, minimum, and maximum option counts as a formatted string.
- `num_feature_count.sparql`: Counts all numerical features by looking for features linked to `:numerical_range`.
- `text_feature_count.sparql`: Counts all textual features by looking for features linked to `:textual_range`.
- `knowledge_count.sparql`: Counts all `:KNOWLEDGE` nodes in the analysis graph.
- `knowledge_feature_average.sparql`: Computes the average number of knowledge nodes connected to a feature across `:constrains`, `:conditions`, and `:consequences`.
- `knowledge_feature_min.sparql`: Computes the minimum number of knowledge nodes attached to any feature across those relations.
- `knowledge_feature_max.sparql`: Computes the maximum number of knowledge nodes attached to any feature across those relations.
- `knowledge_feature_average_as_str.sparql`: Returns the average, minimum, and maximum knowledge-per-feature values as a formatted string.
- `inverse_knowledge_feature_average.sparql`: Computes the average number of distinct features referenced by a knowledge node across `:constrains`, `:conditions`, and `:consequences`.
- `inverse_knowledge_feature_min.sparql`: Computes the minimum number of referenced features for any knowledge node.
- `inverse_knowledge_feature_max.sparql`: Computes the maximum number of referenced features for any knowledge node.
- `inverse_knowledge_feature_average_as_str.sparql`: Returns the average, minimum, and maximum features-per-knowledge values as a formatted string.
- `avg_terminology_depth.sparql`: Computes the average structural depth of leaf components and features by counting their ancestors in the `:has` hierarchy.
