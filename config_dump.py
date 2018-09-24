import argparse
import os
import urllib3
import yaml

from vsd_writer import VsdWriter

# Disables annoying SSL certificate validation warnings
urllib3.disable_warnings()

DEBUG = False

DESCRIPTION = """This tool dumps the configuration from a VSD as Yaml."""

DEFAULT_VSD_USERNAME = 'csproot'
DEFAULT_VSD_PASSWORD = 'csproot'
DEFAULT_VSD_ENTERPRISE = 'csp'
DEFAULT_URL = 'https://localhost:8080'
ENV_VSD_USERNAME = 'VSD_USERNAME'
ENV_VSD_PASSWORD = 'VSD_PASSWORD'
ENV_VSD_ENTERPRISE = 'VSD_ENTERPRISE'
ENV_VSD_URL = 'VSD_URL'
ENV_VSD_SPECIFICATIONS = 'VSD_SPECIFICATIONS_PATH'

VSD_CSP_ENTERPRISE_GUID = "76046673-d0ea-4a67-b6af-2829952f0812"
ROOT_OBJECT_NAME = "me"
FILTER_OBJECTS = ['keyservermember', 'enterprisesecurity',
                  'l7applicationsignature', 'vrsredeploymentpolicy',
                  'vrsaddressrange', 'job', 'containerresync',
                  'ingressexternalservicetemplate',
                  'applicationperformancemanagement', 'l4service',
                  'ltestatistics', 'eventlog']


class MissingSubset(Exception):
    pass


class NotRemoved(Exception):
    pass


class ChildError(Exception):
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
        if DEBUG:
            print object_name
        try:
            contexts = vsd_writer.get_object_list(object_name.lower(),
                                                  parent_context)
            for context in contexts:
                if DEBUG:
                    print "%s vs %s" % (context.current_object.parent_id,
                                        parent_id)
                if (context.current_object.parent_id == parent_id or
                        context.current_object.parent_id is None):
                    if DEBUG:
                        print_object(context.current_object)
                    child = walk_object_children(
                        vsd_writer,
                        context.current_object.get_name(),
                        context.current_object.id,
                        context)
                    children.append(child)
        except ChildError as e:
            raise e
        except Exception as e:
            print "# ERROR in %s: %s" % (object_name, str(e))
            if not args.ignore_errors:
                raise ChildError()

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
                        except NotRemoved:
                            pass

        if not args.expect_removed and not found:
            missing_yaml = yaml.safe_dump(child_subset,
                                          default_flow_style=False,
                                          default_style='')
            raise MissingSubset("\n\n" + missing_yaml)

        if args.expect_removed and found:
            extra_yaml = yaml.safe_dump(child_subset,
                                        default_flow_style=False,
                                        default_style='')
            raise NotRemoved("\n\n" + extra_yaml)


def compare_objects(superset_obj, subset_obj):
    for subset_name, subset_value in subset_obj['attributes'].items():
        if (subset_name not in superset_obj['attributes'] or
                superset_obj['attributes'][subset_name] != subset_value):
            return False

    return True


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('-sp', '--spec-path', dest='spec_path',
                        action='store', required=False,
                        help=('Path containing object specifications. Can also'
                              ' set using environment variable %s') % (
                                  ENV_VSD_SPECIFICATIONS))

    parser.add_argument('-v', '--vsd-url', dest='vsd_url',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_URL, DEFAULT_URL),
                        help=('URL to VSD REST API. Can also set using '
                              'environment variable %s') % (ENV_VSD_URL))

    parser.add_argument('-u', '--username', dest='username',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_USERNAME,
                                          DEFAULT_VSD_USERNAME),
                        help=('Username for VSD. Can also set using '
                              'environment variable %s') % (ENV_VSD_USERNAME))

    parser.add_argument('-p', '--password', dest='password',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_PASSWORD,
                                          DEFAULT_VSD_PASSWORD),
                        help=('Password for VSD. Can also set using '
                              'environment variable %s') % (ENV_VSD_PASSWORD))

    parser.add_argument('-e', '--enterprise', dest='enterprise',
                        action='store', required=False,
                        default=os.getenv(ENV_VSD_ENTERPRISE,
                                          DEFAULT_VSD_ENTERPRISE),
                        help=('Enterprise for VSD. Can also set using '
                              'environment variable %s') % (
                                  ENV_VSD_ENTERPRISE))

    parser.add_argument('-c', '--compare-file', dest='compare_file',
                        action='store', required=False, default=None,
                        help=('Compare configuration against a provided Yaml '
                              'file. All given objects must be contained on '
                              'the VSD.'))

    parser.add_argument('-rr', '--resolve-references',
                        dest='resolve_references',
                        action='store_true', required=False, default=False,
                        help=('Resolve any ID references in the config to'
                              ' name based tokens'))

    parser.add_argument('-i', '--ignore-errors',
                        dest='ignore_errors',
                        action='store_true', required=False, default=False,
                        help=('Ignore any errors found'))

    parser.add_argument('-er', '--expect-removed',
                        dest='expect_removed',
                        action='store_true', required=False, default=False,
                        help=('Verify that expected config was removed'))

    return parser.parse_args()


def main():
    global args
    args = parse_args()

    if args.spec_path is None:
        print "Specifications path -sp is required"
        exit(1)

    vsd_writer = VsdWriter()
    vsd_writer.read_api_specifications(args.spec_path)
    vsd_writer.set_session_params(args.vsd_url,
                                  username=args.username,
                                  password=args.password,
                                  enterprise=args.enterprise)
    vsd_writer.start_session()

    config = walk_object_children(vsd_writer, ROOT_OBJECT_NAME,
                                  VSD_CSP_ENTERPRISE_GUID)

    if args.resolve_references is True or args.compare_file is not None:
        guid_map = get_guid_map(config)
        resolve_references(config, guid_map)

    print yaml.safe_dump(config, default_flow_style=False, default_style='')

    if args.compare_file is not None:
        subset_config = read_configuration(args.compare_file)
        compare_tree(config, subset_config)


if __name__ == "__main__":
    main()
