from app01 import  models
from stark.service import v1

class UserInfoConfig(v1.TigaConfig):
   pass
v1.site.register(models.Userinfo)
v1.site.register(models.UserType)
v1.site.register(models.Role)