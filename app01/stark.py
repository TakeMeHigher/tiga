from app01 import  models
from django.utils.safestring import mark_safe
from stark.service import v1

class UserInfoConfig(v1.TigaConfig):
   def checkbox(self,obj=None,is_head=False):
       if is_head:
           return '选择'

       return mark_safe("<input type='checkbox' name='pk' value='%s'>"%(obj.id,))

   def edit(self,obj=None,is_head=False):
       if is_head:
           return '编辑'
       return mark_safe("<a href='/edit/%s/'>编辑</a>"%(obj.id,))

   list_display = [checkbox,'id','name','addr',edit]
v1.site.register(models.Userinfo,UserInfoConfig)


class UserTypeConfig(v1.TigaConfig):
   list_display = ['id','name']
v1.site.register(models.UserType,UserTypeConfig)


class RoleConfig(v1.TigaConfig):
   list_display = ['id','caption']
v1.site.register(models.Role,RoleConfig)