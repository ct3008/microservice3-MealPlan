from framework.services.service_factory import BaseServiceFactory
import app.resources.mealplan_resource as mealplan_resource
from framework.services.data_access.MySQLRDBDataService import MySQLRDBDataService


# TODO -- Implement this class
class ServiceFactory(BaseServiceFactory):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_service(cls, service_name):
        #
        # TODO -- The terrible, hardcoding and hacking continues.
        #
        if service_name == 'MealplanResource':
            result = mealplan_resource.MealplanResource(config=None)
        elif service_name == 'MealplanResourceDataService':
            context = dict(user="root", password="dbuserdbuser",
                           host="35.196.59.220", port=3306)
            data_service = MySQLRDBDataService(context=context)
            result = data_service
        else:
            result = None

        return result




