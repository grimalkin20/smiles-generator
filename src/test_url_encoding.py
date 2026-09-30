from urllib.parse import quote

test_names = [
    "aspirin",
    "acetaminophen",
    "1-amino-3-(1H-imidazol-4-yl)propanoic acid",
    "N-acetryl-L-tyrosine"
    
]

for name in test_names:
    encoded = quote(name, safe="")
                    
    print("Original :", name)
    print("Encoded :", encoded)
    print()