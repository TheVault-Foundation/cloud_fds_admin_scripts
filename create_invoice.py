from bson import json_util
from datetime import date, datetime, timedelta
from dateutil.relativedelta import *

import random

import traceback
    
from log import Log
from models import *

class CreateInvoice():
    def __init__(self):
        self.curTime = datetime.now


    @staticmethod
    def createTestData():
        # ApiUsageCount.objects.delete()
        for d in range(365):
            tmpDate = date(2019, 1, 1) + timedelta(days=d)

            count = ApiUsageCount(userId = ObjectId("5d915a5228d321d46e6e6ea3"), apiId = ObjectId("5d75c247daf67e862aabb905"), date=tmpDate, count=random.randint(0,50))
            count.save()

            count = ApiUsageCount(userId = ObjectId("5d8734236f0436f89ec7d222"), apiId = ObjectId("5d8e9d57494549c6381e539e"), date=tmpDate, count=random.randint(0,30))
            count.save()

            count = ApiUsageCount(userId = ObjectId("5d92c293e6163b19dce793ce"), apiId = ObjectId("5d8e9d57494549c6381e539e"), date=tmpDate, count=random.randint(0,30))
            count.save()

    
    def createUserInvoice(self, userId, month, amount):
        Log.debug("createUserInvoice()")
        Log.debug("user id:{0}, month:{1}, amount:{2}".format(userId, month, amount))

        try:
            UserInvoice.objects(userId=userId, month=month).update(set__userId=userId, set__month=month, set__invoiceAmount=amount, set__createdAt=self.curTime, upsert=True)
        except:
            Log.error(traceback.format_exc())


    def getUserList(self, billingType):
        try:
            billingTypeDoc = BillingType.objects.get(billingType = billingType)
            return User.objects(billingType = billingTypeDoc.id)
        except:
            Log.error(traceback.format_exc())
            return []

    
    def findPrice(self, billingType, invoiceDate):
        try:
            billingTypeDoc = BillingType.objects.get(billingType = billingType)
            priceDoc = Price.objects(billingType = billingTypeDoc.id, startDate__lte=invoiceDate).order_by('-startDate').first()
            return priceDoc.price
        except:
            Log.error(traceback.format_exc())
            return None


    def freeTrial(self, startDate, endDate):
        Log.debug("freeTrial() : {0} - {1}".format(startDate, endDate))

        userList = self.getUserList("Free trial")
        Log.info("{0} user(s) found".format(len(userList)))
        
        for user in userList:
            self.createUserInvoice(user.id, int(startDate.strftime("%Y%m")), 0.0)


    def monthly(self, startDate, endDate):
        Log.debug("monthly() : {0} - {1}".format(startDate, endDate))

        price =self.findPrice("Monthly", startDate)
        Log.info("price:" + str(price))
        
        userList = self.getUserList("Monthly")
        Log.info("{0} user(s) found".format(len(userList)))
        
        for user in userList:
            self.createUserInvoice(user.id, int(startDate.strftime("%Y%m")), price)
        

    def metered(self, startDate, endDate):
        Log.debug("metered() : {0} - {1}".format(startDate, endDate))

        price =self.findPrice("Metered", startDate)
        Log.info("price:" + str(price))

        userList = self.getUserList("Metered")
        Log.info("{0} user(s) found".format(len(userList)))        
        
        for user in userList:
            count = ApiUsageCount.objects(userId = user.id, date__gte = startDate, date__lte = endDate).sum("count")
            Log.info("user:{0}, count:{1}".format(user.id, count))
            self.createUserInvoice(user.id, int(startDate.strftime("%Y%m")), price * count)

        
    def createLastMonth(self):
        Log.debug("createLastMonth()")

        first_day_of_current_month = date.today().replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

        self.freeTrial(first_day_of_previous_month, last_day_of_previous_month)
        self.monthly(first_day_of_previous_month, last_day_of_previous_month)
        self.metered(first_day_of_previous_month, last_day_of_previous_month)



if __name__ == '__main__':
    Log.info("create_invoice.py")

    # CreateInvoice.createTestData()

    invoice = CreateInvoice()
    invoice.createLastMonth()

    # for m in range(1, 12):
    #     first_day_of_month = date(2019, m, 1)
    #     next_month = first_day_of_month + relativedelta(months=+1)
    #     last_day_of_month = next_month - timedelta(days=1)

    #     invoice.freeTrial(first_day_of_month, last_day_of_month)
    #     invoice.monthly(first_day_of_month, last_day_of_month)
    #     invoice.metered(first_day_of_month, last_day_of_month)