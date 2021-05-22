import json
from scrape import models


area = models.Area.objects.all().values()
areaobj = models.Area.objects.get(area_name__contains="市川")
store = models.Store.objects.filter(area=areaobj).values("id","store_name","area__area_name")
len(store)
with open("json_for_algolia.json","w") as f:
    json.dump(list(store),f, indent=4)