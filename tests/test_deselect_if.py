import pytest
from pytest import ExitCode


def dont_use_mark_alias(code):
    newcode = code.replace("from pytest_deselect_if import deselect_if", "")
    newcode = newcode.replace("@deselect_if", "@pytest.mark.deselect_if")
    return newcode


mark_alias = pytest.mark.parametrize(
    "transform_code",
    [lambda x: x, dont_use_mark_alias],
    ids=["use_mark_alias", "dont_use_mark_alias"],
)


def test_run_without_deselect_marker(pytester):
    """Test should run normally without the deselect_if marker."""
    pytester.makepyfile(
        """
        def test_simple_case():
            assert 1 == 1
        """
    )
    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(
        [
            "*::test_simple_case PASSED*",
        ]
    )
    assert result.ret == 0


@mark_alias
def test_not_parametrized_class(pytester, transform_code):
    """Test that an error is raised when the deselect_if marker is used on a non-parametrized test."""
    pytester.makepyfile(
        transform_code(
            """
        import pytest
        from pytest_deselect_if import deselect_if

        @pytest.mark.deselect_if(func=lambda **kwargs: True)
        class TestTestClass:
            def test_not_parametrized(self):
                assert 1 == 1
        """
        )
    )
    result = pytester.runpytest("-v")
    result.stdout.re_match_lines(
        [
            r".*ValueError: deselect_if can only be run on parametrized tests.*",
        ]
    )
    assert result.ret != 0


@mark_alias
def test_class_decoration_applies_to_functions(pytester, transform_code):
    """Test that the deselect_if marker can be applied to a class and will apply to all functions in the class."""
    pytester.makepyfile(
        transform_code(
            """
        import pytest
        from pytest_deselect_if import deselect_if

        param_decorator = pytest.mark.parametrize('param', [1, 2])

        @param_decorator
        @pytest.mark.deselect_if(func=lambda param, **kwargs: param == 2)
        class TestTestClass:
            def test_one(self, param):
                assert param != 2

            def test_two(self, param):
                assert param < 2
        """
        )
    )
    result = pytester.runpytest("-v")
    result.stdout.re_match_lines(
        [
            r"^collecting ... collected 4 items \/ 2 deselected \/ 2 selected$",
            r".*::TestTestClass::test_one\[1\] PASSED.*",
            r".*::TestTestClass::test_two\[1\] PASSED.*",
        ]
    )
    assert result.ret == 0


@mark_alias
def test_class_decoration_with_function_deselectif(pytester, transform_code):
    """Test that the deselect_if marker can be applied to a class and will apply to all functions in the class."""
    pytester.makepyfile(
        transform_code(
            """
        import pytest
        from pytest_deselect_if import deselect_if

        param_decorator = pytest.mark.parametrize('param', [1, 2])

        @pytest.mark.deselect_if(func=lambda param, **kwargs: param == 2)
        class TestTestClass:
            def test_one(self):
                assert param != 2

            @param_decorator
            def test_two(self, param):
                assert param < 2
        """
        )
    )
    result = pytester.runpytest("-v")
    result.stdout.re_match_lines(
        [
            r"^.*ValueError: deselect_if can only be run on parametrized tests$",
        ]
    )
    assert result.ret == ExitCode.INTERNAL_ERROR


@mark_alias
def test_class_decoration_with_function_deselectif_with_raise_when_not_parametrized(
    pytester, transform_code
):
    """Test that the deselect_if marker can be applied to a class and will apply to all functions in the class."""
    pytester.makepyfile(
        transform_code(
            """
        import pytest
        from pytest_deselect_if import deselect_if

        param_decorator = pytest.mark.parametrize('param', [1, 2])

        @pytest.mark.deselect_if(func=lambda param, **kwargs: param == 2, raise_when_not_parametrized=False)
        class TestTestClass:
            def test_one(self):
                assert 2 == 2

            @param_decorator
            def test_two(self, param):
                assert param < 2
        """
        )
    )
    result = pytester.runpytest("-v")
    result.stdout.re_match_lines(
        [
            r"^collecting ... collected 3 items \/ 1 deselected \/ 2 selected$",
            r".*::TestTestClass::test_one PASSED.*",
            r".*::TestTestClass::test_two\[1\] PASSED.*",
        ]
    )
    assert result.ret == 0


@mark_alias
def test_class_parametrized_decoration_on_function_deselectif(pytester, transform_code):
    """Test that the deselect_if marker can be applied to a class and will apply to all functions in the class."""
    pytester.makepyfile(
        transform_code(
            """
        import pytest
        from pytest_deselect_if import deselect_if

        param_decorator = pytest.mark.parametrize('param', [1, 2])

        @param_decorator
        class TestTestClass:
            @pytest.mark.deselect_if(func=lambda param, **kwargs: param == 2)
            def test_one(self, param):
                assert param < 2

            def test_two(self, param):
                assert param < 3
        """
        )
    )
    result = pytester.runpytest("-v")
    result.stdout.re_match_lines(
        [
            r"^collecting ... collected 4 items \/ 1 deselected \/ 3 selected$",
            r".*::TestTestClass::test_one\[1\] PASSED.*",
            r".*::TestTestClass::test_two\[1\] PASSED.*",
            r".*::TestTestClass::test_two\[2\] PASSED.*",
        ]
    )
    assert result.ret == 0


