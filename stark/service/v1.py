from django.conf.urls import url
from django.shortcuts import HttpResponse

class TigaConfig(object):
    def __init__(self,model_class,site):
        self.model_class=model_class
        self.site=site

    def changlist_view(self,request,*args,**kwargs):
        return HttpResponse("list")

    def add_view(self,request,*args,**kwargs):
        return HttpResponse("add")

    def chang_view(self,request,nid,*args,**kwargs):
        return HttpResponse("change")

    def delete_view(self,request,nid,*args,**kwargs):
        return HttpResponse("delete")

    def get_urls(self):
        model_class_app=(self.model_class._meta.app_label,self.model_class._meta.model_name)
        tem=[
            url(r'^$',self.changlist_view,name='%s_%s_changelist'%model_class_app),
            url(r'^add/$',self.add_view,name='%s_%s_add'%model_class_app),
            url(r'^(\d+)/change/$',self.chang_view,name='%s_%s_change'%model_class_app),
            url(r'^(\d+)/delete/$',self.delete_view,name='%s_%s_delete'%model_class_app)
        ]

        return tem


    @property
    def urls(self):
        return  self.get_urls()

class TigaSite(object):
    def __init__(self):
        self._registry={}

    def register(self,model_class,tiga_config_class=None):
        if not tiga_config_class:
            tiga_config_class=TigaConfig
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



site=TigaSite()