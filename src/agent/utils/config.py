import dataclasses
import re
import typing

import agent.utils.consts


@dataclasses.dataclass
class PPECredentials:
    email: str
    password: str = dataclasses.field(repr=False)
    id: int | None = dataclasses.field(default=None)

    __EMAIL_REGEX = r"^\S+@\S+\.\S+$"

    def __post_init__(self) -> None:
        self._validate_email()
        self.password = self.password.strip()

    def _validate_email(self) -> None:
        self.email = self.email.strip()
        if not re.match(self.__EMAIL_REGEX, self.email):
            raise ValueError('Invalid email address')

    def get_form_data(self) -> dict[str, typing.Any]:
        return {
            agent.utils.consts.PPE_LOGIN_FORM_USERNAME_ID: str(self.email),
            agent.utils.consts.PPE_LOGIN_FORM_PASSWORD_ID: str(self.password)
        } | agent.utils.consts.PPE_LOGIN_FORM_ADDITIONAL_DATA
