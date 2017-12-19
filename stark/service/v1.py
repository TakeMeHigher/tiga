from django.conf.urls import url
from django.shortcuts import HttpResponse, render, redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import ModelForm
from django.http import QueryDict
from django.db.models import Q

from utils.pager import Pagination


# 封装列表页面  因为列表页面代码太多啦 而却有好几个功能
class ChangeList(object):
    def __init__(self, config, querySet):
        # 当前操作的StarkConfig对象
        self.config = config
        # 所展示的字段
        self.list_display = config.get_list_display()
        # 当前所操作的model类
        self.model_class = config.model_class
        # 获取request
        self.request = config.request

        # 总记录数 分页时用到
        total_count = len(querySet)
        self.total_count = total_count

        # 当前页
        self.current_page = config.request.GET.get('page', 1)

        # 分页对象
        pageObj = Pagination(self.current_page, self.total_count, self.request.path_info, self.request.GET,
                             per_page_count=1)

        self.pageObj = pageObj

        # 每一页所显示的记录数
        self.per_page_data_list = querySet[self.pageObj.start:self.pageObj.end]

        # 前端页面添加按钮的url
        self.add_url = config.get_add_url()

        # 是否有添加按钮
        self.add_btn = config.get_add_btn()

        #是否显示搜索框
        self.show_search_form=config.get_show_search_form()
        #搜索框的value和url同步
        self.search_form_val=self.request.GET.get(config.search_key,' ')



    # 获取thead名称
    def head_list(self):
        # thead名称
        result = []
        for field_name in self.list_display:
            if isinstance(field_name, str):
                # 获取该字段的名称也就是class中的verbose_name
                verbose_name = self.model_class._meta.get_field(field_name).verbose_name
            else:
                # 不是字符串的话就是函数 调用当前函数 注意是函数也就是类调用的
                verbose_name = field_name(self.config, is_head=True)

            result.append(verbose_name)
        return result

    # tbody数据
    def body_list(self):
        new_data_list = []

        # dataObj model实例
        for dataObj in self.per_page_data_list:
            # tr
            tem = []
            if not self.list_display:
                tem.append(dataObj)
            else:
                for field_name in self.list_display:
                    # 如果是字符串
                    if isinstance(field_name, str):
                        # td
                        val = getattr(dataObj, field_name)
                    # 如果是函数名
                    else:
                        val = field_name(self.config, dataObj)
                    tem.append(val)
            new_data_list.append(tem)
        return new_data_list


