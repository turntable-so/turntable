import os
from functools import wraps

from pyinstrument import Profiler


def pyprofile(show_all=False, save_html=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = Profiler()
            profiler.start()

            try:
                result = func(*args, **kwargs)
            finally:
                profiler.stop()
                if save_html:
                    save_path = f"scripts/debug/profile/{func.__name__}.html"
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    profiler.write_html(save_path, show_all=show_all)
                else:
                    print(
                        profiler.output_text(
                            unicode=True, color=True, show_all=show_all
                        )
                    )

            return result

        return wrapper

    return decorator
