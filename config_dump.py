import argparse
import yaml

from vsd_writer import VsdWriter


RESOLVE_REFERENCES = True
COMPARE_FILE = "/Users/mpiecuch/Downloads/expected_subset.yml"
VSD_API_SPECS = "/Users/mpiecuch/vsd-api-specifications"
VSD_USERNAME = "csproot"
VSD_PASSWORD = "csproot"
VSD_ENTERPRISE = "csp"
VSD_URL = "https://localhost:8080"
ROOT_OBJECT_NAME = "me"
FILTER_OBJECTS = ['keyservermember', 'enterprisesecurity',
                  'l7applicationsignature', 'vrsredeploymentpolicy',
                  'vrsaddressrange', 'job', 'containerresync',
                  'ingressexternalservicetemplate',
                  'nsgateway']


class MissingSubset(Exception):
    pass


def print_object(obj):
    print obj.get_name()
    for attr_name, attr in obj._attributes.items():
        print "    %s: %s" % (attr_name, str(getattr(obj, attr_name)))


def build_object_dict(obj, children):
    object_dict = dict()
    attributes = dict()
    object_dict[obj.get_name()] = {"attributes": attributes,
                                   "children": children}

    for attr_name, attr in obj._attributes.items():
        attributes[attr_name] = getattr(obj, attr_name)

    return object_dict


def walk_object_children(vsd_writer, object_name, parent_id=None,
                         parent_context=None):
    children_names = get_child_names(vsd_writer, vsd_writer.specs[
        object_name.lower()])
    children = list()
    for object_name in children_names:
        # print object_name
        contexts = vsd_writer.get_object_list(object_name.lower(),
                                              parent_context)
        for context in contexts:
            # print "%s vs %s" % (context.current_object.parent_id, parent_id)
            if context.current_object.parent_id == parent_id:
                # print_object(context.current_object)
                child = walk_object_children(vsd_writer,
                                             context.current_object.get_name(),
                                             context.current_object.id,
                                             context)
                children.append(child)

    if parent_context is None:
        return children
    else:
        object_dict = build_object_dict(parent_context.current_object,
                                        children)
        return object_dict


def get_child_names(vsd_writer, spec):
    child_object_names = list()
    children = spec['children']
    child_rest_names = [x['rest_name'] for x in children]
    for name_key, spec in vsd_writer.specs.items():
        if (spec['model']['rest_name'] in child_rest_names and
                spec['model']['get'] is True and
                spec['model']['rest_name'] not in FILTER_OBJECTS):
            child_object_names.append(spec['model']['entity_name'])

    return child_object_names
    # if 'Enterprise' in child_object_names:
    #     return ['Enterprise']
    # if 'Domain' in child_object_names:
    #     return ['Domain']
    # return []


def get_guid_map(children, guid_map=None):
    if guid_map is None:
        guid_map = dict()

    for child in children:
        for obj_type, obj in child.items():
            if 'id' in obj['attributes']:
                guid = obj['attributes']['id']
                if 'name' in obj['attributes']:
                    name = obj['attributes']['name']
                else:
                    name = "????"
                guid_map[guid] = "$(%s,name,%s)" % (obj_type, name)

            get_guid_map(obj['children'], guid_map)

    return guid_map


def resolve_references(children, guid_map):
    for child in children:
        for obj_type, obj in child.items():
            for attr_name, attr_value in obj['attributes'].items():
                if attr_name != 'id' and str(attr_value) in guid_map:
                    obj['attributes'][attr_name] = guid_map[attr_value]

            resolve_references(obj['children'], guid_map)


def read_configuration(filename):
    with open(filename, 'r') as file:
        return yaml.safe_load(file.read())


def compare_tree(superset, subset):

    for child_subset in subset:
        found = False
        for subset_obj_type, subset_obj in child_subset.items():
            for child_superset in superset:
                for superset_obj_type, superset_obj in child_superset.items():
                    if (superset_obj_type == subset_obj_type and
                            compare_objects(superset_obj, subset_obj)):
                        try:
                            compare_tree(superset_obj['children'],
                                         subset_obj['children'])
                            found = True
                        except MissingSubset:
                            pass

        if not found:
            missing_yaml = yaml.safe_dump(child_subset,
                                          default_flow_style=False,
                                          default_style='')
            raise MissingSubset("\n\n" + missing_yaml)


def compare_objects(superset_obj, subset_obj):
    for subset_name, subset_value in subset_obj['attributes'].items():
        if (subset_name not in superset_obj['attributes'] or
                superset_obj['attributes'][subset_name] != subset_value):
            return False

    return True


def main():

    vsd_writer = VsdWriter()
    vsd_writer.read_api_specifications(VSD_API_SPECS)
    vsd_writer.set_session_params(VSD_URL,
                                  username=VSD_USERNAME,
                                  password=VSD_PASSWORD,
                                  enterprise=VSD_ENTERPRISE)
    vsd_writer.start_session()

    config = walk_object_children(vsd_writer, ROOT_OBJECT_NAME)

    if RESOLVE_REFERENCES is True:
        guid_map = get_guid_map(config)
        resolve_references(config, guid_map)
        # print str(guid_map)

    print yaml.safe_dump(config, default_flow_style=False, default_style='')

    if COMPARE_FILE is not None:
        subset_config = read_configuration(COMPARE_FILE)
        compare_tree(config, subset_config)


if __name__ == "__main__":
    main()