class StarkConfig(object):


    def __init__(self, model_class, site):
        self.model_class = model_class
        self.site = site

        # 保存搜索条件传入的参数，比如修改后调回当前页 而不是 首页
        self._query_param_key = '_listfilter'
        # request参数
        self.request = None


        self.search_key='_q'

    # -----------------------------------获取request编写的装饰器-----------------------------------------
    # 为了获取request，方便在edit add delete 中获取request.GET
    def wrap(self, view_func):
        def inner(request, *args, **kwargs):
            self.request = request
            return view_func(request, *args, **kwargs)

        return inner

    # -------------------------------------获取request编写的装饰器结束----------------------------------------------------------


    #*********************************************权限相关***************************************************



   #-----------------------添加按钮-----------------------------------------------------------------------
    #调用时可以定制
    add_btn = True
    def get_add_btn(self):
        return self.add_btn
    #-----------------------------添加按钮结束--------------------------------------------------------------


    #-----------------------搜索框-----------------------------------------------------------------------
    #定制
    show_search_form=False
    def get_show_search_form(self):
        return self.show_search_form

    # 定制
    search_fileds=[]
    def get_search_fileds(self):
        data=[]
        if self.search_fileds:
            data.extend(self.search_fileds)
        return data

    def get_search_condition(self):
        key_word=self.request.GET.get(self.search_key)
        search_fileds=self.get_search_fileds()
        condition=Q()
        condition.connector='or'
        if key_word and self.get_show_search_form():
            for filed in search_fileds:
                condition.children.append((filed,key_word))

        return condition




    #-----------------------------搜索框结束-----------------------------------------------------------------



    # ****************************************权限相关  结束*********************************************************************


    # -------------------------------------列表页面展示相关list_dispaly--------------------------------------------------------------------
    # 开始复选框
    def checkbox(self, obj=None, is_head=False):
        if is_head:
            return '选择'

        return mark_safe("<input type='checkbox' name='pk' value='%s'>" % (obj.id,))

    # 编辑
    def edit(self, obj=None, is_head=False):
        if is_head:
            return '编辑'
        parms = QueryDict(mutable=True)
        query_url = self.request.GET.urlencode()
        if query_url:
            parms[self._query_param_key] = query_url
            return mark_safe("<a href='%s?%s'>编辑</a>" % (self.get_change_url(obj.id), parms.urlencode()))
        return mark_safe("<a href='%s'>编辑</a>" % (self.get_change_url(obj.id)))

    # 删除
    def delete(self, obj=None, is_head=False):
        if is_head:
            return '删除'
        parms = QueryDict(mutable=True)
        query_url = self.request.GET.urlencode()
        parms[self._query_param_key] = query_url
        return mark_safe("<a href='%s?%s'>删除</a>" % (self.get_delete_url(obj.id), parms.urlencode()))

    # 列表页面展示字段
    list_display = []
    def get_list_display(self):
        data = []
        if self.list_display:
            data.extend(self.list_display)
            data.append(StarkConfig.edit)
            data.append(StarkConfig.delete)
            data.insert(0, StarkConfig.checkbox)
        return data

        # -------------------------------------列表页面展示相关list_dispaly 结束--------------------------------------------------------------------

    # ---------------------------------------url相关-----------------------------------------------------
    # 总的url
    def get_urls(self):
        model_class_app = (self.model_class._meta.app_label, self.model_class._meta.model_name)
        urlpatterns = [
            url(r'^$', self.wrap(self.changlist_view), name='%s_%s_changelist' % model_class_app),
            url(r'^add/$', self.wrap(self.add_view), name='%s_%s_add' % model_class_app),
            url(r'^(\d+)/change/$', self.wrap(self.chang_view), name='%s_%s_change' % model_class_app),
            url(r'^(\d+)/delete/$', self.wrap(self.delete_view), name='%s_%s_delete' % model_class_app)
        ]
        urlpatterns.extend(self.extra_url())
        return urlpatterns

    # 额外的url 在自己的config中定义该函数添加
    def extra_url(self):
        return []

    @property
    def urls(self):
        return self.get_urls()

    # 列表页面的url
    def get_list_url(self):
        name = 'stark:%s_%s_changelist' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        list_url = reverse(name)
        return list_url

    # 添加按钮的url
    def get_add_url(self):
        name = 'stark:%s_%s_add' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        add_url = reverse(name)
        return add_url

    # 编辑的url
    def get_change_url(self, nid):
        name = 'stark:%s_%s_change' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        edit_url = reverse(name, args=(nid,))
        return edit_url

    # 删除的url
    def get_delete_url(self, nid):
        name = 'stark:%s_%s_delete' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        del_url = reverse(name, args=(nid,))
        return del_url

    # --------------------------- ------------------url相关 结束----------------------------------------------------------------




    # ---------------------------------视图函数相关------------------------------------------------------------
    model_class_form = None
    def get_model_class_form(self):
        if self.model_class_form:
            return self.model_class_form
        else:
            class TigetherForm(ModelForm):
                class Meta:
                    model = self.model_class
                    fields = '__all__'

            return TigetherForm

    # 字段列表展示页面视图函数
    def changlist_view(self, request, *args, **kwargs):

        # 获取当前类中的所有对象
        data_list = self.model_class.objects.filter(self.get_search_condition()).all()

        cl = ChangeList(self, data_list)
        return render(request, 'stark/changelist.html',
                      {'cl': cl})

        # 另一种方法用yield实现
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

    # 添加视图
    def add_view(self, request, *args, **kwargs):
        AddForm = self.get_model_class_form()
        if request.method == 'GET':
            form = AddForm()
            return render(request, 'stark/add.html', {"form": form})
        else:
            form = AddForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())
            return render(request, 'stark/add.html', {"form": form})

    # 编辑视图
    def chang_view(self, request, nid, *args, **kwargs):
        obj = self.model_class.objects.filter(pk=nid).first()
        EditForm = self.get_model_class_form()
        if request.method == 'GET':
            form = EditForm(instance=obj)
            return render(request, 'stark/edit.html', {"form": form})
        else:
            form = EditForm(instance=obj, data=request.POST)
            if form.is_valid():
                form.save()
                print(request.GET)
                list_query_str = request.GET.get(self._query_param_key)
                list_url = '%s?%s' % (self.get_list_url(), list_query_str)
                return redirect(list_url)
            return render(request, 'stark/edit.html', {"form": form})

    # 删除视图
    def delete_view(self, request, nid, *args, **kwargs):
        self.model_class.objects.filter(pk=nid).delete()
        return redirect(self.get_list_url())


# -------------------------------------视图函数结束-------------------------------------------------------


class StarkSite(object):
    def __init__(self):
        self._registry = {}

    def register(self, model_class, tiga_config_class=None):
        if not tiga_config_class:
            tiga_config_class = StarkConfig
        self._registry[model_class] = tiga_config_class(model_class, self)

    def get_urls(self):
        urlpattern = []
        for model_class, tiga_config_obj in self._registry.items():
            cls_name = model_class._meta.model_name
            app_name = model_class._meta.app_label

            curd_url = url(r'^{0}/{1}/'.format(app_name, cls_name), (tiga_config_obj.urls, None, None))

            urlpattern.append(curd_url)
        return urlpattern

    @property
    def urls(self):
        return (self.get_urls(), None, 'stark')


site = StarkSite()
