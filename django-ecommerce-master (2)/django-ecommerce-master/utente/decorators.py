from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from djecommerce import settings


def manager_only(view_func):
    user_is_manager = user_passes_test(
        lambda user: user.is_manager,
        login_url=settings.LOGIN_URL
    )
    return login_required(user_is_manager(view_func))

