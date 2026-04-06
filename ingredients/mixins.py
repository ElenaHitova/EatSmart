from django.contrib.auth.mixins import UserPassesTestMixin
from accounts.roles import can_manage_food_catalog


def user_can_manage_ingredients(user) -> bool:
    return can_manage_food_catalog(user)


class CanManageIngredientsMixin(UserPassesTestMixin):

    def test_func(self):
        return can_manage_food_catalog(self.request.user)