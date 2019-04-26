import pandas as pd

dataset = pd.read_csv('model/diet-compositions-by-commodity-categories-fao-2017.csv', low_memory=False)
keys = dataset.columns.values.tolist()
keys.sort()
entities = list()
for i in range(0,len(dataset['Entity'])):
	entities.append(dataset['Entity'][i])
	#print(entities)
entities = list(set(entities))

country = "Afghanistan"
country_data = list()
for i in range(0,len(dataset['Entity'])):
	if dataset['Entity'][i] == country:
		ds = list(dataset.ix[i])
		for i in range(0,len(ds)):
			typeVal = type(ds[i]).__name__
			if typeVal == 'int64':
				ds[i] = ds[i].item()
			if typeVal == 'float64':
				ds[i] = ds[i].item()
		ds_dict = dict()
		for i in range(0,len(ds)):
			ds_dict.update({keys[i]: ds[i]})
		print(ds_dict)
		country_data.append(ds)
#print(country_data)
