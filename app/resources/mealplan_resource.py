# resource.py
from typing import Any, List
from framework.resources.base_resource import BaseResource
from datetime import datetime
from datetime import date
from typing import List, Dict, Any
from pydantic import BaseModel
from fastapi import HTTPException

from app.models.mealplan_model import Mealplan, DailyMealplan, WeeklyMealplan
from app.services.service_factory import ServiceFactory


def transform_to_daily_mealplans(input_data: Dict) -> List[Dict[str, Any]]:
    weekly_meal_plans = input_data["weekly_meal_plan"]
    meals = input_data["meals"]
    
    daily_mealplans = []
    day_plan_id = 1  # Starting day_plan_id
    
    for week_plan in weekly_meal_plans:
        week_plan_id = week_plan["week_plan_id"]
        for meal in meals:
            # Create a daily meal plan object
            daily_mealplan = {
                "day_plan_id": day_plan_id,
                "week_plan_id": week_plan_id,
                "date": meal["date"].isoformat(),
                "meal_id": day_plan_id,  # Assuming meal_id is same as day_plan_id for this case
                "links": {
                    "self": f"/daily-mealplans/{day_plan_id}",
                    "week": f"/weekly-mealplans/{week_plan_id}",
                    "mealplan": f"/mealplans/{day_plan_id}",
                    "edit": f"/daily-mealplans/{day_plan_id}/edit",
                    "delete": f"/daily-mealplans/{day_plan_id}/delete"
                }
            }
            daily_mealplans.append(daily_mealplan)
            day_plan_id += 1  # Increment the day_plan_id for each new meal

    return daily_mealplans

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
        
    async def get_by_key_async(self, key: Any, collection: str):
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
        print(self.data_service.get_total_count(self.database, self.meal_plans))
        # mealplan_data['meal_id'] = self.data_service.get_total_count(self.database, self.meal_plans) + 2
        mealplan_data['meal_id'] = self.data_service.get_max_value("meal_id", self.database, self.meal_plans) + 1
        print("DAY PLAN ID: ", mealplan_data['meal_id'])
        # Call insert_data with the meal plan data
        result = self.data_service.insert_data(self.database, self.meal_plans, mealplan_data)
        return Mealplan(**result)
    
    # Create a new weekly meal plan entry
    def create_weekly_meal_plan(self, weekly_mealplan: WeeklyMealplan) -> WeeklyMealplan:
        weekly_mealplan_data = weekly_mealplan.dict(exclude_unset=True)
        # Remove any links 
        weekly_mealplan_data.pop('links', None)
        # weekly_mealplan_data['week_plan_id'] = self.data_service.get_total_count(self.database, self.weekly_meal_plans) + 1
        weekly_mealplan_data['week_plan_id'] = self.data_service.get_max_value("week_plan_id", self.database, self.weekly_meal_plans) + 1
        print("WEEK PLAN ID: ", weekly_mealplan_data['week_plan_id'])
        # Call insert_data with the meal plan data
        result = self.data_service.insert_data(self.database, self.weekly_meal_plans, weekly_mealplan_data)
        return WeeklyMealplan(**result)

    def create_daily_meal_plan(self, daily_mealplan: DailyMealplan) -> DailyMealplan:
        daily_mealplan_data = daily_mealplan.dict(exclude_unset=True)
        daily_mealplan_data.pop('links', None)

        # Extract the date
        date = daily_mealplan_data['date']

        try:
            # Check if a weekly plan exists for the date
            query = """
            SELECT week_plan_id FROM mealplan_db.weekly_meal_plans
            WHERE %s BETWEEN start_date AND end_date
            """
            params = (date,)
            print(f"Checking for existing weekly plan with query: {query}, params: {params}")  # Debugging
            existing_week_plan = self.data_service.execute_query(query, params)

            if existing_week_plan:
                # Use the existing week_plan_id
                daily_mealplan_data['week_plan_id'] = existing_week_plan[0]['week_plan_id']
            else:
                # Create a new weekly plan
                new_week_plan_id = self.data_service.get_max_value(
                    "week_plan_id", self.database, "weekly_meal_plans"
                ) + 1

                # Calculate the start_date and end_date for the new weekly plan
                start_date = date  # Assuming the week starts on the provided date
                end_date_query = """
                SELECT DATE_ADD(%s, INTERVAL 6 DAY) AS end_date
                """
                end_date_result = self.data_service.execute_query(end_date_query, (start_date,))
                end_date = end_date_result[0]['end_date']

                # Insert the new weekly plan
                insert_query = """
                INSERT INTO mealplan_db.weekly_meal_plans (week_plan_id, start_date, end_date)
                VALUES (%s, %s, %s)
                """
                print(
                    f"Creating new weekly plan with query: {insert_query}, params: ({new_week_plan_id}, {start_date}, {end_date})")  # Debugging
                self.data_service.execute_query(insert_query, (new_week_plan_id, start_date, end_date))

                # Use the newly created week_plan_id
                daily_mealplan_data['week_plan_id'] = new_week_plan_id

            # Generate a new day_plan_id
            daily_mealplan_data['day_plan_id'] = self.data_service.get_max_value(
                "day_plan_id", self.database, "daily_meal_plans"
            ) + 1

            # Insert the daily meal plan
            result = self.data_service.insert_data(
                self.database, "daily_meal_plans", daily_mealplan_data
            )
            return DailyMealplan(**result)
        except Exception as e:
            print(f"Error in create_daily_meal_plan: {e}")  # Debugging
            raise HTTPException(status_code=500, detail="Failed to create daily meal plan.")

    def _get_year_and_week(self, date: str) -> tuple:
        """
        Helper function to extract the year and week number from a date.

        :param date: The date string in YYYY-MM-DD format.
        :return: A tuple containing the year and week number.
        """
        from datetime import datetime
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        return date_obj.isocalendar()[0], date_obj.isocalendar()[1]

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
    def get_daily_meal_plans_by_date(self, date: str) -> List[DailyMealplan]:
        results = self.data_service.get_daily_meal_plans_by_date(date)
        print("results: ", results)

        return results
    # Retrieve meal plans from a specific date
    # def get_daily_meal_plans_by_date(self, date: str) -> List[DailyMealplan]:
    #     results = self.data_service.get_daily_meal_plans_by_date(date)
    #     print("RESULTS BISH: ", results)
        
    #     # Prepare results with the correct format
    #     daily_meals = []
    #     for idx, (weekly, meal) in enumerate(zip(results['weekly_meal_plan'], results['meals'])):
    #         # Construct the result dictionary
    #         result = {
    #             "end_date": weekly["end_date"].strftime("%Y-%m-%d"),
    #             "start_date": weekly["start_date"].strftime("%Y-%m-%d"),
    #             "day_plan_id": idx,  # You can generate a unique day_plan_id if needed
    #             "week_plan_id": weekly["week_plan_id"],
    #             "date": meal["date"].strftime("%Y-%m-%d"),  # Ensure date is a string
    #             "meal_id": meal["meal_id"],
    #             'breakfast_recipe': meal["breakfast_recipe"],
    #             'lunch_recipe': meal["lunch_recipe"],
    #             'dinner_recipe': meal["dinner_recipe"]
    #             # "start_date" and "end_date" are not part of the DailyMealplan model, so we don't include them
    #         }
    #         print("Processed result: ", result)  # Print to debug
    #         daily_meals.append(result)  # Unpack the result dictionary

    #     return daily_meals


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
                "day_plan_id": 0,
                "week_plan_id": result["week_plan_id"],
                "date": result["date"].strftime("%Y-%m-%d"),
                "meal_id": result["meal_id"]
            }
        return [DailyMealplan(**item) for item in results]
        

