class ClienteNotFoundError(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Cliente com e-mail '{email}' não encontrado")


class ClienteAlreadyExistsError(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Cliente com e-mail '{email}' já está cadastrado")


class WebhookEventAlreadyProcessedError(Exception):
    def __init__(self, event_id: str):
        self.event_id = event_id
        super().__init__(f"Evento '{event_id}' já foi processado")
