from flask_restful import reqparse
from flask_restful import Resource
from elasticsearch import Elasticsearch
from flask_reqparse import RequestParser

parser = reqparse.RequestParser()
parser.add_argument('tel',location = 'args')

response = {"code":200,"msg":"success"}

class data (Resource):
    def get(self):

        #取得url中的變數
        parser = reqparse.RequestParser()
        parser.add_argument('tel') #電話號碼(ex:0975-009-299)
        parser.add_argument('sex') #性別要求(ex:men or women)
        parser.add_argument('loc') #地址(ex:tpc or ntpc)
        parser.add_argument('iden') #屋主身分(ex: owner or agency)
        parser.add_argument('sex_owner') #屋主性別(ex:men or women)
        parser.add_argument('surname') #屋主姓氏(ex: wu)
        args = parser.parse_args()
        #參數轉換
        if args['loc'] != None:
            loc = {'tpc':"台北市",'ntpc':"新北市"}
            es_loc = loc[args['loc']]
        else:
            es_loc = ''
        if args['sex'] != None:
            sex = {'men':'男','women':'女'}
            es_sex = sex[args['sex']]
        else:
            es_sex = ''
        if args['iden'] != None:
            iden = {'owner':'屋主','agency':'仲介'}
            es_iden = iden[args['iden']]
        else:
            es_iden = ''
        if args['sex_owner'] != None:
            sex_owner = {'men':['先生'],'women':["太太","媽媽","小姐","阿姨"]}
            es_sex_owner = sex_owner[args['sex_owner']]
        else:
            es_sex_owner = ''
        if args['tel'] != None:
            es_tel = args['tel']
        else:
            es_tel = ''
        if args['surname'] != None:
            surname = {'wu':'吳','chou':'周'}
            es_surname = surname[args['surname']]
        else:
            es_surname = ''
        res_args = {'地址':es_loc,"性別要求":es_sex,"屋主身分":es_iden,"屋主性別":es_sex_owner,"電話":es_tel,"屋主姓氏":es_surname}
        response['args'] = res_args
        es_sex_owner_list = []
        es_surname_list = ['先生',"太太","媽媽","小姐","阿姨"]
        #可以解決有姓氏跟身分問題
        if es_sex_owner != '' and es_surname != "":
            for i in es_sex_owner:
                es_sex_owner_list.append(es_surname + i)
            query_json = {
        "query": {
            "bool": {
            "must": [
                {"wildcard": {
                "性別要求": es_sex +"*"
                }},
                {"wildcard":{
                    "地址":es_loc+"*"
                }},
                {"wildcard": {
                    "電話": es_tel + "*"
                }},
                {"wildcard": {
                    "屋主身分": es_iden + "*"
                }},
                {"terms": {
                    "屋主名稱": es_sex_owner_list
                }},
            ]
            }
        }
        }
        elif es_sex_owner == '' and es_surname != "":
            for i in es_surname_list:
                es_sex_owner_list.append(es_surname + i)
            query_json = {
                "query": {
                    "bool": {
                        "must": [
                            {"wildcard": {
                                "性別要求": es_sex + "*"
                            }},
                            {"wildcard": {
                                "地址": es_loc + "*"
                            }},
                            {"wildcard": {
                                "電話": es_tel + "*"
                            }},
                            {"wildcard": {
                                "屋主身分": es_iden + "*"
                            }},
                            {"terms": {
                                "屋主名稱": es_sex_owner_list
                            }},
                        ]
                    }
                }
            }
        elif args['sex_owner'] == 'men' and es_surname == "":
            query_json = {
                "query": {
                    "bool": {
                        "must": [
                            {"wildcard": {
                                "性別要求": es_sex + "*"
                            }},
                            {"wildcard": {
                                "地址": es_loc + "*"
                            }},
                            {"wildcard": {
                                "電話": es_tel + "*"
                            }},
                            {"wildcard": {
                                "屋主身分": es_iden + "*"
                            }},
                            {"wildcard": {
                                "屋主名稱": "*" +es_sex_owner[0]
                            }},
                        ]
                    }
                }
            }
        elif args['sex_owner'] == 'women' and es_surname == "":
            query_json = {
                "query": {
                    "bool": {
                        "should": [
                            {"bool": {"must": [{"wildcard": {"屋主名稱": "*小姐"}}, {"wildcard": {"地址": es_loc + "*"}},{"wildcard": {"性別要求": es_sex + "*"}},{"wildcard": {"電話": es_tel + "*"}},{"wildcard": {"屋主身分": es_iden + "*"}},]}},
                            {"bool": {"must": [{"wildcard": {"屋主名稱": "*太太"}}, {"wildcard": {"地址": es_loc + "*"}},{"wildcard": {"性別要求": es_sex + "*"}},{"wildcard": {"電話": es_tel + "*"}},{"wildcard": {"屋主身分": es_iden + "*"}},]}},
                            {"bool": {"must": [{"wildcard": {"屋主名稱": "*媽媽"}}, {"wildcard": {"地址": es_loc + "*"}},{"wildcard": {"性別要求": es_sex + "*"}},{"wildcard": {"電話": es_tel + "*"}},{"wildcard": {"屋主身分": es_iden + "*"}},]}},
                            {"bool": {"must": [{"wildcard": {"屋主名稱": "*阿姨"}}, {"wildcard": {"地址": es_loc + "*"}},{"wildcard": {"性別要求": es_sex + "*"}},{"wildcard": {"電話": es_tel + "*"}},{"wildcard": {"屋主身分": es_iden + "*"}},]}},
                        ],
                    }
                }
            }
        else:
            query_json = {
                "query": {
                    "bool": {
                        "must": [
                            {"wildcard": {
                                "性別要求": es_sex + "*"
                            }},
                            {"wildcard": {
                                "地址": es_loc + "*"
                            }},
                            {"wildcard": {
                                "電話": es_tel + "*"
                            }},
                            {"wildcard": {
                                "屋主身分": es_iden + "*"
                            }},
                        ]
                    }
                }
            }

        #建立elastic連線
        es = Elasticsearch()
        query = es.search(index='house_chou',body=query_json,scroll='5m',size = 100)
        results = query['hits']['hits'] # es查询出的结果第一页
        total = query['hits']['total']['value']  # es查询出的结果总量
        scroll_id = query['_scroll_id'] # 游标用于输出es查询出的所有结果
        for i in range(0, int(total/100)+1):
            # scroll参数必须指定否则会报错
            query_scroll = es.scroll(scroll_id=scroll_id,scroll='5m')['hits']['hits']
            results += query_scroll
        response['len'] = len(results)
        response['query'] = query_json
        response['data'] = results

        return response