import pandas as pd
import pickle
from utils import wrapper_engine

engine = wrapper_engine(config='config.ini')

with engine.connect() as connection:
    package = pd.read_sql_table(
        table_name="package", 
        con=connection,
        schema="public",
        )

data = package[["id", "title", "notes"]].head(5)

# https://huggingface.co/dangvantuan/sentence-camembert-large
# Autres modèles à tester : camembert/camembert-base-wikipedia-4gb
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('dangvantuan/sentence-camembert-large')

def limit_input_size(input:str, max_length:int)->str:
    try:
        return " ".join(input.split()[:max_length])
    except Exception as exception:
        print("Exception: ", exception)
        return None
    
#@TODO: test à partir des 100 premiers mots des notes (limite du modèle)
notes = list(data.loc[:, "notes"].apply(lambda x: limit_input_size(x, 100)))
notes_embeddings = model.encode(notes, show_progress_bar=True)

with open('embeddings.pkl', "wb") as output:
    pickle.dump({'notes': notes, 
                 'embeddings': notes_embeddings}, output, 
                protocol=pickle.HIGHEST_PROTOCOL)