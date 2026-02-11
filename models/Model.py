from pydantic import BaseModel
from typing import List


class Model(BaseModel):
    model_name: str
    model_code: int = 1607392319
    fields: List[dict] = [
        {"name": "Question"},
        {"name": "Answer"},
    ]
    templates: List[dict] = [{}]


# my_model = genanki.Model(
#     1607392319,
#     "Simple Model",
#     fields=[
#         {"name": "Question"},
#         {"name": "Answer"},
#     ],
#     templates=[
#         {
#             "name": "Card 1",
#             "qfmt": "{{Question}}",
#             "afmt": '{{FrontSide}}<hr id="answer">{{Answer}}',
#         },
#     ],
# )
