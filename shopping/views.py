from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from .services import (
    latest_shopping_list,
    regenerate_shopping_list,
    update_bought_flags,
)


class ShoppingListView(LoginRequiredMixin, TemplateView):
    template_name = "shopping/shopping_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        sl = latest_shopping_list(self.request.user)

        ctx["shopping_list"] = sl
        ctx["items"] = (
            sl.items.select_related("ingredient").order_by("ingredient__name")
            if sl
            else []
        )

        return ctx

    def post(self, request, *args, **kwargs):
        if "regenerate" in request.POST:
            sl = regenerate_shopping_list(request.user)
            if sl is None:
                messages.warning(
                    request,
                    "Nothing to add yet. Create meal plans with breakfast, lunch, or dinner "
                    "recipes that include ingredient lines.",
                )
            else:
                messages.success(
                    request,
                    "Shopping list updated from your meal plans. Similar ingredients are combined into one total quantity.",
                )
        elif "save_bought" in request.POST:
            bought = {int(x) for x in request.POST.getlist("bought") if x.isdigit()}
            update_bought_flags(request.user, bought)
            messages.success(request, "Saved what you have already bought.")
        return redirect("shopping:list")
