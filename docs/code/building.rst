How to build the distribution locally for testing
=================================================

As the docs are .rst files that have to be built into HTML to be viewed, it is very useful to be able to build the docs locally to see what the HTML will look like.
Sphinx uses Python, so you must have it installed. 
You can then simply run (recommended in a virtual environment):

.. code-block::

    pip install -r requirements.txt

in the ``docs`` directory of the repository, to install the required python packages.
Followed by: 

.. code-block::

    make html

in the same directory to create the html files in the ``docs/_build`` directory.
Simply open ``docs/_build/html/index.html`` with a web browser to see your local version of the docs.
