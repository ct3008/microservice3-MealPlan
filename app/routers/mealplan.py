# mealplan_router.py
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from typing import List, Dict

from app.models.mealplan_model import Mealplan, DailyMealplan, WeeklyMealplan, PaginatedResponse
from app.resources.mealplan_resource import MealplanResource
from app.services.service_factory import ServiceFactory
import asyncio
import time
import httpx
import requests

router = APIRouter()

@router.post("/mealplans", tags=["mealplans"], status_code=201, response_model=Mealplan)
async def create_mealplan(mealplan: Mealplan) -> Mealplan:
    """
    Create a new meal plan.
    """
    res = ServiceFactory.get_service("MealplanResource")
    try:
        # Log the input for debugging
        print("Creating new meal plan:", mealplan)
        
        # Pass the meal plan data to the service for creation
        new_mealplan = res.create_meal_plan(mealplan)
        return new_mealplan
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error in create_mealplan endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create meal plan: {e}")

@router.get("/mealplans/{meal_id}", tags=["mealplans"], response_model=Mealplan)
async def get_mealplan_by_id(meal_id: int) -> Mealplan:
    """
    Retrieve a meal plan by its ID.
    """
    res = ServiceFactory.get_service("MealplanResource")
    result = res.get_by_key(meal_id, "meal_plans")
    print(result)

    if not result:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    return result

# @router.get("/mealplans/{user_id}/{meal_id}", tags=["mealplans"], response_model=Mealplan)
# async def get_mealplan_with_user_id(user_id: int, meal_id: int) -> Mealplan:
#     """
#     Retrieve a meal plan by its ID.
#     """
#     print("USER ID MEALPLAN: ", user_id)
#     res = ServiceFactory.get_service("MealplanResource")
#     result = res.get_by_key(meal_id, "meal_plans")
#     print(result)

#     if not result:
#         raise HTTPException(status_code=404, detail="Meal plan not found")

#     return result

@router.put("/mealplans/{meal_id}", tags=["mealplans"], response_model=Mealplan)
async def update_mealplan_by_id(meal_id: int, mealplan: Mealplan) -> Mealplan:
    """
    Update a meal plan by its ID.
    """
    res = ServiceFactory.get_service("MealplanResource")
    update_data = mealplan.dict(exclude_unset=True)
    updated_mealplan = res.update_meal_plan(meal_id, update_data)

    if not updated_mealplan:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    return updated_mealplan


tasks_status: Dict[str, dict] = {}

async def get_mealplan_async(background_tasks: BackgroundTasks, task_id: str, meal_id: int):
    async def fetch_mealplan(meal_id: int):
        await asyncio.sleep(30)  # Simulating a delay
        return {"meal_id": meal_id, "status": "fetched"}
    mealplan = await fetch_mealplan(meal_id)
    tasks_status[task_id] = {"status": "completed", "mealplan": mealplan}

async def start_task(background_tasks: BackgroundTasks, task_id: str, meal_id: int):
    tasks_status[task_id] = {"status": "in-progress"}
    background_tasks.add_task(get_mealplan_async, background_tasks, task_id, meal_id)

@router.post("/mealplans/start-task")
async def start_mealplans_task(background_tasks: BackgroundTasks, meal_id: int):
    task_id = str(time.time())
    await start_task(background_tasks, task_id, meal_id)
    # return {"message": "Meal plan fetching initiated", "task_id": task_id, "status": 202}
    return JSONResponse(
        status_code=202,  # Set the status code to 202
        content={"message": "Meal plan fetching initiated", "task_id": task_id, "status": 202}
    )

@router.get("/mealplans/poll/{task_id}")
async def poll_task_status(task_id: str):
    task = tasks_status.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task["status"] == "in-progress":
        return {"task_id": task_id, "status": "in-progress", "message": "Task is still running."}
    if task["status"] == "completed":
        return {"task_id": task_id, "status": "completed", "mealplan": task["mealplan"]}
    raise HTTPException(status_code=500, detail="Unknown task status")

@router.put("/mealplans/{meal_id}", tags=["mealplans"], response_model=Mealplan)
async def update_mealplan_by_id(meal_id: int, mealplan: Mealplan) -> Mealplan:
    """
    Update a meal plan by its ID.
    """
    res = ServiceFactory.get_service("MealplanResource")
    update_data = mealplan.dict(exclude_unset=True)
    updated_mealplan = res.update_meal_plan(meal_id, update_data)

    if not updated_mealplan:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    return updated_mealplan

# @router.get("/mealplans/async/{meal_id}", tags=["mealplans"])
async def get_mealplans_async():
    res = ServiceFactory.get_service("MealplanResource")

    async def fetch_mealplan(meal_id):
        try:
            return await res.get_by_key_async(meal_id, "meal_plans")
        except Exception as e:
            return {"meal_id": meal_id, "error": str(e)}

    meal_ids = [1, 2, 3, 7, 8]
    mealplans = await asyncio.gather(*(fetch_mealplan(meal_id) for meal_id in meal_ids))
    return {"mealplans": mealplans}

