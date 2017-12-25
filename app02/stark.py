from django.utils.safestring import mark_safe
from stark.service import v1
from app02 import  models

from django.forms import ModelForm
from  django.shortcuts import redirect,render,HttpResponse


class UserInfoForm(ModelForm):
    class Meta:
        model=models.UserInfo
        fields='__all__'
        error_messages={
            'name':{
                'required':"用户名不能为空"
            },
            'email':{
                'required':"地址不能为空"
            }
        }

class UserInfoConfig(v1.StarkConfig):
    def display_gender(self,obj=None,is_head=False):
        if is_head:
            return '性别'
        return obj.get_gender_display()

    def dispaly_depart(self,obj=None,is_head=False):
        if is_head:
            return '部门'
        return obj.depart.caption


    def dispaly_roles(self,obj=None,is_head=False):
        if is_head:
            return '角色'

        roles=obj.roles.all()
        l=[]
        for role in roles:
            l.append(role.title)
        return ','.join(l)



    list_display=['id',"name",'email',display_gender,dispaly_depart,dispaly_roles]

    model_class_form=UserInfoForm

    show_search_form=True

    search_fileds=['name__contains','email__contains']

    show_action=True
    def multi_del(self,request):
        id_list=request.POST.getlist('pk')
        # print(id_list,'****------')
        self.model_class.objects.filter(id__in=id_list).delete()
        return redirect(self.get_list_url())

    multi_del.short_desc='批量删除'

    def multi_info(self,request):
        pass

    multi_info.short_desc='批量初始化'

    action_func_list=[multi_del,multi_info]

    combine_seach=[
        v1.FilterOption('gender', is_choice=True),
        v1.FilterOption('depart'),
        v1.FilterOption('roles', is_choice=False,is_multi=True),
    ]

v1.site.register(models.UserInfo,UserInfoConfig)



class RoleConfig(v1.StarkConfig):

    list_display=['id','title']
v1.site.register(models.Role,RoleConfig)


class UserTypeConfig(v1.StarkConfig):
    list_display=['id','caption']


v1.site.register(models.Department,UserTypeConfig)
