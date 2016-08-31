Configuration
=============

The configuration file is in `toml`_. A sample configuration file ``config.toml.sample`` is provided.

There are multiple sections of interest:

.. _`toml`: https://github.com/toml-lang/toml

Inputs and Outputs
~~~~~~~~~~~~~~~~~~

Here is a sample configuration for a local syslog listener (an input, then)::

    [inputs.localsyslog]
    key = "local.syslog" # mandatory
    class = "UDPSyslogInput" # mandatory
    # these have "sensible" defaults :)
    host = "localhost"
    port = 5141

As we can see, there is a section title, called "inputs.localsyslog", which is just a name we give to this input. As you can see, we also specify the class to use.

The ``key`` parameter is used to "tag" the Messages recieved via this input, for further routing and processing.

The other parameters are optional, and should provide reasonnable defaults.

For further information on writing such modules and the full argument list for each input/output, please look at :doc:`inputs` and :doc:`outputs`.


