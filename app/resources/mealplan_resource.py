# resource.py
from typing import Any, List
from framework.resources.base_resource import BaseResource
from datetime import datetime

from app.models.mealplan_model import Mealplan, DailyMealplan, WeeklyMealplan
from app.services.service_factory import ServiceFactory


class MealplanResource(BaseResource):

    def __init__(self, config):
        super().__init__(config)

        self.data_service = ServiceFactory.get_service("MealplanResourceDataService")
        self.database = "mealplan_db"
        self.meal_plans = "meal_plans"
        self.daily_meal_plans = "daily_meal_plans"
        self.weekly_meal_plans = "weekly_meal_plans"
        self.meal_plans_pk = "meal_id"
        self.weekly_pk = "week_plan_id"
        self.daily_pk = "day_plan_id"

    
    def create_by_key(self, data: dict) -> Mealplan:
        d_service = self.data_service
        d_service.insert_data(
            self.database, self.meal_plans, data
        )
        return Mealplan(**data)

    def get_by_key(self, key: Any, collection: str):
        d_service = self.data_service
        try:
            key = int(key)
        except:
            key = str(key) #RETURN AN ERROR CODE FOR INCORRECT KEY TYPE
        if collection == "meal_plans":
            result = d_service.get_data_object(
                self.database, self.meal_plans, key_field=self.meal_plans_pk, key_value=key
            )
            return Mealplan(**result)
        elif collection == "weekly_meal_plans":
            result = d_service.get_data_object(
                self.database, self.weekly_meal_plans, key_field=self.weekly_pk, key_value=key
            )
            return WeeklyMealplan(**result)
        elif collection == "daily_meal_plans":
            result = d_service.get_data_object(
                self.database, self.daily_meal_plans, key_field=self.daily_pk, key_value=key
            )
            return DailyMealplan(**result)

    def update_by_key(self, key: str, data: dict) -> Mealplan:
        d_service = self.data_service
        d_service.update_data(
            self.database, self.meal_plans, data, key_field=self.key_field, key_value=key
        )
        return self.get_by_key(key)

    def delete_by_key(self, key: str) -> None:
        d_service = self.data_service
        d_service.delete_data(
            self.database, self.meal_plans, key_field=self.key_field, key_value=key
        )
    # Get the total count of meal plans in the meal_plans table
    def get_total_count(self) -> int:
        return self.data_service.get_total_count(self.database, self.meal_plans)

    # Create a new meal plan entry
    def create_meal_plan(self, mealplan: Mealplan) -> Mealplan:
        mealplan_data = mealplan.dict(exclude_unset=True)
        # Remove links
        mealplan_data.pop('links', None)
        mealplan_data['meal_id'] = self.data_service.get_total_count(self.database, self.meal_plans) + 1
        # Call insert_data with the meal plan data
        result = self.data_service.insert_data(self.database, self.meal_plans, mealplan_data)
        return Mealplan(**result)
    
    # Create a new weekly meal plan entry
    def create_weekly_meal_plan(self, weekly_mealplan: WeeklyMealplan) -> WeeklyMealplan:
        weekly_mealplan_data = weekly_mealplan.dict(exclude_unset=True)
        # Remove any links 
        weekly_mealplan_data.pop('links', None)
        weekly_mealplan_data['week_plan_id'] = self.data_service.get_total_count(self.database, self.weekly_meal_plans) + 1
        # Call insert_data with the meal plan data
        result = self.data_service.insert_data(self.database, self.weekly_meal_plans, weekly_mealplan_data)
        return WeeklyMealplan(**result)
    
    # Create a new daily meal plan entry
    def create_daily_meal_plan(self, daily_mealplan: DailyMealplan) -> DailyMealplan:
        daily_mealplan_data = daily_mealplan.dict(exclude_unset=True)
        # Remove any links before insert
        daily_mealplan_data.pop('links', None)
        daily_mealplan_data['day_plan_id'] = self.data_service.get_total_count(self.database, self.daily_meal_plans) + 1
        # Call insert_data with the meal plan data
        result = self.data_service.insert_data(self.database, self.daily_meal_plans, daily_mealplan_data)
        return DailyMealplan(**result)

    # Retrieve a specific weekly meal plan by its week_plan_id
    def get_weekly_meal_plan(self, week_plan_id: Any) -> WeeklyMealplan:
        result = self.data_service.get_data_object(
            self.database, self.weekly_meal_plans, key_field="week_plan_id", key_value=week_plan_id
        )
        return WeeklyMealplan(**result) if result else None

    # Retrieve daily meal plans within a specific week
    def get_daily_meal_plans_by_week(self, week_plan_id: Any) -> List[DailyMealplan]:
        results = self.data_service.get_all_data(
            self.database, self.daily_meal_plans, filters={"week_plan_id": week_plan_id}
        )
        for idx, result in enumerate(results):
            results[idx] = {
                "day_plan_id": result["day_plan_id"],
                "week_plan_id": result["week_plan_id"],
                "date": result["date"].strftime("%Y-%m-%d"),
                "meal_id": result["meal_id"]
            }
        return [DailyMealplan(**item) for item in results]
    
    # Retrieve meal plans from a specific date
    def get_daily_meal_plans_by_date(self, date: str) -> List[DailyMealplan]:
        results = self.data_service.get_daily_meal_plans_by_week(date)
        for idx, result in enumerate(results):
            results[idx] = {
                "day_plan_id": result["day_plan_id"],
                "week_plan_id": result["week_plan_id"],
                "date": result["date"].strftime("%Y-%m-%d"),
                "meal_id": result["meal_id"]
            }
        return [DailyMealplan(**item) for item in results]

    # Update a meal plan based on its meal_id
    def update_meal_plan(self, meal_id: Any, data: dict) -> Mealplan:
        self.data_service.update_data(
            self.database, self.meal_plans, data, key_field="meal_id", key_value=meal_id
        )
        return self.get_by_key(meal_id, self.meal_plans)
    
    # Update a daily meal plan based on its meal_id
    def update_daily_meal_plan(self, day_plan_id: int, data: dict) -> DailyMealplan:
        self.data_service.update_data(
            self.database, self.daily_meal_plans, data, key_field="day_plan_id", key_value=day_plan_id
        )
        return self.get_by_key(day_plan_id, self.daily_meal_plans)
    
    # Update a weekly meal plan based on its meal_id
    def update_weekly_meal_plan(self, week_plan_id: int, data: dict) -> WeeklyMealplan:
        self.data_service.update_data(
            self.database, self.weekly_meal_plans, data, key_field="week_plan_id", key_value=week_plan_id
        )
        return self.get_by_key(week_plan_id, self.weekly_meal_plans)

    # Delete a specific meal plan
    def delete_meal_plan(self, meal_id: int) -> None:
        self.data_service.delete_data(
            self.database, self.meal_plans, key_field="meal_id", key_value=meal_id
        )
    
    # Delete a specific meal plan
    def delete_daily_meal_plan(self, day_plan_id: int) -> None:
        self.data_service.delete_data(
            self.database, self.daily_meal_plans, key_field="day_plan_id", key_value=day_plan_id
        )

    # Delete a specific meal plan
    def delete_weekly_meal_plan(self, week_plan_id: int) -> None:
        self.data_service.delete_data(
            self.database, self.weekly_meal_plans, key_field="week_plan_id", key_value=week_plan_id
        )

    # Retrieve all meal plans with pagination
    def get_all_meal_plans(self, skip: int = 0, limit: int = 10) -> List[Mealplan]:

        results = self.data_service.get_all_data(
            database_name=self.database, 
            collection_name=self.meal_plans, 
            skip=skip, 
            limit=limit
        )
        
        return [Mealplan(**item) for item in results]
    
    def get_all_weekly_meal_plans(self, skip: int = 0, limit: int = 10) -> List[WeeklyMealplan]:
 
        results = self.data_service.get_all_data(
            database_name=self.database, 
            collection_name=self.weekly_meal_plans, 
            skip=skip, 
            limit=limit
        )
        print(type(results[0]['end_date']))
        for idx, result in enumerate(results):
            results[idx] = {
                "week_plan_id": result["week_plan_id"],
                "start_date": result["start_date"].strftime("%Y-%m-%d"),
                "end_date": result["end_date"].strftime("%Y-%m-%d")
            }
        return [WeeklyMealplan(**item) for item in results]
    
    def get_all_daily_meal_plans(self, skip: int = 0, limit: int = 10) -> List[DailyMealplan]:
 
        results = self.data_service.get_all_data(
            database_name=self.database, 
            collection_name=self.daily_meal_plans, 
            skip=skip, 
            limit=limit
        )
        for idx, result in enumerate(results):
            results[idx] = {
                "day_plan_id": result["day_plan_id"],
                "week_plan_id": result["week_plan_id"],
                "date": result["date"].strftime("%Y-%m-%d"),
                "meal_id": result["meal_id"]
            }
        return [DailyMealplan(**item) for item in results]
        

