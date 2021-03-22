
import argparse
from metroae_config import MetroConfig


def main():
    parser = argparse.ArgumentParser(prog="yaml to excel")
    add_parser_arguments(parser)
    args = parser.parse_args()

    yamlToExcel = YamlToExcel(args)
    yamlToExcel.run()


def add_parser_arguments(parser):
    parser.add_argument('-tp', '--template_path', dest='template_path',
                        action='append', required=False,
                        default=None,
                        help='Path containing template files.')
    parser.add_argument('-d', '--data_path', dest='data_path',
                        action='append', required=False,
                        help="Path contain the example user data")
    parser.add_argument('template_names',
                        nargs="*",
                        help='Template names')


class YamlToExcel(object):

    def __init__(self, args):
        self.args = args
        self.args.software_version = None
        self.metroConfig = MetroConfig(self.args, None)
        self.metroConfig.setup_template_store()

    def run(self):

        self.metroConfig.write_excel_input_form(self.args.template_names, self.args.data_path[0])


if __name__ == "__main__":
    main()
