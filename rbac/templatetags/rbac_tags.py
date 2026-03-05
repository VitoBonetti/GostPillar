from django import template
from rbac.policy import can_view, can_edit, is_god, is_admin

register = template.Library()

@register.simple_tag(takes_context=True)
def gp_can_view(context, obj):
    return can_view(context["request"].user, obj)

@register.simple_tag(takes_context=True)
def gp_can_edit(context, obj):
    return can_edit(context["request"].user, obj)

@register.simple_tag(takes_context=True)
def gp_is_god(context):
    return is_god(context["request"].user)

@register.simple_tag(takes_context=True)
def gp_is_admin(context):
    return is_admin(context["request"].user)