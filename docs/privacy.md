# Public demonstration boundaries

All fixtures and generated data are fictional. This repository contains no real
recordings, customer contacts, production logs, database exports, supplier prices,
internal infrastructure addresses or authentication material.

Sensitive configuration files, private key formats, tokens, non-public addresses
and unexpected personal emails are checked by `tools/check_public_content.py`.
It reports locations/categories, never matched secret values. These checks are
defence in depth, not a guarantee that arbitrary content is safe to publish.
Publication also requires human review of the outgoing files and history.

The only personal contact deliberately public is the candidate's resume email.
SSH credentials and private project evidence remain outside the repository.
Git metadata includes the candidate's chosen name and resume email.

No source-system snapshot is imported or filtered into this repository. The demos
are independently prepared examples of previously used integration patterns.
