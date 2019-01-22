from os.path import dirname, abspath
import sys

sys.path.append(dirname(dirname(abspath(__file__))))
from grade.test import Target, Result, register
from grade.test.middleware import iterated


def i(size: int):
    return " " * (size - 1)


@register(middleware=iterated)
def test_pass(target: Target):
    """Basic pass."""

    runtime = target.run("pass", timeout=1)
    passing = runtime.stdout.strip() == "pass"
    yield Result(runtime, passing)


@register(middleware=iterated)
def test_fail(target: Target):
    """Basic pass with fail."""

    runtime = target.run("fail", timeout=1)
    passing = runtime.stdout.strip() == "pass"
    yield Result(runtime, passing)
    if not passing:
        print(i(2), "expected pass, got", runtime.stdout.strip())


@register(middleware=iterated)
def test_error(target: Target):
    """Basic pass with error handling."""

    runtime = target.run("error", timeout=1.0)
    if runtime.code != 0:
        yield Result(runtime, False)
        print(i(2), "received return code", runtime.code)
        for line in filter(None, runtime.stderr.split("\n")):
            print(i(4), line)

    passing = runtime.stdout.strip() == "pass"
    yield Result(runtime, passing)
    print(i(2), "expected pass, got fail")


@register(middleware=iterated)
def test_fault(target: Target):
    """Basic pass with fault detection."""

    runtime = target.run("fault", timeout=1.0)
    if runtime.code != 0:
        yield Result(runtime, False)
        print(i(2), "received return code", runtime.code)
        for line in filter(None, runtime.stderr.split("\n")):
            print(i(4), line)
        if runtime.code == -11:
            print(i(4), "segmentation fault")

    passing = runtime.stdout.strip() == "pass"
    yield Result(runtime, passing)
    print(i(2), "expected pass, got fail")


@register(middleware=iterated)
def test_timeout(target: Target):
    """Basic pass with timeout."""

    runtime = target.run("hang", timeout=1.0)

    if runtime.timeout is not None:
        yield Result(runtime, False)

    if runtime.code != 0:
        yield Result(runtime, False)
        print(i(2), "received return code", runtime.code)
        for line in filter(None, runtime.stderr.split("\n")):
            print(i(4), line)
        if runtime.code == -11:
            print(i(4), "segmentation fault")

    passing = runtime.stdout.strip() == "pass"
    yield Result(runtime, passing)
    print(i(2), "expected pass, got fail")


if __name__ == "__main__":
    from grade.standalone import main
    main()
