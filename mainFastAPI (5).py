import json
from contextlib import asynccontextmanager
from operator import itemgetter
from types import SimpleNamespace
import chromadb
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import logging
import aiofiles
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import List, Tuple
from pydantic import BaseModel
from operator import itemgetter
from types import SimpleNamespace
from contextlib import asynccontextmanager
import json
import chromadb
from typing import List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def _make_documents_ids_metadatas():
    """
    Create documents, ids, and metadatas from the Lyric_dataset.json file.

    Returns:
        documents (list): A list of strings representing the content of each document.
        ids (list): A list of strings representing the IDs of each document.
        metadatas (list): A list of dictionaries representing the metadata of each document.
    """
    with open("/Users/13213/Documents/Lyric_dataset.json", mode='r', encoding='utf-8') as json_file:
        content =  json.load(json_file)
    data_first_5000 = content[:5000]
    documents = [
        f"The following content is about {item['artist_name']} and pertains to the track '{item['track_name']}' released in {item['release_date']} under the genre '{item['genre']}': {item['lyrics']}"
        for item in data_first_5000
    ]
    ids = [str(i) for i in range(len(documents))]
    metadatas = [{k: v for k, v in item.items() if k != "lyrics"} for item in data_first_5000]

    return documents, ids, metadatas


def _create_or_get_collection():
    """
    Ensure a collection named "Lyric_dataset" exists in ChromaDB,
    either by creating it with specified metadata if it doesn't exist
    or simply retrieving it if it does.

    Returns:
        collection (chromadb.Collection): A collection object in ChromaDB.
    """
    chroma_client = chromadb.Client()  # Or PersistentClient, adjust accordingly
    # No need to separately check for existence; this handles both scenarios
    collection = chroma_client.get_or_create_collection(
        name="Lyric_dataset",
        metadata={"hnsw:space": "cosine"}
    )
    return collection



def _query_collection(collection, query_text: str, n_results: int = 10):
    """
    Query the collection in ChromaDB with the specified query text and number of results.

    Args:
        query_text (str): The query text to search for in the collection.
        n_results (int): The number of results to return.

    Returns:
        results (dict): A dictionary containing the query results.
    """
    results = collection.query(n_results=n_results, query_texts=[query_text])

    return results


def _format_results(results: dict):
    """
    Format the query results from ChromaDB into a list of dictionaries.

    Args:
        results (dict): A dictionary containing the query results.

    Returns:
        formatted_results (list): A list of dictionaries representing the formatted query results.
    """
    formatted_results = []
    # Iterate over 'metadatas' if it exists in results
    metadatas = results.get('metadatas', [])
    for metadata_list in metadatas:
        for metadata in metadata_list:
            # Use .get() with a default value of None for 'track_name' and 'artist_name'
            track_name = metadata.get('track_name', None)
            artist_name = metadata.get('artist_name', None)
            # Only include dictionaries in the results where both track_name and artist_name are not None
            if track_name is not None and artist_name is not None:
                formatted_result = {"Track": track_name, "Artist": artist_name}
                formatted_results.append(formatted_result)

    return formatted_results




app = FastAPI()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


async def lifespan(app: FastAPI):
    logging.info("Application startup: Loading data...")
    try:
        documents, ids, metadatas =  _make_documents_ids_metadatas()
        lifespan_namespace.collection = _create_or_get_collection()
        lifespan_namespace.collection.add(documents = documents, ids = ids, metadatas = metadatas)
        logging.info("Data successfully loaded.")
    except Exception as e:
        logging.error(f"Failed to load data: {type(e).__name__} - {e}")
    yield  # If there were cleanup actions, they would go after this yield.


lifespan_namespace = SimpleNamespace()
app = FastAPI(lifespan=lifespan)

# Define a model for what was previously a SimpleNamespace object
class ResultItem(BaseModel):
    id: str
    score: float
    metadata: dict  # Adjust the type as necessary

class QueryResultsResponse(BaseModel):
    query_text: str
    n_results: int
    results: List[ResultItem]  # Use the defined model here

class QueryResults(BaseModel):
    query_text: str
    n_results: int


async def root():
    return {"message": "Hello World"}

class SearchResult(BaseModel):
    Track: str
    Artist: str

class QueryResultsResponse(BaseModel):
    query_text: str
    n_results: int
    results: List[SearchResult]

@app.get("/query", response_model=QueryResultsResponse)
def read_query(query_text: str, n_results: int = 10):
    """
    Query the collection in ChromaDB with the specified query text and number of results.

    Args:
        query_text (str): The query text to search for in the collection.
        n_results (int): The number of results to return. Default is 10.

    Returns:
        QueryResultsResponse: A response containing the query text, number of results, and the search results.
    """
    results = _query_collection(lifespan_namespace.collection, query_text, n_results)
    formatted_results = _format_results(results)

    return QueryResultsResponse(query_text=query_text, n_results=n_results, results=formatted_results)


"""
To Do:

3. Optional: Change query to POST 
4. Optional: Keeping end results as query parameter, while query text as json table
"""