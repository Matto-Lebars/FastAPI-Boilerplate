from src.app.core.helper.crud import HelperCRUD
from src.app.models.user import User

crud_user: HelperCRUD[User] = HelperCRUD(model=User)
