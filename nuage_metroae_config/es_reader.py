import requests

from .device_reader_base import DeviceReaderBase
from .errors import (DeviceWriterError,
                     SessionError)

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
        self.query_cache = dict()

    def set_session_params(self, address, port=None):
        """
        Sets the parameters necessary to connect to the ES.  This must
        be called before reading or an exception will be raised.
        """
        if port is None:
            port = DEFAULT_PORT

        self.session_params = {
            'address': address,
            'port': port}

    def start_session(self):
        """
        Starts a session with the ES
        """
        location = "Session start %s" % str(self.session_params)

        self.log.debug(location)

        self._check_session()

        self.query_cache = dict()

    def stop_session(self):
        """
        Stops the session with the ES
        """
        self.log.debug("Session stopping")

    def connect(self, *args):
        """
        Creates a new connection with another device
        """
        if len(args) < 1:
            raise SessionError("address parameter is required for connect")
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

    def query_attribute(self, obj, attribute):
        """
        Reads an attribute from an object
        """
        if type(obj) == dict and attribute in obj:
            return obj[attribute]

        return None

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
        (start, end) = self._get_filter_index_pair(query_filter)
        es_results = self._query_to_es(search_url, start, end)
        return self._filter_es_results(es_results, objects, attributes, list())

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
        elif type(query_filter) == dict:
            fields = list()
            for field_name in query_filter:
                if field_name.startswith("%"):
                    if field_name in ["%end", "%start", "%group"]:
                        pass
                    elif field_name in ["%sort", "%sort_asc"]:
                        query_params += "sort=%s:asc&" % (
                            query_filter[field_name])
                    elif field_name == "%sort_desc":
                        query_params += "sort=%s:desc&" % (
                            query_filter[field_name])
                    else:
                        raise EsError(
                            "Invalid filter %s for ES index query" %
                            field_name)
                else:
                    if type(query_filter[field_name]) == list:
                        raise EsError("ES index query does not support"
                                      " attribute value lists")
                    fields.append("%s:%s" % (field_name,
                                             query_filter[field_name]))
            if len(fields) > 0:
                query_params += "q="
                query_params += " AND ".join(fields)
                query_params += "&"

        else:
            raise EsError("Invalid filter for ES index query")

        return query_params

    def _get_filter_index_pair(self, filter):
        if type(filter) == dict:
            start = 0
            if "%start" in filter:
                start = int(filter["%start"])
                if start < 0:
                    raise EsError("ES index queries do not support negative"
                                  " indicies, use positive indicies and "
                                  "reverse sort")
            end = MAX_RESULTS
            if "%end" in filter:
                end = int(filter["%end"])
                if end < 0:
                    raise EsError("ES index queries do not support negative"
                                  " indicies, use positive indicies and "
                                  "reverse sort")

            return (start, end)
        else:
            return (0, MAX_RESULTS)

    def _query_to_es(self, search_url, start=0, end=MAX_RESULTS):
        results = list()
        current = start
        while current < end:
            size = min(end - current, PAGE_SIZE)
            result_page = self._query_page_from_es(search_url, current, size)
            results.extend(result_page)
            current += size
            if len(result_page) < size:
                break
        return results

    def _query_page_from_es(self, search_url, start, size):
        search_url += "from=%d&size=%d" % (start, size)
        self.log.debug("GET " + search_url)

        if search_url in self.query_cache:
            return self.query_cache[search_url]

        resp = requests.get(search_url, verify=False)

        results = dict()
        self.log.debug("Status: %d" % resp.status_code)
        if resp.status_code == 200:
            results = resp.json()
        else:
            raise EsError("Status code %d from URL %s" % (
                          resp.status_code, search_url))

        extracted = self._extract_results(results)

        self.query_cache[search_url] = list(extracted)
        return extracted

    def _extract_results(self, results):
        if "hits" not in results or "hits" not in results["hits"]:
            return list()

        hits = results["hits"]["hits"]
        return [x["_source"] for x in hits]

    def _filter_es_results(self, results, objects, attributes, groups):

        filter = objects[0]["filter"]
        filter_list = self.build_filter_list(filter, results)

        if type(filter) != dict or "%group" not in filter:
            groups = list()

        values = list()
        for cur_filter in filter_list:
            self.log.debug("Current filter: " + str(cur_filter))
            values = list()

            if type(cur_filter) == dict and "%group" in cur_filter:
                child_group = list()
                partial_results = self.filter_results(results, cur_filter)
            else:
                child_group = groups
                partial_results = results

            for cur in partial_results:
                values.extend(self.filter_results_level(cur,
                                                        objects,
                                                        attributes, 1,
                                                        child_group))

            if child_group != []:
                self.group_results(groups, cur_filter, child_group)
                values = child_group
            else:
                self.group_results(groups, cur_filter, values)

        if groups != []:
            return groups

        return values
