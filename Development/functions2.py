


def print_pretty_dict(d, indent=0):
    # for key, value in d.items():
    #     print('\t' * indent + str(key))
    #     if isinstance(value, dict):
    #         print_pretty_dict(value, indent+1)
    #     else:
    #         print('\t' * (indent+1) + str(value))
    # for key, value in d.items():
    for key in sorted(d.iterkeys()):
        value = d[key]
        if isinstance(value, dict):
            print('\t' * indent + str(key))
            print_pretty_dict(value, indent+1)
        else:
            print('\t' * indent + str(key) + ': ' + str(value))