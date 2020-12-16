def get_dict_field_no_case(data_dict, field):
    """
    Gets a field value out of a dictionary case-insensitively
    """
    if type(data_dict) != dict:
        raise TypeError("Not a dictionary")

    for key, value in data_dict.items():
        if str(key).lower() == field:
            return value

    return None
