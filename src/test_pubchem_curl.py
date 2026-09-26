import subprocess

compound_name = "aspirin"

url = (
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"
    f"compound/name/{compound_name}/property/"
    "Title,CanonicalSMILES,IsomericSMILES,InChI,InChIKey/JSON"
)

result = subprocess.run(
    [
        "curl.exe",
        "-A",
        "SMILES-Generator/1.0",
        url
    ],
    capture_output=True,
    text=True
)

print("Return code:", result.returncode)
print()

if result.stdout:
    print("Response:")
    print(result.stdout)

if result.stderr:
    print("Errors:")
    print(result.stderr)