import json
import zipfile

packageroot=os.path.join(os.path.split(os.path.realpath(__file__))[0],"models")


def install_local(name:str):
    with zipfile.ZipFile(name, "r") as z:
        id=json.loads(z.read("meta.json"))["id"]


def install(name:str):
    install_local(name)