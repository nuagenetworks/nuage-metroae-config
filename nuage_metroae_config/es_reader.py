import json
import requests

from device_reader_base import DeviceReaderBase
from errors import (DeviceWriterError,
                    InvalidAttributeError,
                    InvalidObjectError,
                    InvalidValueError,
                    MissingSelectionError,
                    MultipleSelectionError,
                    SessionError,
                    SessionNotStartedError)

PAGE_SIZE = 100
DEFAULT_PORT = 9200


class EsError(SessionError):
    """
    Exception class when there is an error from Elasticsearch
    """
    pass


class MissingSessionParamsError(DeviceWriterError):
    """
    Exception class when session is started without parameters specified
    """
    pass


class EsReader(DeviceReaderBase):
    """
    Performs queries on ElasticSearch.  This class is a derived class from
    the DeviceReaderBase Abstract Base Class.
    """

    def __init__(self):
        """
        Derived class from DeviceWriterBase.
        """
        super(EsReader, self).__init__()
        self.session_params = None

    def set_session_params(self, address, port=None):
        """
        Sets the parameters necessary to connect to the VSD.  This must
        be called before writing or an exception will be raised.
        """
        if port is None:
            port = DEFAULT_PORT

        self.session_params = {
            'address': address,
            'port': port}

    def start_session(self):
        """
        Starts a session with the VSD
        """
        location = "Session start %s" % str(self.session_params)

        self.log.debug(location)

        self._check_session()

    def stop_session(self):
        """
        Stops the session with the VSD
        """
        self.log.debug("Session stopping")

    def query(self, objects, attributes):
        """
        Reads attributes from device
        """
        location = "Query %s : %s" % (objects, attributes)
        self.log.debug(location)
        self._check_session()

        return self._query(objects, attributes)

    #
    # Private functions to do the work
    #

    def _check_session(self):
        if self.session_params is None:
            raise MissingSessionParamsError(
                "Cannot start session without parameters")

    def _query(self, objects, attributes):
        search_url = self._build_search_url(objects)
        self.log.debug(search_url)
        raw_results = self._query_to_es(search_url)
        return self._filter_results(raw_results, objects, attributes)

    def _build_search_url(self, objects):
        # print str(objects)
        index = objects[0]["name"]
        url_base = "http://%s:%s/%s/_search" % (self.session_params["address"],
                                                self.session_params["port"],
                                                index)

        return url_base

    def _query_to_es(self, search_url):
        results = self._query_page_from_es(search_url, 0, PAGE_SIZE)
        return results

    def _query_page_from_es(self, search_url, page, size):
        resp = requests.get(search_url, verify=False)

        results = dict()
        if resp.status_code == 200:
            results = resp.json()
        else:
            raise Exception("Status code %d from URL %s" % (
                            resp.status_code, search_url))

        # print str(results)

        return self._extract_results(results)

    def _extract_results(self, results):
        if "hits" not in results or "hits" not in results["hits"]:
            return list()

        hits = results["hits"]["hits"]
        return [x["_source"] for x in hits]

    def _filter_results(self, results, objects, attributes):
        filtered = list()

        print str(objects)

        for result in results:
            current = result
            for obj in objects[1:]:
                if type(current) == dict and obj["name"] in current:
                    current = current[obj["name"]]
                    if type(obj["filter"]) == int:
                        if type(current) != list:
                            raise Exception("Object %s is not a list" %
                                            obj["name"])
                        current = current[obj["filter"]]
                else:
                    raise Exception("Missing object %s in result" %
                                    obj["name"])

            filtered.append(self._filter_attributes(current, attributes))

        return filtered

    def _filter_attributes(self, current, attributes):
        if type(current) != dict:
            raise Exception("Attempting to get attributes from a result that"
                            " is not an object")
        if type(attributes) == list:
            attr_dict = dict()
            if attributes[0] == "*":
                attr_dict = current
            else:
                for attribute in attributes:
                    if attribute in current:
                        attr_dict[attribute] = current[attribute]
                    else:
                        raise Exception("Missing attribute %s in result" %
                                        attribute)
            return attr_dict
        else:
            if attributes in current:
                return current[attributes]
            else:
                raise Exception("Missing attribute %s in result" % attributes)

