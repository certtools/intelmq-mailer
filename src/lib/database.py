from pymongo import MongoClient
import re

class Database(object):
    
    def __init__(self, host, port, database, collection):
        if type(port) != int:
            port = int(port)
        client = MongoClient(host, port)
        #client.the_database.authenticate('user', 'password', source='source_database')
        self.collection = client[database][collection]
        
    def _merge_filters(self, *args):
        if any(args):
            new_dict = dict()
            for arg in args:
                if arg is not None:
                    new_dict.update(arg)
            return new_dict
        else:
            return None

    def _transform_combination(self, combination):
        return combination
    
    def _transform_filter(self, refine):
        if refine is None:
            return None

        refine_filter = dict()
        for (key, value) in refine.items():
            if key.startswith('!'):
                refine_filter[key[1:]] = {"$not": re.compile(value, re.IGNORECASE)} #TODO: maybe I shouldn't put this as "default"
            else:
                refine_filter[key] = re.compile(value, re.IGNORECASE) #TODO: maybe I shouldn't put this as "default"

        return refine_filter

    def _transform_fields(self, fields):
        if fields is None:
            return None

        transformed_fields = {'_id': False}

        for field in fields:
            transformed_fields[field] = True

        return transformed_fields
    
    def _transform_date_filter(self, datefield, dateinterval):
        if datefield is None or dateinterval is None:
            return None
        
        (fromdate, todate) = dateinterval
        
        date_dict = dict()
        date_dict[datefield] = {"$gte": fromdate, "$lt": todate}
        
        return date_dict
        

    # Parameters:
    # - collection - string with the collection we should query
    # - keys - list with one or more keys that are used to find the distinct combination of those keys
    # 
    # This function should return a list of tuples in which each tuple is of the form:
    # (combination_dictionary, count)
    # 
    # For each key the combination dictionary should have a key/value pair corresponding to that combination
    def get_distinct(self, keys, datefield=None, dateinterval=None, refine=None):
        aggregation = {"$group": {"_id": {}, "count": {"$sum": 1}}}

        for key in keys:
            aggregation["$group"]["_id"][key] = "$%s" % key

        results = list()

        if refine or datefield:
            refine_filter = self._transform_filter(refine)
            date_filter = self._transform_date_filter(datefield, dateinterval)
            merged_filter = self._merge_filters(refine_filter, date_filter)
            final_filter = {"$match": merged_filter}

            results = self.collection.aggregate([final_filter, aggregation])
            results = results['result']
        else:
            results = self.collection.aggregate([aggregation])["result"]

        result_list = list()
        for result in results:
            result_list.append((result["_id"], result["count"]))

        return result_list
            

    # Parameters:
    # - collection - string with the collection in which the event should be stored
    # - event - dictionary with all the key/value pairs that constitute an event
    # 
    # This function should save the event in the database
    def save_event(self, event):
        self.collection.insert(event)

    # Parameters:
    # - collection - string with the collection we should query
    # - refine - dictionary in which each key/value pair corresponds to a key of the
    # event and the regex that should be applied to the value of that key
    # 
    # This function should return an iterable with the documents
    def get_events(self, fields=None, datefield=None, dateinterval=None, refine=None):
        transformed_fields = self._transform_fields(fields)
        if refine or datefield:
            refine_filter = self._transform_filter(refine)
            date_filter = self._transform_date_filter(datefield, dateinterval)
            merged_filter = self._merge_filters(refine_filter, date_filter)

            return self.collection.find(spec=merged_filter, fields=transformed_fields)
        else:
            return self.collection.find(fields=transformed_fields)

    # Parameters:
    # - collection - string with the collection we should query
    # - refine - dictionary in which each key/value pair corresponds to a key of the
    # event and the regex that should be applied to the value of that key
    # 
    # This function should return an iterable with the documents
    def get_events_from_combination(self, combination, fields=None, datefield=None, dateinterval=None, refine=None):
        transformed_fields = self._transform_fields(fields)
        transformed_combination = self._transform_combination(combination)
        transformed_filter = self._transform_filter(refine)
        transformed_date = self._transform_date_filter(datefield, dateinterval)
        combined_filter = self._merge_filters(transformed_combination, transformed_filter, transformed_date)

        return self.collection.find(spec=combined_filter, fields=transformed_fields)


