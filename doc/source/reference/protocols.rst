.. include:: ../refs.rst

.. _reference-protocols:

=========
Protocols
=========

These runtime-checkable :class:`~typing.Protocol` classes define the interfaces
that custom artifact exporters and importers must satisfy. Use them with
:func:`isinstance` to verify conformance at runtime.

ArtifactExporter
----------------

.. autoclass:: django_snapshots.artifacts.protocols.ArtifactExporter
   :members:
   :show-inheritance:

AsyncArtifactExporter
---------------------

.. autoclass:: django_snapshots.artifacts.protocols.AsyncArtifactExporter
   :members:
   :show-inheritance:

ArtifactImporter
----------------

.. autoclass:: django_snapshots.artifacts.protocols.ArtifactImporter
   :members:
   :show-inheritance:

AsyncArtifactImporter
---------------------

.. autoclass:: django_snapshots.artifacts.protocols.AsyncArtifactImporter
   :members:
   :show-inheritance:
