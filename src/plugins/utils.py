def is_iterable(obj):
    return hasattr(obj, '__iter__')

def pack_dictionary(dictionary, delimiter='|'):
    new_dict = dict()
    for (key, value) in dictionary.items():
        if is_iterable(value):
            new_dict[key] = delimiter.join(value)
        else:
            new_dict[key] = value
    return new_dict


