# from tortoise import Tortoise
# Tortoise.init_models(["__main__"], "models")

from tortoise.contrib.pydantic import pydantic_model_creator

from models import Tags

Tag_Pydantic = pydantic_model_creator(Tags, name="Tag")
TagIn_Pydantic = pydantic_model_creator(
    Tags, name='TagIn', exclude_readonly=True)