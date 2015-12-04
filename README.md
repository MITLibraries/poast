# poast

This application will generate and send email messages to MIT authors with information about their download statistics for the OA collection.

## Installation

Use pip to install poast into a virtualenv:

```bash
$ pip install https://github.com/MITLibraries/poast/zipball/master
```

In order to connect to the data warehouse you will also need to install the `cx_Oracle` python package into your virtualenv. Steps 1-5 detailed at https://blogs.oracle.com/opal/entry/configuring_python_cx_oracle_and should be sufficient.

## Usage

You can view the help menu for the `poast` command with:

```bash
$ poast --help
```

There are two subcommands. The `queue` subcommand will generate the email messages and the `mail` subcommand will send the messages. You can view the help menu for each command with:

```bash
$ poast queue --help
$ poast mail --help
```
