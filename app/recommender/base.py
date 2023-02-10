from . import config
from .citation_graph import CitationGraph
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class Recommender:
    # Embeddings of all articles
    embeddings = config.load_data(config.EMBEDDINGS_PATH)
    knn = config.load_data(config.MODEL_PATH)

    def __init__(self, qid):
        self.query_id = qid
        self.query_embeddings = np.array(self.embeddings[qid]).reshape(1, -1)

    def calculate_similarity(
        self, xid, query, data, n=config.N_SIMILAR, threshold=config.THRESHOLD
    ):
        """
        Description :
        --------------
        Calculate the similarity between the query embedding and other embeddings.

        Parameters :
        ------------
        - xid : article id
        - query : query embedding
        - data : dictionary of article embedding vectors and their ids to compare with the query.
        - Threshold : percentage of similarity required.
        - n : number of similar items to return.
        """

        data_xid = list(data.keys())
        data_values = list(data.values())

        # Calculate the similarity
        cosine = cosine_similarity(query, data_values)

        # Dictionary contains each article with the corresponding similarity with the query
        similarity = dict({})
        for i, value in enumerate(cosine[0]):
            if value >= threshold:
                similarity[data_xid[i]] = value

        if xid in similarity:
            similarity.pop(xid)

        # Sort articles in descending order based on their similarity to the query and return n articles
        similarity = [
            k
            for k, v in [
                (key, value)
                for key, value in sorted(
                    similarity.items(), key=lambda item: item[1], reverse=True
                )
            ][:n]
        ]

        return similarity

    def get_similar_articles(self):
        """
        Description :
        --------------
        Returns similar articles to the query.

        Output : List of articles id.
        """

        # Create a citation graph for the query of 3-level
        instance = CitationGraph()
        graph = instance.create_graph(
            self.query_id, [[self.query_id]], 0, config.GRAPH_LEVEL
        )
        graph_data = instance.get_graph_data(graph)

        # Return similar articles
        if len(graph_data) <= config.N_SIMILAR:
            _, index = self.knn.kneighbors(self.query_embeddings)
            index = list(index[0])

            if self.query_id in index:
                index.remove(self.query_id)

            return index
        else:
            # Get vectors of query neighbors
            data = {xid: self.embeddings[xid] for xid in graph_data}
            index = self.calculate_similarity(
                self.query_id, self.query_embeddings, data
            )

            return index
