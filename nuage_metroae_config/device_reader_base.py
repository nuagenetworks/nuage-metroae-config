from logger import Logger

from errors import DeviceWriterError


class DeviceReaderBase(object):
    """
    Base class for reading information from devices.  This is an
    abstract base class, meaning that it cannot be instantiated
    on its own. It must act as a base for a device-specific derived class.
    """
    def __init__(self):
        """
        Abstract Base Class.  Cannot be instantiated directly. Use
        device-specific derived class.
        """
        self.log = Logger()
        self.log.set_to_stdout("ERROR", enabled=True)

    def set_logger(self, logger):
        self.log = logger

    def get_logger(self):
        return self.log

    def build_filter_list(self, filter, object_list):
        if type(filter) == dict and "%group" in filter:
            group_field = filter["%group"]
            if group_field not in filter:
                items = list()
                for obj in object_list:
                    value = self.query_attribute(obj, group_field)
                    if value not in items:
                        items.append(value)
            elif type(filter[group_field]) != list:
                items = [filter[group_field]]
            else:
                items = filter[group_field]

            filter_list = list()
            for item in items:
                filter_copy = dict(filter)
                filter_copy[group_field] = item
                filter_copy["%group_value"] = item
                filter_list.append(filter_copy)
        else:
            filter_list = [filter]

        return filter_list

    def filter_results(self, results, filter):
        filtered = list()
        sort_desc = False
        sort_field = None
        start = None
        end = None

        if filter is None:
            return results
        elif type(filter) == dict:
            for field_name in filter:
                if field_name.startswith("%"):
                    if field_name == "%start":
                        start = filter[field_name]
                    elif field_name == "%end":
                        end = filter[field_name]
                    elif field_name in ["%sort", "%sort_asc"]:
                        sort_field = filter[field_name]
                        sort_desc = False
                    elif field_name == "%sort_desc":
                        sort_field = filter[field_name]
                        sort_desc = True
                    elif field_name in ["%group", "%group_value"]:
                        pass
                    else:
                        raise DeviceWriterError(
                            "Invalid filter %s for query" % field_name)
        else:
            raise DeviceWriterError("Invalid filter for query")

        for result in results:
            if self._should_keep_result(result, filter):
                filtered.append(result)

        if sort_field is not None:
            def sort_func(result):
                return self.query_attribute(result, sort_field)

            filtered.sort(reverse=sort_desc, key=sort_func)

        return filtered[slice(start, end)]

    def filter_results_level(self, results, objects, attributes, level,
                             groups):
        values = list()

        if level >= len(objects):
            return self.filter_attributes(results, attributes)
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
                        values.extend(self.filter_results_level(
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
                values.extend(self.filter_results_level(cur,
                                                        objects,
                                                        attributes,
                                                        level,
                                                        groups))

        if groups != []:
            return groups

        return values

    def filter_attributes(self, current, attributes):
        if attributes is None:
            return [current]

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

    def _should_keep_result(self, result, filter):
        for attr_name in filter:
            if not attr_name.startswith("%"):
                result_value = self.query_attribute(result, attr_name)
                if type(filter[attr_name]) == list:
                    value_list = filter[attr_name]
                else:
                    value_list = [filter[attr_name]]

                if result_value not in value_list:
                    return False

        return True

    def group_results(self, groups, cur_filter, values):
        is_grouped = type(cur_filter) == dict and "%group_value" in cur_filter
        if is_grouped:
            group_value = cur_filter["%group_value"]
            for search_pair in groups:
                if search_pair[0] == group_value:
                    search_pair[1].extend(values)
                    return

            groups.append([group_value, values])

    # Abstract prototype functions
    # All types of device writer classes will need to implement these
    # functions in order to apply the configurations to the device.

    def start_session(self):
        """
        Starts a session with device
        """
        # Abstract prototype function
        raise NotImplementedError("Abstract base function not implemented")

    def stop_session(self):
        """
        Stops the session with device
        """
        # Abstract prototype function
        raise NotImplementedError("Abstract base function not implemented")

    def connect(self, *args):
        """
        Creates a new connection with another device
        """
        # Abstract prototype function
        raise NotImplementedError("Abstract base function not implemented")

    def query(self, objects, attributes):
        """
        Reads attributes from device
        """
        # Abstract prototype function
        raise NotImplementedError("Abstract base function not implemented")

    def query_attribute(self, object, attribute):
        """
        Reads an attribute from an object
        """
        # Abstract prototype function
        raise NotImplementedError("Abstract base function not implemented")
