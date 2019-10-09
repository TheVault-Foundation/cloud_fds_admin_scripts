from bson import json_util
from datetime import date, datetime

import traceback
    
from log import Log
from models import *

class UpdateUserBillingType():
    @staticmethod
    def createTestData():
        change = UserChangeBillingType(userId = ObjectId("5d915a5228d321d46e6e6ea3"), billingType = ObjectId("5d75c242daf67e862aabb8ff"), startDate=date(2019, 1, 1), createdAt=datetime.now, createdBy="Admin")
        change.save()

        change = UserChangeBillingType(userId = ObjectId("5d92c293e6163b19dce793ce"), billingType = ObjectId("5d9837eb2d207c3854ae400a"), startDate=date(2019, 1, 1), createdAt=datetime.now, createdBy="Admin")
        change.save()

    
    def updateOne(self, doc):
        Log.debug("updateOne()")
        Log.debug("user id:{0}, billing type id:{1}".format(doc.userId, doc.billingType))

        try:
            User.objects(id=ObjectId(doc.userId)).update(billingType=doc.billingType)

            doc.isUpdated = True
            doc.updatedAt = datetime.now
            doc.save()
        except:
            Log.error(traceback.format_exc())


    def processAll(self):
        Log.debug("processAll()")

        docArray = UserChangeBillingType.objects(startDate__lte = date.today(), isUpdated__ne = True)
        Log.info("{0} record(s) found".format(len(docArray)))
        for doc in docArray:
            self.updateOne(doc)


if __name__ == '__main__':
    Log.info("update_user_billing_type.py")

    # UpdateUserBillingType.createTestData()

    update = UpdateUserBillingType()
    update.processAll()