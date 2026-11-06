# Security policy

## Reporting a vulnerability

Please don't open a public issue. Report it privately through GitHub instead:
go to the [Security tab](https://github.com/bensynapse/jsonrpcclient/security)
and click "Report a vulnerability". Only the maintainers can see the report.

Include the version, a short description and, if you can, code that shows the
problem. We'll reply within a week.

## Supported versions

| Version | Security fixes | Bug fixes |
|---|---|---|
| 5.0 release candidates | Yes | Yes |
| 4.x | Yes | Yes |
| 3.x and older | No | No |

4.x is the supported line until 5.0.0 is released. After that, 5.x is the
supported line, and 4.x gets security fixes for 12 months from the 5.0.0
release date. Other 4.x bug fixes in that time are at our discretion. After 12
months, 4.x gets no more releases.

Release candidates, such as 5.0.0rc1, get fixes in the next release candidate
or in 5.0.0.

A fix comes out as a new release of each supported line, so upgrade to the
latest release of your line to get it. Older releases within a line don't get
updates.

Each line has its own docs: the version menu at the top of
https://bensynapse.github.io/jsonrpcclient/ switches between them.

## Old domains

jsonrpcclient no longer controls its old website domains, jsonrpcclient.com
and jsonrpcserver.com. They now belong to someone else, so ignore them and any
links to them. The copy of the docs at explodinglabs.com/jsonrpcclient/ is old
and no longer updated.

The only official places are this repository,
https://bensynapse.github.io/jsonrpcclient/ and
https://pypi.org/project/jsonrpcclient/.
