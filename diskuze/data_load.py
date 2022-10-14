# from typing import List
#
# from aiodataloader import DataLoader
#
# from diskuze import db
# from diskuze.models import User
#
#
# class UserDataLoader(DataLoader):
#     async def batch_load_fn(self, keys: List[int]) -> List[User]:
#         return db.session.query(User).filter(User.id.in_(keys)).all()
#
#
# # user_loader = UserDataLoader()
