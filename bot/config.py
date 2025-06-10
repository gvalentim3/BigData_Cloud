#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    URL_PREFIX = os.environ.get("URL_PREFIX", "https://projeto-ibmec-cloud-9016-2025-f8hhfgetc3g3a2fg.centralus-01.azurewebsites.net")
