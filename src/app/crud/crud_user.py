from src.app.core.helper.crud import CRUDBase
from src.app.models.user import User

crud_user: CRUDBase[User] = CRUDBase(model=User)
