""" Recommendation Algorithm Global Configuration Settings """

import pickle

# File path for binary files
EMBEDDINGS_PATH = "app/bin/glove_w2v_embeddings.pkl"
MODEL_PATH = "app/bin/glove_knn_model.pkl"

# Algorithm constants
THRESHOLD = 0.4 
N_SIMILAR = 10  # Number of recommendations to return
GRAPH_LEVEL = 3  # The level of citation graph to build


def load_data(path):
    """
    Description : Loading data from path.

    Parameters :
    ------------
        - path : file path to load.
    """

    with open(path, "rb") as f:
        return pickle.load(f)
