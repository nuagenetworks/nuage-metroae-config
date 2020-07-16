from device_reader_base import DeviceReaderBase


class VariableReader(DeviceReaderBase):
    """
    Extracts results from internal variables.  This class is a derived class
    from the DeviceReaderBase Abstract Base Class.
    """

    def __init__(self):
        """
        Derived class from DeviceWriterBase.
        """
        super(VariableReader, self).__init__()
        self.data = list()

    def set_data(self, data):
        """
        Sets the data to extract results from
        """
        self.data = data

    def start_session(self):
        """
        Starts a session (not needed to be called)
        """
        self.log.debug("Session start")

    def stop_session(self):
        """
        Stops the session (not needed to be called)
        """
        self.log.debug("Session stopping")

    def query(self, objects, attributes):
        """
        Reads attributes from internal data
        """
        location = "Query %s : %s" % (objects, attributes)

        print location

        self.log.debug(location)

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

    def _query(self, objects, attributes):

        return self._filter_results_level(self.data, objects, attributes, 0,
                                          list())

    def _filter_results_level(self, results, objects, attributes, level,
                              groups):
        values = list()

        if level >= len(objects):
            return self._filter_attributes(results, attributes)
        else:
            obj_name = objects[level]["name"]
            filter = objects[level]["filter"]

            if type(results) == list:

                filter_list = self.build_filter_list(filter, results)

                for cur_filter in filter_list:
                    self.log.debug("Current filter: " + str(cur_filter))
                    values = list()
                    if type(filter) != dict or "%group" not in filter:
                        child_group = groups
                    else:
                        child_group = list()

                    for cur in self.filter_results(results, cur_filter):
                        values.extend(self._filter_results_level(
                            cur, objects, attributes, level + 1, child_group))

                    if child_group != []:
                        self.group_results(groups, cur_filter, child_group)
                        values = child_group
                    else:
                        self.group_results(groups, cur_filter, values)

            elif type(results) == dict and obj_name in results:
                cur = results[obj_name]
                if type(cur) != list:
                    level += 1
                values.extend(self._filter_results_level(cur,
                                                         objects,
                                                         attributes,
                                                         level,
                                                         groups))

        if groups != []:
            return groups

        return values

    def _filter_attributes(self, current, attributes):
        if attributes is None:
            return current

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
