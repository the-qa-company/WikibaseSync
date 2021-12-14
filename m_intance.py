import numpy as np

import others_config as cf
from collections import OrderedDict, defaultdict

from utilities import io_worker as iw
from utilities.sparql_queries import SparqlEndPoint
from tqdm import tqdm
from utilities.util import WikibaseImporter
import pandas as pd


def get_wikicom_init_items(refresh=False):
    # Use temp file
    if not refresh:
        try:
            init_list = iw.load_object_csv(cf.DIR_INIT_ITEMS)
            if init_list:
                init_list = [i[0] for i in init_list]
                return init_list
        except FileNotFoundError:
            pass
        except Exception as message:
            iw.print_status(message)
            pass

    # Refresh
    # Wikidata SPARQL endpoint
    sparql_wd = SparqlEndPoint(endpoint_config=cf.WD_QUERY)

    init_list = cf.WC_INIT_ITEMS

    def run_queries(type_obj, **kwargs):
        status, responds = sparql_wd.run(**kwargs)
        iw.print_status(f"{type_obj}: {len(responds)}")
        if status == cf.StatusSPARQL.Success:
            init_list.extend(sorted([l[0] for l in responds], key=lambda x: int(x[1:])))

    run_queries("Properties", **cf.SPARQL_JAPAN_COMPANIES_PROPS)
    run_queries("Types", **cf.SPARQL_JAPAN_COMPANIES_TYPES)
    run_queries("Item", **cf.SPARQL_JAPAN_COMPANIES_ITEMS)

    init_list = list(OrderedDict.fromkeys(init_list))
    iw.save_object_csv(cf.DIR_INIT_ITEMS, init_list)
    return init_list


def import_init_list():
    import m_f
    import pywikibot

    m_f.init()
    # Wikibase
    wikibase_site = pywikibot.Site("my", "my")
    # Wikidata
    wikidata_site = pywikibot.Site("wikidata", "wikidata")

    importer = WikibaseImporter(wikibase_site, wikidata_site)

    def import_wikidata_items(list_items, from_i=0, import_claims=True):
        for i, wikidata_id in enumerate(
            tqdm(list_items[from_i:], total=len(list_items), initial=from_i)
        ):
            importer.change_item(
                importer.wikidata_repo,
                importer.wikibase_repo,
                wikidata_id,
                statements=import_claims,
            )

    # import_wikidata_items(cf.WC_INIT_ITEMS, import_claims=False)
    # --> Edit P1 P2
    full_list = get_wikicom_init_items()
    import_wikidata_items(full_list[:3125], import_claims=False)
    import_wikidata_items(full_list, from_i=0, import_claims=True)
    # 158: 27610


def get_mapper_japanese_company_id(refresh=False, get_detail_info=False):
    # Use temp file
    run_wd_query = True
    query_responds = []
    if not refresh:
        try:
            query_responds = iw.load_object_csv(cf.DIR_MAP_WD_COM_ID)
            run_wd_query = False
        except FileNotFoundError:
            pass
        except Exception as message:
            iw.print_status(message)
            pass
    if run_wd_query:
        # Wikidata company id
        kwargs_query = {
            "query": "SELECT DISTINCT ?i ?iLabel ?t ?tLabel ?id {"
            "?i wdt:P3225 ?id; wdt:P31 ?t."
            'SERVICE wikibase:label { bd:serviceParam wikibase:language "en".}'
            "}",
            "params": ["i", "iLabel", "t", "tLabel", "id"],
        }
        wd_query = SparqlEndPoint()
        status, query_responds = wd_query.run(**kwargs_query)
        if status != cf.StatusSPARQL.Success:
            raise Exception(status)
        print("Query: " + kwargs_query["query"])
        print(f"Responds: {len(query_responds)} records")
        iw.save_object_csv(cf.DIR_MAP_WD_COM_ID, query_responds)

    com_id = defaultdict(set)
    type_wd = defaultdict(set)
    count_type = 0
    items = {}
    for i, il, t, tl, id in query_responds:
        com_id[id].add(i)
        if get_detail_info:
            items[i] = il
            count_type += 1
            type_wd[f"{t}\t{tl}"].add(id)

    count_dup = 0
    mapper = {}
    print_dup = []
    for k, v in com_id.items():
        # Get the first edit item
        mapper[k] = sorted(list(v), key=lambda x: x[1:])[0]
        if get_detail_info and len(v) > 1:
            count_dup += len(v)
            print_dup.append([k, v])
    print(f"Mapper final: {len(mapper)}")

    if get_detail_info:
        iw.print_status(
            f"\tDuplicate: {count_dup}/{len(items)} - {count_dup / len(items) * 100:.2f}%"
        )
        for i, (k, v) in enumerate(print_dup):
            iw.print_status(
                f"{i+1}\t"
                f"{k}\t"
                f"{len(v)}\t" + " ".join([f"{i}[{items.get(i)}]" for i in v])
            )

        type_wd = sorted(type_wd.items(), key=lambda x: len(x[1]), reverse=True)
        iw.print_status(
            f"\tTypes: {len(type_wd)} - Types/item: {count_type / len(items):.2f}"
        )
        for i, (k, v) in enumerate(type_wd):
            iw.print_status(f"{i+1}\t{k}\t{len(v)}\t{len(v)/len(items)*100:.2f}%")

    return mapper


