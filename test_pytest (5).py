import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import Mock
from mainFastAPI import app, QueryResultsResponse, SearchResult, lifespan_namespace  
from pydantic import BaseModel, PositiveInt

client = TestClient(app)

chroma_results= {
  "ids": [
    [
      "8660",
      "9231",
    ]
  ],
  "distances": [
    [
      0.39068877696990967,
      0.3985518217086792,
    ]
  ],
  "metadatas": [
    [
      {
        "acousticness": "0.181726086",
        "age": "0.657142857",
        "artist_name": "lynyrd skynyrd",
        "communication": "0.058784894",
        "danceability": "0.578685151",
        "dating": "0.061274947",
        "energy": "0.605593288",
        "family/gospel": "0.088386346",
        "family/spiritual": "0.029383546",
        "feelings": "0.021994503",
        "genre": "country",
        "instrumentalness": "0.00033502",
        "len": "92",
        "light/visual perceptions": "0.000773994",
        "like/girls": "0.000773994",
        "loudness": "0.602825424",
        "movement/places": "0.044120333",
        "music": "0.548999134",
        "night/time": "0.000773994",
        "obscene": "0.000773994",
        "release_date": "1974",
        "romantic": "0.08075777",
        "sadness": "0.000773994",
        "shake the audience": "0.04464614",
        "topic": "music",
        "track_name": "sweet home alabama",
        "valence": "0.888705688",
        "violence": "0.000773994",
        "world/life": "0.000773994"
      },
      {
        "acousticness": "0.113452925",
        "age": "0.571428571",
        "artist_name": "alabama",
        "communication": "0.000923361",
        "danceability": "0.500703997",
        "dating": "0.000923361",
        "energy": "0.538524126",
        "family/gospel": "0.000923361",
        "family/spiritual": "0.000923361",
        "feelings": "0.000923361",
        "genre": "country",
        "instrumentalness": "5.69E-06",
        "len": "84",
        "light/visual perceptions": "0.253175972",
        "like/girls": "0.078853233",
        "loudness": "0.711868318",
        "movement/places": "0.097088303",
        "music": "0.352936704",
        "night/time": "0.000923361",
        "obscene": "0.000923361",
        "release_date": "1980",
        "romantic": "0.000923361",
        "sadness": "0.036419655",
        "shake the audience": "0.018484283",
        "topic": "music",
        "track_name": "mountain music",
        "valence": "0.70012366",
        "violence": "0.000923361",
        "world/life": "0.000923361"
      }
    ]
  ],
  "embeddings": None,
  "documents": [
    [
      "The following content is about lynyrd skynyrd and pertains to the track 'sweet home alabama' released in 1974 under the genre 'country': wheel turnin home singin songs southland miss alabamy think hear young sing southern hear young remember southern need sweet home alabama sky blue sweet home alabama lord come home birmingham governor watergate bother conscience bother tell truth sweet home alabama sky blue sweet home alabama lord come home muscle shoal swampers know pick song lord pick feel blue bout sweet home alabama sky blue sweet home alabama lord come home sweet home alabama sweet home baby sky blue governor true sweet home alabama lordy lord come home yeah yeah stop come short",
      "The following content is about alabama and pertains to the track 'mountain music' released in 1980 under the genre 'country': mountain yeah days go climb mountain play mountain music like grandma grandpa play float river cajun hideaway drift away like ride raft huck like winkle daze dream play mountain music like grandma grandpa play float river cajun hideaway swim river prove spend lazy nature friend climb long tall hickory bend skin cat play baseball chert rock sawmill slabs bat play backhome comeon music come heart play lot feel music start play mountain music like grandma grandpa play float river cajun hideaway play mountain music"
    ]
  ],
  "uris": None,
  "data": None
}


def make_search_results():
    return [SearchResult(Track="sweet home alabama", Artist="lynyrd skynyrd"), SearchResult(Track="mountain music", Artist="alabama")]

def test_query_endpoint(mocker):
    # Arrange.
    request_body = {"query_text": "Your query text here", "n_results": 10}
    lifespan_namespace.collection= Mock()
    mocker.patch("mainFastAPI._query_collection", return_value=chroma_results)
    search_results = make_search_results()

    # Act.
    response = client.get("/query", params=request_body)

    # Assert.
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == QueryResultsResponse(n_results= request_body["n_results"], query_text= request_body["query_text"], results=search_results).model_dump()

    
  