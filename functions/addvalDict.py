def addValDict(sample_dict, key, list_of_values):
    if key not in sample_dict:
        sample_dict[key] = list()
    sample_dict[key].extend(list_of_values)
    return sample_dict


def getKeyDict(dict,value):
    key = [key
                for key, obj in dict.items()
                if value in obj]
    return key