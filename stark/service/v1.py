from django.conf.urls import url
from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import ModelForm
from utils.pager import Pagination
class StarkConfig(object):
    list_display=[]
    def __init__(self,model_class,site):
        self.model_class=model_class
        self.site=site

#-----------------------------------权限相关-----------------------------------------------------
    add_btn=True
    def get_add_btn(self):
        return self.add_btn

#-----------------------------------权限相关  结束-----------------------------------------------------


#-------------------------------------列表页面展示相关list_dispaly--------------------------------------------------------------------
    #开始复选框
    def checkbox(self, obj=None, is_head=False):
        if is_head:
            return '选择'

        return mark_safe("<input type='checkbox' name='pk' value='%s'>" % (obj.id,))
    #编辑
    def edit(self, obj=None, is_head=False):
        if is_head:
            return '编辑'
        return mark_safe("<a href='%s'>编辑</a>" % self.get_change_url(obj.id))

    #删除
    def delete(self,obj=None,is_head=False):
        if is_head:
            return '删除'
        return  mark_safe("<a href='%s'>删除</a>" % self.get_delete_url(obj.id))

    #列表页面展示字段
    def get_list_display(self):
        data=[]
        if self.list_display:
            data.extend(self.list_display)
            data.append(StarkConfig.edit)
            data.append(StarkConfig.delete)
            data.insert(0, StarkConfig.checkbox)
        return data


#-------------------------------------列表页面展示相关list_dispaly 结束--------------------------------------------------------------------




# ---------------------------------------url相关-----------------------------------------------------
    # 总的url
    def get_urls(self):
        model_class_app = (self.model_class._meta.app_label, self.model_class._meta.model_name)
        urlpatterns = [
            url(r'^$', self.changlist_view, name='%s_%s_changelist' % model_class_app),
            url(r'^add/$', self.add_view, name='%s_%s_add' % model_class_app),
            url(r'^(\d+)/change/$', self.chang_view, name='%s_%s_change' % model_class_app),
            url(r'^(\d+)/delete/$', self.delete_view, name='%s_%s_delete' % model_class_app)
        ]
        urlpatterns.extend(self.extra_url())
        return urlpatterns

    # 额外的url 在自己的config中定义该函数添加
    def extra_url(self):
        return []

    @property
    def urls(self):
        return self.get_urls()

    def get_list_url(self):
        name = 'tiga:%s_%s_changelist' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        list_url = reverse(name)
        return list_url

    def get_add_url(self):
        name = 'tiga:%s_%s_add' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        add_url = reverse(name)
        return add_url

    def get_change_url(self, nid):
        name = 'tiga:%s_%s_change' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        edit_url = reverse(name, args=(nid,))
        return edit_url

    def get_delete_url(self, nid):
        name = 'tiga:%s_%s_delete' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        del_url = reverse(name, args=(nid,))
        return del_url





# --------------------------- ------------------url相关 结束----------------------------------------------------------------




            #---------------------------------视图函数相关------------------------------------------------------------
    #字段列表展示页面视图函数
    def changlist_view(self,request,*args,**kwargs):
        #thead名称
        head_list=[]
        for field_name in self.get_list_display():
            if isinstance(field_name,str):
                #获取该字段的名称也就是class中的verbose_name
                verbose_name=self.model_class._meta.get_field(field_name).verbose_name
            else:
                verbose_name=field_name(self,is_head=True)

            head_list.append(verbose_name)


        #获取当前类中的所有对象
        data_list=self.model_class.objects.all()
        pageObj=Pagination(request.GET.get('page',1),len(data_list),request.path_info,request.GET,per_page_count=1)

        per_page_data_list=data_list[pageObj.start:pageObj.end]
        page_html=pageObj.page_html()
        #存储tr
        new_data_list=[]
        for dataObj in per_page_data_list:
            #tr
            tem=[]
            if not self.list_display:
                tem.append(dataObj)
            else:
                for field_name in self.get_list_display():
                    #如果是字符串
                   if isinstance(field_name,str):
                        #td
                       val=getattr(dataObj,field_name)
                   #如果是函数名
                   else:
                       val=field_name(self,dataObj)

                   tem.append(val)
            new_data_list.append(tem)


        print(new_data_list)
        return render(request,'stark/changelist.html',{'new_data_list':new_data_list,'head_list':head_list,'add_url':self.get_add_url(),'add_btn':self.get_add_btn(),"page_html":page_html})

        #另一种方法用yield实现
        # thead名称
        # head_list = []
        # def inner():
        #     for field_name in self.list_display:
        #         if isinstance(field_name, str):
        #             # 获取该字段的名称也就是class中的verbose_name
        #             verbose_name = self.model_class._meta.get_field(field_name).verbose_name
        #         else:
        #             verbose_name = field_name(self, is_head=True)
        #         yield  verbose_name
        #
        #
        # data_list = self.model_class.objects.all()
        # print(data_list)
        # # 存储tr
        #
        # def wapper():
        #     new_data_list = []
        #
        #     for dataObj in data_list:
        #         # tr
        #         def inner(dataObj):
        #             if not self.list_display:
        #                 yield dataObj
        #             else:
        #                 for field_name in self.list_display:
        #                     print(self.list_display)
        #                     if isinstance(field_name, str):
        #                         val = getattr(dataObj, field_name)
        #                         print(val)
        #                     else:
        #                         val = field_name(self, dataObj)
        #                     yield val
        #         yield inner(dataObj)
        # return render(request, 'stark/changelist.html', {'new_data_list': wapper(), 'head_list': inner()})

    model_class_form=None
    def get_model_class_form(self):
        if self.model_class_form:
            return self.model_class_form
        else:
            class TigetherForm(ModelForm):
                class Meta:
                    model=self.model_class
                    fields='__all__'

            return TigetherForm



    #添加视图
    def add_view(self,request,*args,**kwargs):
        AddForm=self.get_model_class_form()
        if request.method=='GET':
            form=AddForm()
            return render(request,'stark/add.html',{"form":form})
        else:
            form=AddForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())
            return render(request, 'stark/add.html', {"form": form})
    #编辑视图
    def chang_view(self,request,nid,*args,**kwargs):
       obj=self.model_class.objects.filter(pk=nid).first()
       EditForm=self.get_model_class_form()
       if request.method=='GET':
           form=EditForm(instance=obj)
           return render(request,'stark/edit.html',{"form":form})
       else:
           form=EditForm(instance=obj,data=request.POST)
           if form.is_valid():
               form.save()
               return redirect(self.get_list_url())
           return render(request, 'stark/edit.html', {"form": form})

    #删除视图
    def delete_view(self,request,nid,*args,**kwargs):
        self.model_class.objects.filter(pk=nid).delete()
        return redirect(self.get_list_url())

#-------------------------------------视图函数结束-------------------------------------------------------


class StarkSite(object):
    def __init__(self):
        self._registry={}

    def register(self,model_class,tiga_config_class=None):
        if not tiga_config_class:
            tiga_config_class=StarkConfig
        self._registry[model_class]=tiga_config_class(model_class,self)

    def get_urls(self):
        urlpattern=[]
        for model_class,tiga_config_obj in self._registry.items():
            cls_name=model_class._meta.model_name
            app_name=model_class._meta.app_label

            curd_url=url(r'^{0}/{1}/'.format(app_name,cls_name),(tiga_config_obj.urls,None,None))

            urlpattern.append(curd_url)
        return urlpattern

    @property
    def urls(self):
        return (self.get_urls(),None,'tiga')



site=StarkSite()