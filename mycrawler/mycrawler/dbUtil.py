# encoding=utf-8
import pymongo
import settings
import commands


class DbUtil(object):

    def conn(self):
        self.client = pymongo.MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DATABASE]
        return self

    def collection(self, colName=None):
        if not colName:
            return self.db[settings.MONGO_COLLECTION]
        elif isinstance(colName, str):
            return self.db[colName]
        else:
            print "集合名字必须是字符串"
            return

    def close(self):
        self.client.close()


def url_items(name):
    db = DbUtil().conn()
    cols = db.collection('url_items').find({'name': name})
    return [str(c.get('start_urls')) for c in cols]


def all_firm():
    col = DbUtil().conn().collection('scrapy_items')
    return (col.find({"Status": {"$gte": 0}}).count(), col.find({"Status": 0}).count())


def download_process():
    all_spiders = commands.getoutput("scrapy list").split('\n')
    col = DbUtil().conn().collection('scrapy_items')
    for spider_name in all_spiders:
        yield [spider_name, col.find({'Firm': spider_name.capitalize(), "Status": {"$gte": 0}}).count(), col.find({'Firm': spider_name.capitalize(), "Status": 0}).count()]
if __name__ == '__main__':
    pass
