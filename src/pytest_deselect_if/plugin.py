from typing import Callable

import pytest
from pytest import Function, MarkDecorator, hookimpl


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "deselect_if(func(**kwargs)): tests marked with deselect_if"
        " will not be collected if func(**kwargs) returns True - "
        "like skipif but output will be deselected rather than skipped",
    )


@hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]):
    removed = []
    kept = []
    for item in items:
        m = item.get_closest_marker("deselect_if")
        if m:
            try:
                func = m.kwargs["func"]
            except KeyError:
                raise ValueError("deselect_if marker must have a func argument")
            if not (hasattr(item, "callspec") and hasattr(item.callspec, "params")):
                if m.kwargs.get("raise_when_not_parametrized", True):
                    raise ValueError(
                        "deselect_if can only be run on parametrized tests"
                    )
            elif isinstance(item, Function) and func(**item.callspec.params):
                removed.append(item)
                continue
        kept.append(item)
    if removed:
        config.hook.pytest_deselected(items=removed)
        items[:] = kept


class _DeselectIfMarkDecorator(MarkDecorator):
    def __call__(  # type: ignore[override,empty-body]
        self,
        func: Callable[..., bool],
        raise_when_not_parametrized: bool = True,
    ) -> MarkDecorator:
        """
        Mark a test to be deselected if `func(**params)` returns True.

        Keyword arguments:
        :param Function func: function to determine if the test should be deselected
        :param bool raise_when_not_parametrized: raise an error if the mark is applied on a test that is not parametrized defaults to True - but you may want to disable it if marking test classes while only the test methods are parametrized
        """
        ...  # pragma: no cover - it's just type hints


deselect_if: _DeselectIfMarkDecorator = pytest.mark.deselect_if  # type: ignore[assignment]
