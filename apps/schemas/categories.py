from apps.schemas.up_model import UpModel
from apps.schemas.common import ResourceRef

class CategoryAttributes(UpModel):
    name: str

class ParentRelationship(UpModel):
    data: ResourceRef | None = None

class CategoryRelationships(UpModel):
    parent: ParentRelationship

class CategoryResource(UpModel):
    id: str
    attributes: CategoryAttributes
    relationships: CategoryRelationships
    
class CategoriesPage(UpModel):
    data: list[CategoryResource]
