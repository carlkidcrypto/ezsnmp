======
Images
======

Overview
========
This directory contains images and graphics used in the EzSnmp project documentation
and README files.

Image Files
===========

``ezsnmp_logo.jpeg``
--------------------
The official EzSnmp project logo. This image is displayed in:

* Main project README
* GitHub repository header
* Documentation landing page

``buy_me_a_coffee.png``
-----------------------
Button/badge image linking to the project maintainer's support page. This image is
used in the README to allow users to support the project financially.

Usage in Documentation
======================
Images from this directory are referenced in reStructuredText documents using
relative paths:

.. code-block:: rst

    .. image:: images/ezsnmp_logo.jpeg
        :alt: EzSnmp Logo

Or in Markdown:

.. code-block:: markdown

    ![EzSnmp Logo](images/ezsnmp_logo.jpeg)

Best Practices
==============
When adding images to this directory:

* Use descriptive filenames
* Optimize images for web display (reasonable file sizes)
* Provide alt text when using images in documentation
* Use common formats: PNG for graphics/logos, JPEG for photos
* Keep aspect ratios consistent for similar image types

Related Documentation
=====================
* `Main README <../README.rst>`_
* `Sphinx Documentation <../sphinx_docs_build/source/index.rst>`_
