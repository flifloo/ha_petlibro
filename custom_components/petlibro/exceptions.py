from homeassistant.exceptions import HomeAssistantError


class PetLibroAPIError(HomeAssistantError):
    "Basic API error"


class PetLibroCannotConnect(PetLibroAPIError):
    """Error to indicate we cannot connect."""


class PetLibroInvalidAuth(PetLibroAPIError):
    """Error to indicate there is invalid auth."""

class PetLibroLoginExpired(PetLibroAPIError):
    """Error to indicate that the token has expired."""
