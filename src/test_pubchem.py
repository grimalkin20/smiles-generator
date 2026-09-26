import requests


compound_name = "aspirin"

url = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
    f"compound/name/{compound_name}/property/"
    "Title,CanonicalSMILES,IsomericSMILES,InChI,InChIKey/JSON"
)

headers = {
    "User-Agent": "SMILES-Generator/1.0 (educational cheminformatics project)"
}

print("Requesting:")
print(url)
print()

try:
    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    print("Status code:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print()

    print("Response:")
    print(response.text)

except requests.exceptions.Timeout:
    print("Request timed out.")

except requests.exceptions.ConnectionError as error:
    print("Connection error:")
    print(error)

except requests.exceptions.RequestException as error:
    print("Request failed:")
    print(error)