import json

'''This code is a last minute addition in order to format the data coming in from the gateway into JSON files
to conform with last minute shortcomings from the data transferring side of the project"
The data on the "str" parameter is in format:
"timestamp(microseconds) MACaddress value(hexadecimal)"'''
def create_json(str):
    parts = str.split()
    l = len(parts)

    dictionary = {}

    i = 0
    while i < l:
        # combine measurement with timestamp
        not_hex = int(parts[i+2], 16)

        tup = (parts[i], not_hex)

        # check if address is already a key, if not, add it
        if parts[i+1] in dictionary.keys():
            dictionary[parts[i+1]].append(tup)
        else:
            dictionary[parts[i+1]] = [tup]

        i += 3

    print(dictionary)

    return dictionary
