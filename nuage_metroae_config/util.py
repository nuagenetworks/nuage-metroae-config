
TEMPLATE_ABREVIATION_MAP = {
    "Application": "App",
    "Management": "Mgmt",
    "Performance": "Perf",
    "Security": "Sec"
}


TEMPLATE_EXPANTION_MAP = {
    "App": "Application",
    "Mgmt": "Management",
    "Perf": "Performance",
    "Sec": "Security"
}


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


def get_abreviated_template_name(template_name):
    """
    Gets an abreviated template name
    """
    abreviated_template_name = ""
    for n in template_name.split(" "):
        abreviated_template_name += " " + (TEMPLATE_ABREVIATION_MAP[n] if n in TEMPLATE_ABREVIATION_MAP else n)

    return abreviated_template_name.strip()


def get_expanded_template_name(template_name):
    """
    Gets an expanded template name
    """
    expanded_template_name = ""
    for n in template_name.split(" "):
        expanded_template_name += " " + (TEMPLATE_EXPANTION_MAP[n] if n in TEMPLATE_EXPANTION_MAP else n)

    return expanded_template_name.strip().lower()
