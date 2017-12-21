from django.template import Library
from django.urls import reverse

from stark.service.v1 import site

register =Library()


@register.inclusion_tag('stark/form.html')
def form(model_obj_form):
    new_form = []
    for bfield in model_obj_form:
        temp = {"is_popup": False, "bfiled": bfield}
        from django.forms import ModelChoiceField
        if isinstance(bfield.field, ModelChoiceField):
            relate_class_name = bfield.field.queryset.model
            if relate_class_name in site._registry:
                app_model_name = relate_class_name._meta.app_label, relate_class_name._meta.model_name
                baseurl = reverse('stark:%s_%s_add' % app_model_name)
                popurl = '%s?_popbackid=%s' % (baseurl, bfield.auto_id)
                temp["is_popup"] = True
                temp['popurl'] = popurl

        new_form.append(temp)

    return {"form":new_form}