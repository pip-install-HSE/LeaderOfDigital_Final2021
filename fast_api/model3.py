# from tortoise import Tortoise
# Tortoise.init_models(["__main__"], "models")

from tortoise.contrib.pydantic import pydantic_model_creator

from models import Objects

Object_Pydantic = pydantic_model_creator(Objects, name="Object")
ObjectIn_Pydantic = pydantic_model_creator(
    Objects, name='ObjectIn', exclude_readonly=True)