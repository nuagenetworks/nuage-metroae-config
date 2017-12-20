import argparse
from vsd_writer import VsdWriter, Fetcher
import vspk.v5_0 as vspk


def main():
    # session = vspk.NUVSDSession(username='csproot',
    #                             password='csproot',
    #                             enterprise='csp',
    #                             api_url='https://localhost:8080')
    # session.start()
    # root = session.user
    # print str(root.get_resource_url())
    # print str(root.enterprises._prepare_url())
    # print str(root.enterprises.get_first())
    # ent = root.enterprises.get_first()
    # print str(ent.domains._prepare_url())
    # exit(0)
    # args = parse_args()
    vsd_writer = VsdWriter()
    vsd_writer.read_api_specifications('../vsd-api-specifications')
    vsd_writer.set_session_params('https://localhost:8080')
    vsd_writer.start_session()
    # obj = vsd_writer._get_new_config_object("Me")
    # print str(obj)
    # print str(vsd_writer.session.root_object._attributes)
    # print str(vsd_writer.session.get_root_object())
    print str(vsd_writer.session.root_object.get_resource_url())
    print str(vsd_writer.session.root_object.enterprises._prepare_url())
    print str(vsd_writer.session.root_object.enterprises.get_first())
    ent = vsd_writer.session.root_object.enterprises.get_first()
    print str(ent.to_dict())
    fetch = Fetcher()
    fetch.parent_object = ent
    print str(fetch._prepare_url())


def parse_args():
    parser = argparse.ArgumentParser(description='Runs metro-ansible steps')
    parser.add_argument('-m', '--metro-path', dest='metro_path',
                        action='store', required=False,
                        help='Path containing the metro deployment')


if __name__ == "__main__":
    main()
