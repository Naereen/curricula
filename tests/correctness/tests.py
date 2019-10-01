import sys
import shutil
from pathlib import Path

sys.path.append(str(Path(__file__).absolute().parent.parent.parent))
from curricula.grade.shortcuts import *
from curricula.grade.library import process


grader = Grader()
root = Path(__file__).absolute().parent


def overwrite_directory(path: Path):
    if path.exists():
        shutil.rmtree(str(path))
    path.mkdir()


@grader.setup(required=True)
def check_program(context: Context, log: Logger):
    """Check if the program has been submitted."""

    if not context.target.joinpath("program.cpp").exists():
        return CheckResult(complete=True, passed=False, error="missing file test.cpp")
    log[2]("Found program.cpp")
    return CheckResult(complete=True, passed=True)


@grader.setup(required=True)
def build_program(context: Context, log: Logger, resources: dict):
    """Compile program with GCC."""

    source = context.target.joinpath("program.cpp")
    build = root.joinpath("build")
    overwrite_directory(build)
    executable = build.joinpath("program")

    runtime = process.run("g++", "-Wall", "-o", str(executable), str(source), timeout=5)
    if runtime.code != 0:
        return BuildResult(passed=False, error="failed to build program", runtime=runtime.dump())

    log[2]("Successfully built program")
    resources.update(program=Executable(str(executable)))
    return BuildResult(passed=True, runtime=runtime.dump())


@grader.test()
def test_pass(program: Executable):
    """Basic pass."""

    runtime = program.execute("pass", timeout=1)
    passed = runtime.stdout.strip() == b"pass"
    return CorrectnessResult(passed, runtime)


@grader.test()
def test_fail(log: Logger, program: Executable):
    """Basic pass with fail."""

    runtime = program.execute("fail", timeout=1)
    passed = runtime.stdout.strip() == b"pass"
    result = CorrectnessResult(passed, runtime)
    if not passed:
        log[2]("Expected pass, got", runtime.stdout.strip())
    return result


@grader.test()
def test_error(log: Logger, program: Executable):
    """Basic pass with error handling."""

    runtime = program.execute("error", timeout=1.0)
    if runtime.code != 0:
        log[2]("Received return code", runtime.code)
        for line in filter(None, runtime.stderr.split(b"\n")):
            log[4](line)
        return CorrectnessResult(False, runtime)

    passed = runtime.stdout.strip() == b"pass"
    log[2]("Expected pass, got fail")
    return CorrectnessResult(passed, runtime)


@grader.test()
def test_fault(log: Logger, program: Executable):
    """Basic pass with fault detection."""

    runtime = program.execute("fault", timeout=1.0)
    if runtime.code != 0:
        log[2]("Received return code", runtime.code)
        for line in filter(None, runtime.stderr.split(b"\n")):
            log[4](line)
        if runtime.code == -11:
            log[4]("Segmentation fault")
        return CorrectnessResult(False, runtime)

    passing = runtime.stdout.strip() == b"pass"
    log("Expected pass, got fail")
    return CorrectnessResult(passing, runtime)


@grader.test()
def test_timeout(log: Logger, program: Executable):
    """Basic pass with timeout."""

    runtime = program.execute("hang", timeout=1.0)

    if runtime.timeout:
        return CorrectnessResult(False, runtime)

    if runtime.code != 0:
        log("Received return code", runtime.code)
        for line in filter(None, runtime.stderr.split(b"\n")):
            log[2](line)
        if runtime.code == -11:
            log[2]("Segmentation fault")
        return CorrectnessResult(False, runtime)

    passing = runtime.stdout.strip() == b"pass"
    log("Expected pass, got fail")
    return CorrectnessResult(passing, runtime)


if __name__ == "__main__":
    from curricula.grade import main
    main(grader)
