from neurodocker.reproenv.state import registered_templates_items

software = {"name": [], "url": []}
for s in registered_templates_items():
    if s[1]["name"] == "_header":
        continue
    software["name"].append(s[1]["name"])
    software["url"].append(s[1]["url"])

# sort alphabetically
for s in sorted(zip(software["name"], software["url"])):
    print(f"- `{s[0]} <{s[1]}>`_")
