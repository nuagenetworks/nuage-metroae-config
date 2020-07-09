import requests

from device_reader_base import DeviceReaderBase
from errors import (DeviceWriterError,
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

    def set_session_params(self, address, port=None):
        """
        Sets the parameters necessary to connect to the ES.  This must
        be called before writing or an exception will be raised.
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
        return self._filter_es_results(es_results, objects, attributes)

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
                    if field_name in ["%end", "%start"]:
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

        self.log.debug("%d %d" % (end, start))

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

        resp = requests.get(search_url, verify=False)

        results = dict()
        self.log.debug("Status: %d" % resp.status_code)
        if resp.status_code == 200:
            results = resp.json()
        else:
            raise EsError("Status code %d from URL %s" % (
                          resp.status_code, search_url))

        return self._extract_results(results)

    def _extract_results(self, results):
        if "hits" not in results or "hits" not in results["hits"]:
            return list()

        hits = results["hits"]["hits"]
        return [x["_source"] for x in hits]

    def _filter_es_results(self, results, objects, attributes):

        filtered = list()
        for next in results:
            filtered.extend(self._filter_es_results_level(next,
                                                          objects,
                                                          attributes))

        return filtered

    def _filter_es_results_level(self, results, objects, attributes, level=1):
        filtered = list()

        if level >= len(objects):
            return self._filter_attributes(results, attributes)
        else:
            obj_name = objects[level]["name"]
            filter = objects[level]["filter"]
            if type(results) == list:

                for next in self.filter_results(results, filter):
                    filtered.extend(self._filter_es_results_level(next,
                                                                  objects,
                                                                  attributes,
                                                                  level + 1))

            elif type(results) == dict and obj_name in results:
                next = results[obj_name]
                if type(next) != list:
                    level += 1
                filtered.extend(self._filter_es_results_level(next,
                                                              objects,
                                                              attributes,
                                                              level))

        return filtered

    def _filter_attributes(self, current, attributes):
        if type(current) != dict:
            self.log.debug("Attempting to get attributes from a result that"
                           " is not an object")
            return list()
        if type(attributes) == list:
            attr_dict = dict()
            if attributes[0] == "*":
                attr_dict = current
            else:
                for attribute in attributes:
                    if attribute in current:
                        attr_dict[attribute] = current[attribute]
                    else:
                        self.log.debug("Missing attribute %s in result" %
                                       attribute)
            return [attr_dict]
        else:
            if attributes in current:
                return [current[attributes]]
            else:
                self.log.debug("Missing attribute %s in result" % attributes)
                return list()