# @router.get("/mealplans/sync/{meal_id}", tags=["mealplans"])
def get_mealplans_sync():
    res = ServiceFactory.get_service("MealplanResource")
    def fetch_mealplan(meal_id):
        try:
            return res.get_by_key(meal_id, "meal_plans")
        except Exception as e:
            return {"meal_id": meal_id, "error": str(e)}

    meal_ids = [1, 2, 3, 7,8]
    mealplans = [fetch_mealplan(meal_id) for meal_id in meal_ids]
    return {"mealplans": mealplans}

@router.get("/mealplans/test/{meal_id}", tags=["mealplans"])
async def test_mealplans_performance(meal_id: int):
    def call_async_mealplans():
        start_time = time.time()
        response = get_mealplans_async()
        async_duration = time.time() - start_time
        return response, async_duration

    def call_sync_mealplans():
        start_time = time.time()
        response = get_mealplans_sync()
        sync_duration = time.time() - start_time
        return response, sync_duration

    async_response, async_time = call_async_mealplans()
    sync_response, sync_time = call_sync_mealplans()

    return {
        "async_time_taken": async_time,
        "sync_time_taken": sync_time,
    }

# END OF MEALPLANS

@router.put("/weekly-mealplans/{week_plan_id}", tags=["weekly-mealplans"], response_model=WeeklyMealplan)
async def update_weekly_mealplan_by_id(week_plan_id: int, weekly_mealplan: WeeklyMealplan) -> WeeklyMealplan:
    """
    Update a meal plan by its ID.
    """
    res = ServiceFactory.get_service("MealplanResource")
    update_data = weekly_mealplan.dict(exclude_unset=True)
    updated_mealplan = res.update_weekly_meal_plan(week_plan_id, update_data)

    if not updated_mealplan:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    return updated_mealplan

@router.put("/daily-mealplans/{day_plan_id}", tags=["daily-mealplans"], response_model=DailyMealplan)
async def update_daily_mealplan_by_id(day_plan_id: int, daily_mealplan: DailyMealplan) -> DailyMealplan:
    """
    Update a meal plan by its ID.
    """
    res = ServiceFactory.get_service("MealplanResource")
    update_data = daily_mealplan.dict(exclude_unset=True)
    updated_daily_mealplan = res.update_daily_meal_plan(day_plan_id, update_data)

    if not updated_daily_mealplan:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    return updated_daily_mealplan



@router.delete("/mealplans/{meal_id}", tags=["mealplans"])
async def delete_mealplan_by_id(meal_id: int):
    """
    Delete a meal plan by its ID.
    """
    res = ServiceFactory.get_service("MealplanResource")
    res.delete_meal_plan(meal_id)
    return {"message": f"Meal plan with ID {meal_id} has been deleted"}

@router.delete("/daily-mealplans/{day_plan_id}", tags=["daily-mealplans"])
async def delete_daily_mealplan_by_id(day_plan_id: int):
    """
    Delete a daily meal plan by its ID.
    """
    res = ServiceFactory.get_service("MealplanResource")
    res.delete_daily_meal_plan(day_plan_id)
    return {"message": f"Meal plan with ID {day_plan_id} has been deleted"}

@router.delete("/weekly-mealplans/{weekly_meal_id}", tags=["weekly-mealplans"])
async def delete_weekly_mealplan_by_id(weekly_meal_id: int):
    """
    Delete a weekly meal plan by its ID.
    """
    res = ServiceFactory.get_service("MealplanResource")
    res.delete_weekly_meal_plan(weekly_meal_id)
    return {"message": f"Meal plan with ID {weekly_meal_id} has been deleted"}

@router.post("/weekly-mealplans", tags=["weekly-mealplans"], status_code=201, response_model=WeeklyMealplan)
async def create_weekly_mealplan(weekly_mealplan: WeeklyMealplan) -> WeeklyMealplan:
    """
    Create a new weekly meal plan.
    """
    res = ServiceFactory.get_service("MealplanResource")
    try:
        new_weekly_plan = res.create_weekly_meal_plan(weekly_mealplan)
        return new_weekly_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create weekly meal plan: {e}")

@router.get("/weekly-mealplans/{week_plan_id}", tags=["weekly-mealplans"], response_model=WeeklyMealplan)
async def get_weekly_mealplan_by_id(week_plan_id: int) -> WeeklyMealplan:
    """
    Retrieve a weekly meal plan by its ID.
    """
    res = ServiceFactory.get_service("MealplanResource")
    result = res.get_by_key(week_plan_id, "weekly_meal_plans")

    if not result:
        raise HTTPException(status_code=404, detail="Weekly meal plan not found")

    return result

