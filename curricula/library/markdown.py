import re
import contextlib
from typing import TextIO, Dict, Callable, Any, List


class ItemizeBuilder:
    """Context for managing a list generator."""

    items: List[str]
    indent: int

    def __init__(self, indent: int = 0):
        """Just use the file of the document."""

        self.items = []
        self.indent = indent

    def add(self, item: str):
        """Add a bullet to the document."""

        self.items.append(" " * self.indent + "- {}".format(item.strip()))

    def get(self) -> str:
        """Return the string itemize."""

        return "\n".join(self.items)

    @contextlib.contextmanager
    def start_itemize(self):
        """Open an itemizing context, resulting in a bulleted list."""

        builder = ItemizeBuilder(indent=self.indent + 4)
        yield builder
        self.items.extend(builder.items)


class EnumerateBuilder:
    """Context for managing an enumeration generator."""

    items: List[str]
    counter: int
    indent: int

    def __init__(self, counter: int = 1, indent: int = 0):
        """Just use the file of the document."""

        self.items = []
        self.counter = counter
        self.indent = indent

    def add(self, item: str):
        """Add a bullet to the document."""

        self.items.append(" " * self.indent + "{}. {}".format(self.counter, item.strip()))
        self.counter += 1

    def get(self) -> str:
        """Return the string itemize."""

        return "\n".join(self.items)

    @contextlib.contextmanager
    def start_enumerate(self, counter: int = 1):
        """Open an itemizing context, resulting in a bulleted list."""

        builder = EnumerateBuilder(counter=counter, indent=self.indent + 4)
        yield builder
        self.add(builder.get())


class Builder:
    """A loose wrapper for a Markdown document."""

    def __init__(self):
        """Create a builder with an empty section list."""

        self.sections = []

    def add(self, section: str):
        """Add a section to the document, strip whitespace."""

        self.sections.append(section.strip() + "\n\n")

    def add_header(self, contents: str, *, level: int = 1):
        """Add a header section."""

        self.add("{} {}".format("#" * level, contents))

    def add_code(self, contents: str, *, language: str = ""):
        """Add a code block."""

        self.add("```{}\n{}\n```".format(language, contents))

    def add_front_matter(self, **kwargs):
        """Add a front matter header in YAML format."""

        lines = tuple("{}: {}".format(key, value) for key, value in kwargs.items())
        self.add("\n".join(("---",) + lines + ("---",)))

    @contextlib.contextmanager
    def start_itemize(self):
        """Open an itemizing context, resulting in a bulleted list."""

        builder = ItemizeBuilder()
        yield builder
        self.add(builder.get())

    @contextlib.contextmanager
    def start_enumerate(self, counter: int = 1):
        """Open an itemizing context, resulting in a bulleted list."""

        builder = EnumerateBuilder(counter=counter)
        yield builder
        self.add(builder.get())

    def get(self) -> str:
        """Return the string itemize."""

        return "\n".join(self.sections)


INTERPOLATION_PATTERN = re.compile(r"(?<!\\)" r"\[\[\s*" r"(.+?)" r"\s*\]\]")

NAMESPACE = {}

FILTERS = {
    "datetime": lambda d: d.strftime("%B %d, %Y at %H:%M"),
    "date": lambda d: d.strftime("%B %d, %Y"),
    "str": lambda x: str(x),
}


def underwrite(top: dict, bottom: dict) -> dict:
    """Add any keys not in bottom to top, return top."""

    for key in bottom:
        if key not in top:
            top[key] = bottom[key]
    return top


def get(obj, *keys):
    """Descend a list of string properties."""

    for key in keys:
        obj = obj[key] if hasattr(obj, "__getitem__") else getattr(obj, key)
    return obj


class Template:
    """Tools for manipulating a Markdown template."""

    contents: str

    def __init__(self, file: TextIO):
        """Load a Markdown template from a path."""

        self.contents = file.read()

    def interpolate(self, namespace: Dict[str, Any], filters: Dict[str, Callable[[Any], Any]] = None) -> str:
        """Interpolate the file with values and filters."""

        contents = self.contents
        namespace = underwrite(namespace, NAMESPACE)
        filters = underwrite(filters, FILTERS) if filters is not None else {}

        matches = list(INTERPOLATION_PATTERN.finditer(contents))
        for match in reversed(matches):
            variable_name, *filter_names = map(str.strip, match.group().split("|"))
            result = get(namespace, variable_name.split("."))
            for filter_name in filter_names:
                result = filters[filter_name](result)
            contents = contents[:match.start()] + str(result) + contents[match.end():]
        return contents
