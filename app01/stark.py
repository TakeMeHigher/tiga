from app01 import  models
from django.utils.safestring import mark_safe
from stark.service import v1
from django.forms import  ModelForm

class UserinfoForm(ModelForm):
   class Meta:
      model=models.Userinfo
      fields='__all__'
      error_messages={
          "name":{"required":'用户名不能为空'},
          "addr":{'required':"地址不能为空"}
       }

class UserInfoConfig(v1.TigaConfig):

   list_display = ['id','name','addr','email']

   model_class_form=UserinfoForm

v1.site.register(models.Userinfo,UserInfoConfig)


class UserTypeConfig(v1.TigaConfig):
   list_display = ['id','name']
v1.site.register(models.UserType,UserTypeConfig)


class RoleConfig(v1.TigaConfig):
   list_display = ['id','caption']
v1.site.register(models.Role,RoleConfig)




#主要是为了测试
class HostForm(ModelForm):
   class Meta:
      model=models.Host
      fields='__all__'

      error_messages={
         'hostname':{"required":"主机名不能为空"},
         'ip':{"required":"ip不能为空"},
         'port':{"required":"port不能为空"}
      }


class HostConfig(v1.TigaConfig):
   def ip_port(self,obj=None,is_head=False):
      if is_head:
         return 'ip和端口'
      return '%s_%s'%(obj.ip,obj.port)

   list_display = ['hostname','ip','port',ip_port]
   model_class_form=HostForm
v1.site.register(models.Host,HostConfig)
