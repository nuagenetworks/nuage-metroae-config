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
    # ent = vsd_writer._get_fetcher("Enterprise").get_first(filter='ID is "7bb7788c-d277-4b36-8268-d5f7ca8d978d"')
    # print str(ent)
    # print str(ent.to_dict())
    # domain = vsd_writer._get_fetcher("Domain", ent).get_first()
    # print str(domain)

    # domain = vsd_writer._get_new_config_object("Domain")
    # print str(domain.to_dict())
    # domain.name = "test3"
    # domain.templateid = "3b791e3b-93a5-4d22-b38e-2336aad7132d"
    # ent.current_child_name = "domains"
    # ent.create_child(domain)
    # vsd_writer._add_object(domain, ent)

    # domain.description = "It works"
    # domain.save()

    # new_ent = vsd_writer._get_new_config_object("Enterprise")
    # new_ent.name = "test_ent"
    # vsd_writer._add_object(new_ent)

    # print str(ent)
    # print str(ent.to_dict())

    # ents = vsd_writer._get_fetcher("Enterprise").get()
    # for ent in ents:
    #     print str(ent)
    #     print str(ent.to_dict())


    # obj = vsd_writer._get_new_config_object("Me")
    # print str(obj)
    # print str(vsd_writer.session.root_object._attributes)
    # print str(vsd_writer.session.get_root_object())
    # print str(vsd_writer.session.root_object.get_resource_url())
    # print str(vsd_writer.session.root_object.enterprises._prepare_url())
    # print str(vsd_writer.session.root_object.enterprises.get_first())
    # ent = vsd_writer.session.root_object.enterprises.get(filter='id is 7bb7788c-d277-4b36-8268-d5f7ca8d978d')
    # print str(ent[0].to_dict())
    # fetch = Fetcher()
    # fetch.parent_object = ent
    # print str(fetch._prepare_url())

    # ent = vsd_writer._get_fetcher("Enterprise").get_first(filter='name is "test_ent"')
    # print str(ent)
    # ent.delete()

    # ent = vsd_writer._get_fetcher("Enterprise").get_first()
    # print str(ent.name)
    # dom = vsd_writer._get_fetcher("Domain", ent).get_first(filter='name is "test2"')
    # print str(dom.name)
    # dom.delete()

    ent = vsd_writer._select_object("Enterprise", "id", "7bb7788c-d277-4b36-8268-d5f7ca8d978d")
    dom = vsd_writer._select_object("Domain", "name", "test2", ent)
    print str(dom)


def parse_args():
    parser = argparse.ArgumentParser(description='Runs metro-ansible steps')
    parser.add_argument('-m', '--metro-path', dest='metro_path',
                        action='store', required=False,
                        help='Path containing the metro deployment')


if __name__ == "__main__":
    main()
