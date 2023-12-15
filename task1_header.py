import requests
import json


# TASK 1:
def get_API_data(filters, structure):
    """
    Fetch data from the UK Government Coronavirus data API.

    :param filters: A string of conditions to filter the data (e.g., "areaType=nation;areaName=England").
    :param structure: A dictionary defining the structure of the data to be returned.
    :return: The data returned by the API or an error message.
    """
    base_url = "https://api.coronavirus.data.gov.uk/v1/data"

    # Convert the structure dictionary to a JSON-formatted string
    structure_json = json.dumps(structure)

    # Define the parameters for the API request
    api_params = {
        "filters": filters,
        "structure": structure_json,
        "page": 1,
    }

    try:
        response = requests.get(base_url, params=api_params)

        # Check if the request was successful
        response.raise_for_status()

        # Return the JSON data
        return response.json()
    except requests.RequestException as e:
        return f"Error: {e}"