def read_zenkoku_all(release="20211130"):
    def read_dataframe(refresh=False):
        if not refresh:
            try:
                return pd.read_pickle(cf.DIR_DF_COM)
            except FileNotFoundError:
                pass
            except Exception as e:
                pass
        # parse XML
        # /Users/phucnguyen/git/WikibaseSync/data/06_yamagata_all_20211130/06_yamagata_all_20211130.xml
        # tmp_df = pd.read_xml(
        #     f"/Users/phucnguyen/git/WikibaseSync/data/06_yamagata_all_20211130/06_yamagata_all_20211130.xml",
        #     parser="etree",
        # )
        # print(tmp_df.columns)
        # columns = tmp_df.columns
        dtypes_int = [0, 3, 23, 29]
        dtypes = {col: int if i in dtypes_int else str for i, col in enumerate(columns)}

        parse_dates = ["updateDate", "changeDate", "closeDate", "assignmentDate"]

        tmp_df = pd.read_csv(
            f"{cf.DIR_ROOT}/data/00_zenkoku_all_{release}/00_zenkoku_all_{release}.csv",
            header=None,
            names=columns,
            low_memory=False,
            dtype=dtypes,
            parse_dates=parse_dates,
        )
        tmp_df.to_pickle(cf.DIR_DF_COM)
        print(tmp_df.info(show_counts=True))
        for c in columns:
            print(f"\n{c}: ")
            print(tmp_df[c][tmp_df[c].notnull()])
        return tmp_df

    columns = [
        "sequenceNumber",
        "corporateNumber",
        "process",
        "correct",
        "updateDate",
        "changeDate",
        "name",
        "nameImageId",
        "kind",
        "prefectureName",
        "cityName",
        "streetNumber",
        "addressImageId",
        "prefectureCode",
        "cityCode",
        "postCode",
        "addressOutside",
        "addressOutsideImageId",
        "closeDate",
        "closeCause",
        "successorCorporateNumber",
        "changeCause",
        "assignmentDate",
        "latest",
        "enName",
        "enPrefectureName",
        "enCityName",
        "enAddressOutside",
        "furigana",
        "hihyoji",
    ]

    houjin = read_dataframe(refresh=True)

    mapper_com_wd = get_mapper_japanese_company_id()
    res_map = houjin.loc[houjin["corporateNumber"].isin({k for k in mapper_com_wd})]

    print(res_map.info(show_counts=True))
    res_map.to_pickle(cf.DIR_DF_COM + ".mapped")
    for c in columns:
        print(f"\n{c}: ")
        print(res_map[c][res_map[c].notnull()])


if __name__ == "__main__":
    # Get wikicom init list: wikibase instance of Japanese companies
    # wc_init_items = get_wikicom_init_items(refresh=True)
    # iw.print_status(f"Total: {len(wc_init_items)}")

    # Import the init list
    import_init_list()
    # read_zenkoku_all(release="20211130")
