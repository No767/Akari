# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Akari"
copyright = "2023, No767 (Noelle)"
author = "No767"
release = "v0.2.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# "sphinxawesome_theme.docsearch"
extensions = [
    "sphinxawesome_theme.highlighting",
    "myst_parser",
    "sphinxemoji.sphinxemoji",
    "sphinx_design",
]
myst_enable_extensions = ["colon_fence"]

templates_path = ["_templates"]
exclude_patterns = []

source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinxawesome_theme"
html_static_path = ["_static"]

html_theme_options = {
    "logo_light": "_static/akari-v2.1-heart-24.png",
    "logo_dark": "_static/akari-v2.1-heart-24.png",
}
