# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.schema import Attachment


class UserProfile:
    def __init__(self, name: str = None, cpf: str = None, id_usuario: int = None):
        self.nome = name
        self.cpf = cpf
        self.id_usuario = id_usuario