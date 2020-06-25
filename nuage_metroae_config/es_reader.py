import requests
import sys

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
MAX_RESULTS = 10000
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

    def connect(self, *args):
        """
        Creates a new connection with another device
        """
        if len(args) < 1:
            raise Exception("address parameter is required for connect")
        address = args[0]

        if len(args) < 2:
            port = DEFAULT_PORT
        else:
            port = int(args[1])

        if len(args) > 2:
            raise SessionError("Too many arguments to connect")

        self.stop_session()

        self.set_session_params(address, port)

        self.start_session()

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
        query_filter = objects[0]["filter"]
        (max, start) = self._get_filter_max_index_pair(query_filter)
        raw_results = self._query_to_es(search_url, max, start)
        return self._filter_results(raw_results, objects, attributes)

    def _build_search_url(self, objects):
        index = objects[0]["name"]
        query_filter = objects[0]["filter"]
        query_params = self._build_search_query_url_params(query_filter)
        url = "http://%s:%s/%s/_search?%s" % (self.session_params["address"],
                                              self.session_params["port"],
                                              index,
                                              query_params)

        return url

    def _build_search_query_url_params(self, query_filter):
        query_params = ""
        if query_filter is None:
            pass
        elif type(query_filter) == int:
            pass
        elif type(query_filter) == dict:
            fields = list()
            for field_name in query_filter:
                if field_name.startswith("%"):
                    if field_name in ["%max", "%start"]:
                        pass
                    elif field_name in ["%sort", "%sort_asc"]:
                        query_params += "sort=%s:asc&" % (
                            query_filter[field_name])
                    elif field_name == "%sort_desc":
                        query_params += "sort=%s:desc&" % (
                            query_filter[field_name])
                    else:
                        raise Exception(
                            "Invalid filter %s for ES index query" %
                            field_name)
                else:
                    fields.append("%s:%s" % (field_name,
                                             query_filter[field_name]))
            if len(fields) > 0:
                query_params += "q="
                query_params += " AND ".join(fields)
                query_params += "&"

        elif query_filter == "*":
            pass
        else:
            raise Exception("Invalid filter for ES index query")

        return query_params

    def _get_filter_max_index_pair(self, filter):
        if type(filter) == dict:
            start = 0
            if "%start" in filter:
                start = int(filter["%start"])
            max = MAX_RESULTS
            if "%max" in filter:
                max = int(filter["%max"])
            return (max, start)
        if type(filter) == int:
            raise Exception("Cannot use position for ES index query, use "
                            "[%%max=1 & %%start=%s & %%sort=<field>] filters"
                            " instead" % filter)
        else:
            return (MAX_RESULTS, 0)

    def _query_to_es(self, search_url, max=MAX_RESULTS, start=0):

        results = list()
        if max < 0:
            size = PAGE_SIZE
        else:
            size = min(max, PAGE_SIZE)
        while start < max:
            result_page = self._query_page_from_es(search_url, start, size)
            if len(result_page) == 0:
                break
            results.extend(result_page)
            start += size
        return results

    def _query_page_from_es(self, search_url, start, size):
        search_url += "from=%d&size=%d" % (start, size)
        self.log.debug("GET " + search_url)


        resp = requests.get(search_url, verify=False)

        results = dict()
        self.log.debug("Status: %d" % resp.status_code)
        if resp.status_code == 200:
            results = resp.json()
        else:
            raise Exception("Status code %d from URL %s" % (
                            resp.status_code, search_url))

        return self._extract_results(results)

    def _extract_results(self, results):
        if "hits" not in results or "hits" not in results["hits"]:
            return list()

        hits = results["hits"]["hits"]
        return [x["_source"] for x in hits]

    def _filter_results(self, results, objects, attributes):
        filtered = list()

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

