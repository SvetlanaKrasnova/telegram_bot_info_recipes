from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from typing import Any


class Meal(BaseModel):
    id_meal: str = Field(default='', alias='idMeal')
    str_meal: str = Field(default='', alias='strMeal')
    str_instructions: str = Field(default='', alias='strInstructions')
    ingredients: list = Field(default=[])
    status: str = Field(default='Success', alias='status')

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


class ResponceMeals(BaseModel):
    meals: Optional[List[Meal]] = Field(default=None, alias='meals')
