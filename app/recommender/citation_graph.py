""" Citation graph creation class """

from app.models import Article


class CitationGraph:
    def create_graph(self, xid, graph, index, max_level):
        """
        Description :
        --------------
        Create a multilevel citation graph for a query.

        Parameters :
        ------------
        - xid : query id.
        - graph : Nested list in which each sub-list represents a level of the graph.
        - index : current graph level.
        - max_level : maximum level of the graph to create.

        Output : Returns nested list of articles id.
        """

        # If the level of the graph is higher than the maximum level allowed
        if len(graph) >= max_level:
            return graph

        # Get articles id of current level items
        children = []
        for vertex in graph[index]:
            vertex_row = Article.query.filter_by(id=vertex).first()
            references = vertex_row.references

            if references is not None:
                for ref in references:
                    tmp = Article.query.filter_by(id=ref).first()
                    if (
                        ref != xid
                        and not any(ref in subl for subl in graph)
                        and tmp is not None
                    ):
                        children.append(ref)

        # No data for the current graph level
        if len(children) == 0:
            return graph
        else:
            graph.append(children)
            return self.create_graph(xid, graph, len(graph) - 1, max_level)

    def get_graph_data(self, graph):
        """
        Description :
        --------------
        Retrieve the identifiers of all articles in the citation graph.

        Parameters :
        ------------
        - graph : List of lists of objects. Each element of the graph represents a level.

        Output : Return a list of identifiers.
        """

        references = []

        # Excludes level 0 since it represents the query
        for subl in graph[1:]:
            for xid in subl:
                references.append(xid)

        return references
