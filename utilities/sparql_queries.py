from time import sleep

from SPARQLWrapper import SPARQLWrapper, JSON
import others_config as cf
import logging

from utilities import io_worker as iw


class SparqlEndPoint:
    def __init__(self, endpoint_config=cf.WD_QUERY):
        # Config validation
        if (
            not endpoint_config.get("url")
            or not endpoint_config.get("prefix_ent")
            or not endpoint_config.get("prefix_pro")
        ):
            raise KeyError

        self.url = endpoint_config.get("url")
        self.prefix_ent = endpoint_config.get("prefix_ent")
        self.prefix_pro = endpoint_config.get("prefix_pro")
        self.sparql = SPARQLWrapper(self.url)
        self.sparql.setTimeout(100000)
        self.sparql.setReturnFormat(JSON)

    def remove_prefix(self, item):
        remove_list = [self.prefix_ent, self.prefix_pro]
        for remove_substring in remove_list:
            item = item.replace(remove_substring, "")
        return item

    def run(self, query, params, limit=50000, retries=1, offset=0, remove_prefix=True):
        responds = []
        has_next = True
        logging.debug(query)
        max_limit = limit
        status = cf.StatusSPARQL.Success

        while has_next:
            try:
                q = f"{query}\nLIMIT {limit}\nOFFSET {offset}"
                self.sparql.setQuery(q)
                self.sparql.setMethod("POST")
                result_query = self.sparql.query().convert()
                results = result_query["results"]["bindings"]

                for result in results:
                    responds.append(
                        [
                            self.remove_prefix(result[p]["value"])
                            if remove_prefix
                            else result[p]["value"]
                            for p in params
                        ]
                    )

                offset += limit
                if len(responds) < offset:
                    iw.print_status(f"Received Data: {len(responds)}", is_screen=False)
                    has_next = False
                elif len(responds) % limit == 0:
                    iw.print_status(f"Received Data: {len(responds)}", is_screen=False)

                if limit * 2 > max_limit:
                    limit = max_limit
                else:
                    limit = limit * 2

            except Exception as e:
                if "HTTP Error 429: Too Many Requests" in str(e):
                    sleep(60)
                    iw.print_status("HTTP Error 429: Too Many Requests: wait 100")
                    if retries > 0:
                        return self.run(query, params, limit, retries - 1)
                    else:
                        return cf.StatusSPARQL.TooManyRequests, responds
                else:
                    has_next = False
                    iw.print_status("Connection error: %s" % str(e)[:100])
                    iw.print_status(query, is_screen=False)
                    status = cf.StatusSPARQL.ConnectionError

        return status, responds