@mark_alias
def test_not_parametrized(pytester, transform_code):
    """Test that an error is raised when the deselect_if marker is used on a non-parametrized test."""
    pytester.makepyfile(
        transform_code(
            """
        import pytest
        from pytest_deselect_if import deselect_if

        @pytest.mark.deselect_if(func=lambda **kwargs: True)
        def test_not_parametrized():
            assert 1 == 1
        """
        )
    )
    result = pytester.runpytest("-v")
    result.stdout.re_match_lines(
        [
            r".*ValueError: deselect_if can only be run on parametrized tests.*",
        ]
    )
    assert result.ret != 0


@mark_alias
def test_no_func_arg_error(pytester, transform_code):
    """Test that an error is raised when the deselect_if marker has no func argument."""
    pytester.makepyfile(
        transform_code(
            """
        import pytest

        @pytest.mark.deselect_if
        def test_no_func_arg():
            assert 1 == 1
        """
        )
    )
    result = pytester.runpytest("-v")
    result.stdout.re_match_lines(
        [
            r".*ValueError: deselect_if marker must have a func argument.*",
        ]
    )
    assert result.ret != 0


@mark_alias
def test_deselect_based_on_condition(pytester, transform_code):
    """Test that a test is deselected based on the deselect_if condition."""
    pytester.makepyfile(
        transform_code(
            """
        import pytest
        from pytest_deselect_if import deselect_if

        param_decorator = pytest.mark.parametrize('param', [1, 2])

        @param_decorator
        @deselect_if(func=lambda param, **kwargs: param == 2)
        def test_condition_met(param):
            assert param != 2
        """
        )
    )
    result = pytester.runpytest("-v")
    result.stdout.re_match_lines(
        [
            r"^collecting ... collected 2 items \/ 1 deselected \/ 1 selected$",
            r".*::test_condition_met\[1\] PASSED.*",
        ]
    )
    assert result.ret == 0


@mark_alias
def test_run_when_condition_not_met(pytester, transform_code):
    """Ensure test runs when the deselect_if condition is not met."""
    pytester.makepyfile(
        transform_code(
            """
        import pytest
        from pytest_deselect_if import deselect_if

        param_decorator = pytest.mark.parametrize('param', [3, 4])

        @param_decorator
        @deselect_if(func=lambda param, **kwargs: param == 2)
        def test_condition_not_met(param):
            assert param > 2
        """
        )
    )
    result = pytester.runpytest("-v")
    result.stdout.re_match_lines(
        [
            r"^collecting ... collected 2 items$",
            r".*::test_condition_not_met\[3\] PASSED.*",
            r".*::test_condition_not_met\[4\] PASSED.*",
        ]
    )
    assert result.ret == 0


@mark_alias
def test_multiple_parameters_and_conditions(pytester, transform_code):
    """Test with multiple parameters and a more complex deselect condition."""
    pytester.makepyfile(
        transform_code(
            """
        import pytest
        from pytest_deselect_if import deselect_if

        param1_decorator = pytest.mark.parametrize('param1', [1, 2])
        param2_decorator = pytest.mark.parametrize('param2', [1, 3])

        @param2_decorator
        @param1_decorator
        @deselect_if(func=lambda param1, param2, **kwargs: param1 == param2)
        def test_complex_condition(param1, param2):
            assert param1 != param2
        """
        )
    )
    result = pytester.runpytest("-v")
    result.stdout.re_match_lines(
        [
            r"^collecting ... collected 4 items \/ 1 deselected \/ 3 selected$",
            r".*::test_complex_condition\[1-3\] PASSED.*",
            r".*::test_complex_condition\[2-1\] PASSED.*",
            r".*::test_complex_condition\[2-3\] PASSED.*",
        ]
    )
    assert result.ret == 0


@mark_alias
def test_deselection_through_markers(pytester, transform_code):
    """Test with multiple parameters and a more complex deselect condition."""
    # register mymarker
    pytester.makeini(
        """
        [pytest]
        markers =
            mymarker: my custom marker
    """
    )
    pytester.makepyfile(
        transform_code(
            """
        import pytest
        from pytest_deselect_if import deselect_if

        param1_decorator = pytest.mark.parametrize('param1', [1, 2])
        param2_decorator = pytest.mark.parametrize('param2', [1, 3])

        @param2_decorator
        @param1_decorator
        @pytest.mark.mymarker
        @deselect_if(func=lambda param1, param2, **kwargs: param1 == param2)
        def test_complex_condition(param1, param2):
            assert param1 != param2
        """
        )
    )
    result = pytester.runpytest("-v", "-m", "not mymarker")
    result.stdout.re_match_lines(
        [
            r"^collecting ... collected 4 items \/ 4 deselected \/ 0 selected$",
        ]
    )
    assert result.ret == ExitCode.NO_TESTS_COLLECTED


def test_help_message(pytester):
    result = pytester.runpytest(
        "--markers",
    )
    result.stdout.fnmatch_lines(
        [
            "@pytest.mark.deselect_if(func(**kwargs)): tests marked with deselect_if will not be collected if func(**kwargs) returns True - like skipif but output will be deselected rather than skipped",
        ]
    )
