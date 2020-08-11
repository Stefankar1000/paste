import json
import requests


def identify_language(content: str) -> str:
    uri = (
        "https://api.algorithmia.com/v1/algo/PetiteProgrammer/"
        "ProgrammingLanguageIdentification/0.1.3?timeout=300"
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Simple simq2CYjJfL3Itr9U7mENfFJIe91",
    }
    post = requests.post(uri, data=json.dumps(content), headers=headers)

    return str(post.json()["result"][0][0])