@router.post("/daily-mealplans", tags=["daily-mealplans"], status_code=201, response_model=DailyMealplan)
async def create_daily_mealplan(daily_mealplan: DailyMealplan) -> DailyMealplan:
    """
    Create a new daily meal plan.
    """
    res = ServiceFactory.get_service("MealplanResource")
    try:
        new_daily_plan = res.create_daily_meal_plan(daily_mealplan)
        return new_daily_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create daily meal plan: {e}")

@router.get("/daily-mealplans/{day_plan_id}", tags=["daily-mealplans"], response_model=DailyMealplan)
async def get_daily_mealplan_by_id(day_plan_id: int) -> DailyMealplan:
    """
    Retrieve a daily meal plan by its ID.
    """
    res = ServiceFactory.get_service("MealplanResource")
    result = res.get_by_key(day_plan_id, "daily_meal_plans")

    if not result:
        raise HTTPException(status_code=404, detail="Daily meal plan not found")

    return result

@router.get("/weekly-mealplans/{week_plan_id}/daily-mealplans", tags=["weekly-mealplans"], response_model=List[DailyMealplan])
async def get_daily_mealplans_by_week(week_plan_id: int) -> List[DailyMealplan]:
    """
    Retrieve all daily meal plans within a weekly plan by the weekly plan ID.
    """
    res = ServiceFactory.get_service("MealplanResource")
    daily_mealplans = res.get_daily_meal_plans_by_week(week_plan_id)

    if not daily_mealplans:
        raise HTTPException(status_code=404, detail="No daily meal plans found for this weekly plan")

    return daily_mealplans

@router.get("/weekly-mealplans", tags=["weekly-mealplans"])
async def get_daily_meal_plans_by_date(date: str):
    """
    Retrieve all daily meal plans within a weekly plan by the weekly plan ID.
    """
    res = ServiceFactory.get_service("MealplanResource")
    daily_mealplans = res.get_daily_meal_plans_by_date(date)
    # print("DAILY: ", daily_mealplans)

    if not daily_mealplans:
        raise HTTPException(status_code=404, detail="No daily meal plans found for this weekly plan")
    print(daily_mealplans)
    return daily_mealplans

@router.get("/mealplans", tags=["mealplans"], response_model=PaginatedResponse)
async def get_all_mealplans(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to retrieve")
) -> PaginatedResponse:
    """
    Retrieve all meal plans with pagination.
    """
    res = ServiceFactory.get_service("MealplanResource")
    mealplans = res.get_all_meal_plans(skip=skip, limit=limit)
    total_count = res.get_total_count()

    base_url = str(request.url).split('?')[0]
    links = {
        "first": {"href": f"{base_url}?skip=0&limit={limit}"},
        "last": {"href": f"{base_url}?skip={(total_count // limit) * limit}&limit={limit}"}
    }

    if skip + limit < total_count:
        links["next"] = {"href": f"{base_url}?skip={skip + limit}&limit={limit}"}
    if skip > 0:
        links["previous"] = {"href": f"{base_url}?skip={max(skip - limit, 0)}&limit={limit}"}

    return PaginatedResponse(items=mealplans, links=links)

@router.get("/weekly-mealplans/all", tags=["weekly-mealplans"], response_model=PaginatedResponse)
async def get_all_weekly_mealplans(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to retrieve")
) -> PaginatedResponse:
    """
    Retrieve all meal plans with pagination.
    """
    res = ServiceFactory.get_service("MealplanResource")
    weekly_mealplans = res.get_all_weekly_meal_plans(skip=skip, limit=limit)
    total_count = res.get_total_count()

    base_url = str(request.url).split('?')[0]
    links = {
        "first": {"href": f"{base_url}?skip=0&limit={limit}"},
        "last": {"href": f"{base_url}?skip={(total_count // limit) * limit}&limit={limit}"}
    }

    if skip + limit < total_count:
        links["next"] = {"href": f"{base_url}?skip={skip + limit}&limit={limit}"}
    if skip > 0:
        links["previous"] = {"href": f"{base_url}?skip={max(skip - limit, 0)}&limit={limit}"}

    return PaginatedResponse(items=weekly_mealplans, links=links)

@router.get("/daily-mealplans", tags=["daily-mealplans"], response_model=PaginatedResponse)
async def get_all_daily_mealplans(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to retrieve")
) -> PaginatedResponse:
    """
    Retrieve all meal plans with pagination.
    """
    res = ServiceFactory.get_service("MealplanResource")
    daily_mealplans = res.get_all_daily_meal_plans(skip=skip, limit=limit)
    total_count = res.get_total_count()

    base_url = str(request.url).split('?')[0]
    links = {
        "first": {"href": f"{base_url}?skip=0&limit={limit}"},
        "last": {"href": f"{base_url}?skip={(total_count // limit) * limit}&limit={limit}"}
    }

    if skip + limit < total_count:
        links["next"] = {"href": f"{base_url}?skip={skip + limit}&limit={limit}"}
    if skip > 0:
        links["previous"] = {"href": f"{base_url}?skip={max(skip - limit, 0)}&limit={limit}"}

    return PaginatedResponse(items=daily_mealplans, links=links)