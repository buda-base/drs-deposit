project = "drs-deposit"
copyright = '2026, Jim Katz, Buddhist Digital Resource Center'
author = 'Jim Katz, Buddhist Digital Resource Center'
release = 'v1.1.0'
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.githubpages",
    "myst_parser",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

master_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".venv", "venv"]


templates_path = ['_templates']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'classic'
html_static_path = ['_static']

# MyST Parser configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_image",
]
