"""
:type tool
:group Core
:category Core
:summary Open the current Juniper git repo in the browser
:icon icons\\programs\\other\\git.png
"""
import os
import json

import juniper


with open(os.path.join(juniper.paths.root(), "Config\\juniper.json"), "r") as j:
    json_data = json.load(j)
    url = json_data["url"]
    os.system("start \"\" " + url)
