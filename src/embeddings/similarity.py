import pickle
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

with open("embeddings.pkl", "rb") as file:
    embeddings = pickle.load(file)
    
ref_sentence =  \
"""
suivi du déploiement des énergies renouvelables
"""

model = SentenceTransformer('dangvantuan/sentence-camembert-large')
ref_sentence_embedding = model.encode(ref_sentence)

similarities = cosine_similarity(
    [ref_sentence_embedding],
    embeddings["embeddings"]
)

data = pd.DataFrame({
    "notes" : np.array(embeddings["notes"]),
    "similarities" : np.ndarray.transpose(similarities).flatten()
})

data.sort_values(by=["similarities"], ascending=False, inplace=True)