import json
from os.path import dirname, abspath, join
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles


current_dir = dirname(abspath(__file__))
wellknown_path = join(current_dir, ".well-known")
historical_data = join(current_dir, "weather.json")

app = FastAPI()
app.mount("/.well-known", StaticFiles(directory=wellknown_path), name="static")


# load historical json data and serialize it:
with open(historical_data, "r") as f:
    data = json.load(f)

@app.get('/')
def root():
    """
    Allows to open the API documentation in the browser directly instead of
    requiring to open the /docs path.
    """
    return RedirectResponse(url='/docs', status_code=301)


@app.get('/countries')
def countries():
    return list(data.keys())


@app.get('/countries/{country}')
def cities(country: str):
    return list(data[country].keys())


@app.get('/countries/{country}/{city}/{month}')
def monthly_average(country: str, city: str, month: str):
    return data[country][city][month]

# Generate the OpenAPI schema:
openapi_schema = app.openapi()
with open(join(wellknown_path, "openapi.json"), "w") as f:
    json.dump(openapi_schema, f)


# Test with Spain
if __name__ == "__main__":
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # Test cities in Spain
    response = client.get("/countries/Spain")
    print(f"Cities in Spain: {response.json()}")
    
    # Test monthly average for a city in Spain
    cities_in_spain = response.json()
    if cities_in_spain:
        city = cities_in_spain[0]
        response = client.get(f"/countries/Spain/{city}/January")
        print(f"January average for {city}, Spain: {response.json()}")