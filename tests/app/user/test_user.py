from fastapi import status
from httpx import AsyncClient

from app.main import app


async def test_get_me(client: AsyncClient, default_user_headers: dict[str, str]) -> None:
    response = await client.get(app.url_path_for("get_me"), headers=default_user_headers)

    assert response.status_code == status.HTTP_200_OK
