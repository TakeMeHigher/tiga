from django.conf.urls import url
from django.shortcuts import HttpResponse,render

class TigaConfig(object):
    list_display=[]
    def __init__(self,model_class,site):
        self.model_class=model_class
        self.site=site

    def changlist_view(self,request,*args,**kwargs):
        head_list=[]
        for field_name in self.list_display:
            if isinstance(field_name,str):
                verbose_name=self.model_class._meta.get_field(field_name).verbose_name
            else:
                verbose_name=field_name(self,is_head=True)

            head_list.append(verbose_name)



        data_list=self.model_class.objects.all()
        print(data_list)
        new_data_list=[]
        for dataObj in data_list:
            tem=[]
            for field_name in self.list_display:
                if isinstance(field_name,str):
                    val=getattr(dataObj,field_name)
                else:
                    val=field_name(self,dataObj)

                tem.append(val)
            new_data_list.append(tem)


        print(new_data_list)
        return render(request,'stark/changelist.html',{'new_data_list':new_data_list,'head_list':head_list})

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