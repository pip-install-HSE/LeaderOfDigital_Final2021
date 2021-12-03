# from tortoise import Tortoise
# Tortoise.init_models(["__main__"], "models")

from tortoise.contrib.pydantic import pydantic_model_creator

from models import Tasks

Task_Pydantic = pydantic_model_creator(Tasks, name="Task")
TaskIn_Pydantic = pydantic_model_creator(
    Tasks, name='TaskIn', exclude_readonly=True)