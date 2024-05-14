import gradio as gr
import requests
from gradio import components
import pandas as pd

# Define the Gradio interface
def query_lyrics(query_text: str, n_results: int = 10):
    """
    Query the collection in ChromaDB with the specified query text and number of results.

    Args:
        query_text (str): The query text to search for in the collection.
        n_results (int): The number of results to return. Default is 10.

    Returns:
        list: A list of dictionaries representing the search results.
    """
    # Make HTTP request to the FastAPI endpoint
    response = requests.get("http://127.0.0.1:8000/query", params={"query_text": query_text, "n_results": n_results})
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame.from_dict(data["results"])
    else:
        return [{"error": "Failed to fetch data from the server"}]

iface = gr.Interface(
    fn=query_lyrics,
    inputs=[
        gr.Textbox(label="Insert vibe here"),
        gr.Number(label="Number of Songs", value=10)  # Set default value here
    ],
    outputs=components.Dataframe(headers=["Track", "Artist"], type="array"),
    title="VibeWeaver: Find songs for Your Mood!",
    #description="Enter a text and the number of results to retrieve matching lyrics.",
    examples=[["love", 5], ["rain", 10]],
    theme = gr.themes.Soft(primary_hue="teal")
)

# Launch the Gradio interface
iface.launch(share=True)
