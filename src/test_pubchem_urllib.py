import urllib.request
import urllib.error


compound_name = "aspirin"

url = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
    f"compound/name/{compound_name}/property/"
    "Title,CanonicalSMILES,IsomericSMILES,InChI,InChIKey/JSON"
)

request = urllib.request.Request(
    url,
    headers={
        "User-Agent": "SMILES-Generator/1.0"
    }
)

try:
    with urllib.request.urlopen(request, timeout=20) as response:

        print("Status code:", response.status)
        print("Content-Type:", response.headers.get("Content-Type"))
        print()
        print(response.read().decode("utf-8"))

except urllib.error.HTTPError as error:

    print("HTTP Error:", error.code)
    print(error.read().decode("utf-8"))

except urllib.error.URLError as error:

    print("URL Error:", error.reason)