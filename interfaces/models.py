from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from typing import Any


class Meals(BaseModel):
    id_meal: str = Field(alias='idMeal')
    str_meal: str = Field(alias='strMeal')
    str_instructions: str = Field(alias='strInstructions')
    ingredients: list = Field(default=[])

    @model_validator(mode='before')
    @classmethod
    def check_card_number_omitted(cls, data: Any) -> Any:
        ingredients = []
        if isinstance(data, dict):
            for k, v in data.items():
                if k.__contains__('strIngredient'):
                    if v:
                        ingredients.append(v)
            data['ingredients'] = ingredients
        return data


class Responce(BaseModel):
    meals: Optional[List[Meals]] = Field(default=None, alias='meals')
