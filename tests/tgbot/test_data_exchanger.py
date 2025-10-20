import json
import logging
import pytest
from types import SimpleNamespace
from yarl import URL
from aioresponses import aioresponses

import tgbot.data_exchanger as m

RESOURCES_GET_LIST = [
    pytest.param(
        "CATEGORIES_URL",
        "http://categories/api/",
        m.get_categories,
        lambda uid, cat, headers: dict(headers=headers, user_id=uid),
        lambda uid, cat: {"tg_id": uid},
        id="get-categories",
    ),
    pytest.param(
        "TASKS_URL",
        "http://tasks/api/",
        m.list_tasks,
        lambda uid, cat, headers: dict(headers=headers, user_id=uid, category=cat),
        lambda uid, cat: {k: v for k, v in {"tg_id": uid, "category": cat}.items() if v is not None},
        id="list-tasks",
    ),
]

GET_LIST_CASES = [
    pytest.param(123, None, id="uid-only"),
    pytest.param(456, "work", id="uid-with-category"),
    pytest.param(None, None, id="uid-none"),
]


def _get_single_request(mocked):
    ((method, url), calls), = mocked.requests.items()
    return method, url, calls[0]


def _make_url(base_url: str, params: dict) -> str:
    return str(URL(base_url).with_query(params)) if params else base_url


RESOURCES_GET = [
    pytest.param("TASKS_URL", "http://tasks/api/", m.get_task, "task_id", id="get-task"),
    pytest.param("CATEGORIES_URL", "http://categories/api/", m.get_category, "category_id", id="get-category"),
]

RESOURCES_DELETE = [
    pytest.param("TASKS_URL", "http://tasks/api/", m.delete_task, "task_id", id="delete-task"),
    pytest.param("CATEGORIES_URL", "http://categories/api/", m.delete_category, "category_id", id="delete-category"),
]

RESOURCES_UPDATE = [
    pytest.param(
        "CATEGORIES_URL",
        "http://categories/api/",
        m.update_category,
        "category_id",
        lambda rid, body: dict(category_id=rid, updated_data=body),
        id="update-category",
    ),
    pytest.param(
        "TASKS_URL",
        "http://tasks/api/",
        m.update_task,
        "task_id",
        lambda rid, body: dict(data={**body, "task_id": rid}),
        id="update-task",
    ),
]

RESOURCES_POST = [
    pytest.param("TASKS_URL", "http://tasks/api/", m.add_task, id="add-task"),
    pytest.param("CATEGORIES_URL", "http://categories/api/", m.add_category, id="create-category"),
]


class TestGetResource:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("url_attr, base_url, func, id_kw", RESOURCES_GET)
    async def test_get_success(self, monkeypatch, url_attr, base_url, func, id_kw):
        monkeypatch.setattr(m, url_attr, base_url)
        rid = "123"
        url = f"{base_url}{rid}/"
        headers = {"Authorization": "Bearer token"}
        payload = {"id": 123, "ok": True}

        with aioresponses() as mocked:
            mocked.get(url, status=200, payload=payload)

            result = await func(headers=headers, **{id_kw: rid})

            assert result == {"status": 200, "json": payload}
            assert ("GET", URL(url)) in mocked.requests
            req_call = mocked.requests[("GET", URL(url))][0]
            assert req_call.kwargs["headers"] == headers

    @pytest.mark.asyncio
    @pytest.mark.parametrize("url_attr, base_url, func, id_kw", RESOURCES_GET)
    async def test_get_404(self, monkeypatch, url_attr, base_url, func, id_kw):
        monkeypatch.setattr(m, url_attr, base_url)
        rid = "404"
        url = f"{base_url}{rid}/"
        headers = {"X-Request-ID": "test-404"}
        payload = {"detail": "Not found"}

        with aioresponses() as mocked:
            mocked.get(url, status=404, payload=payload)

            result = await func(headers=headers, **{id_kw: rid})
            assert result == {"status": 404, "json": payload}


class TestDeleteResource:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("url_attr, base_url, func, id_kw", RESOURCES_DELETE)
    async def test_delete_success(self, monkeypatch, url_attr, base_url, func, id_kw):
        monkeypatch.setattr(m, url_attr, base_url)
        rid = "123"
        url = f"{base_url}{rid}/"
        headers = {"Authorization": "Bearer token"}

        with aioresponses() as mocked:
            mocked.delete(url, status=204)

            result = await func(headers=headers, **{id_kw: rid})
            assert result["status"] == 204
            assert ("DELETE", URL(url)) in mocked.requests
            req_call = mocked.requests[("DELETE", URL(url))][0]
            assert req_call.kwargs["headers"] == headers

    @pytest.mark.asyncio
    @pytest.mark.parametrize("url_attr, base_url, func, id_kw", RESOURCES_DELETE)
    async def test_delete_404(self, monkeypatch, url_attr, base_url, func, id_kw):
        monkeypatch.setattr(m, url_attr, base_url)
        rid = "404"
        url = f"{base_url}{rid}/"
        headers = {"X-Request-ID": "test-404"}

        with aioresponses() as mocked:
            mocked.delete(url, status=404)

            result = await func(headers=headers, **{id_kw: rid})
            assert result["status"] == 404


class TestUpdateResource:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("url_attr, base_url, func, id_kw, build_kwargs", RESOURCES_UPDATE)
    async def test_update_success(self, monkeypatch, url_attr, base_url, func, id_kw, build_kwargs):
        monkeypatch.setattr(m, url_attr, base_url)
        rid = "123"
        url = f"{base_url}{rid}/"
        headers = {"Authorization": "Bearer token"}
        body = {"name": "new-name"}

        with aioresponses() as mocked:
            mocked.patch(url, status=200)

            kwargs = dict(headers=headers, **build_kwargs(rid, body))
            result = await func(**kwargs)
            assert result["status"] == 200

            assert ("PATCH", URL(url)) in mocked.requests
            req_call = mocked.requests[("PATCH", URL(url))][0]
            assert req_call.kwargs["headers"] == headers
            expected_json = kwargs.get("updated_data", kwargs.get("data"))
            assert req_call.kwargs["json"] == expected_json

    @pytest.mark.asyncio
    @pytest.mark.parametrize("url_attr, base_url, func, id_kw, build_kwargs", RESOURCES_UPDATE)
    async def test_update_404(self, monkeypatch, url_attr, base_url, func, id_kw, build_kwargs):
        monkeypatch.setattr(m, url_attr, base_url)
        rid = "404"
        url = f"{base_url}{rid}/"
        headers = {"X-Request-ID": "test-404"}
        body = {"name": "not-exist"}

        with aioresponses() as mocked:
            mocked.patch(url, status=404)

            kwargs = dict(headers=headers, **build_kwargs(rid, body))
            result = await func(**kwargs)
            assert result["status"] == 404


class TestPostResources:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("url_attr, base_url, func", RESOURCES_POST)
    async def test_post_success(self, monkeypatch, url_attr, base_url, func):
        monkeypatch.setattr(m, url_attr, base_url)
        url = base_url
        headers = {"Authorization": "Bearer token"}
        data = {"title": "Do it"}

        with aioresponses() as mocked:
            mocked.post(url, status=201)

            result = await func(headers=headers, data=data)
            assert result["status"] == 201

            assert ("POST", URL(url)) in mocked.requests
            req_call = mocked.requests[("POST", URL(url))][0]
            assert req_call.kwargs["headers"] == headers
            assert req_call.kwargs["json"] == data

    @pytest.mark.asyncio
    @pytest.mark.parametrize("url_attr, base_url, func", RESOURCES_POST)
    async def test_post_bad_request(self, monkeypatch, url_attr, base_url, func):
        monkeypatch.setattr(m, url_attr, base_url)
        url = base_url
        headers = {"X-Request-ID": "test-400"}
        data = {"invalid": True}

        with aioresponses() as mocked:
            mocked.post(url, status=400)

            result = await func(headers=headers, data=data)
            assert result["status"] == 400


class TestGetListResources:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("url_attr, base_url, func, build_kwargs, build_expected_params", RESOURCES_GET_LIST)
    @pytest.mark.parametrize("user_id, category", GET_LIST_CASES)
    async def test_get_list_success(self, monkeypatch, url_attr, base_url, func, build_kwargs, build_expected_params,
                                    user_id, category):
        if func is m.get_categories and user_id is None:
            pytest.skip("get_categories требует непустой user_id")

        monkeypatch.setattr(m, url_attr, base_url)
        headers = {"Authorization": "Bearer token"}
        payload = {"items": [1, 2, 3]}
        expected_params = build_expected_params(user_id, category)
        url_q = _make_url(base_url, expected_params)

        with aioresponses() as mocked:
            mocked.get(url_q, status=200, payload=payload)

            kwargs = build_kwargs(user_id, category, headers)
            result = await func(**kwargs)

            assert result == {"status": 200, "json": payload}

            method, req_url, req_call = _get_single_request(mocked)
            assert method == "GET"
            assert str(req_url).split("?")[0] == base_url.rstrip("?")
            assert req_call.kwargs["headers"] == headers
            assert req_call.kwargs["params"] == expected_params

    @pytest.mark.asyncio
    @pytest.mark.parametrize("url_attr, base_url, func, build_kwargs, build_expected_params", RESOURCES_GET_LIST)
    @pytest.mark.parametrize("user_id, category", GET_LIST_CASES)
    async def test_get_list_404(self, monkeypatch, url_attr, base_url, func, build_kwargs, build_expected_params,
                                user_id, category):
        if func is m.get_categories and user_id is None:
            pytest.skip("get_categories требует непустой user_id")

        monkeypatch.setattr(m, url_attr, base_url)
        headers = {"X-Request-ID": "test-404"}
        payload = {"detail": "Not found"}
        expected_params = build_expected_params(user_id, category)
        url_q = _make_url(base_url, expected_params)

        with aioresponses() as mocked:
            mocked.get(url_q, status=404, payload=payload)

            kwargs = build_kwargs(user_id, category, headers)
            result = await func(**kwargs)
            assert result == {"status": 404, "json": payload}

            method, req_url, req_call = _get_single_request(mocked)
            assert method == "GET"
            assert str(req_url).split("?")[0] == base_url.rstrip("?")
            assert req_call.kwargs["params"] == expected_params


class TestVerifyAccessToken:
    @pytest.mark.asyncio
    async def test_verify_success(self, monkeypatch):
        base_url = "http://auth/api/token/verify/"
        monkeypatch.setattr(m, "ACCESS_TOKEN_VERIFY_URL", base_url)

        token = "abc123"

        with aioresponses() as mocked:
            mocked.post(base_url, status=200)

            result = await m.verify_access_token(token)
            assert result["status"] == 200

            assert ("POST", URL(base_url)) in mocked.requests
            req_call = mocked.requests[("POST", URL(base_url))][0]
            assert req_call.kwargs["json"] == {"token": token}

    @pytest.mark.asyncio
    async def test_verify_invalid(self, monkeypatch):
        base_url = "http://auth/api/token/verify/"
        monkeypatch.setattr(m, "ACCESS_TOKEN_VERIFY_URL", base_url)

        token = "bad-token"

        with aioresponses() as mocked:
            mocked.post(base_url, status=401)

            result = await m.verify_access_token(token)
            assert result["status"] == 401


class TestRequestNewAccessToken:
    @pytest.mark.asyncio
    async def test_refresh_success(self, monkeypatch):
        base_url = "http://auth/api/token/refresh/"
        monkeypatch.setattr(m, "ACCESS_TOKEN_REFRESH_URL", base_url)

        refresh = "refresh-xyz"
        payload = {"access": "new-access-token"}

        with aioresponses() as mocked:
            mocked.post(base_url, status=200, payload=payload)

            result = await m.request_new_access_token(refresh)
            assert result == {"status": 200, "json": payload}

            assert ("POST", URL(base_url)) in mocked.requests
            req_call = mocked.requests[("POST", URL(base_url))][0]
            assert req_call.kwargs["json"] == {"refresh": refresh}

    @pytest.mark.asyncio
    async def test_refresh_invalid(self, monkeypatch):
        base_url = "http://auth/api/token/refresh/"
        monkeypatch.setattr(m, "ACCESS_TOKEN_REFRESH_URL", base_url)

        refresh = "bad-refresh"
        payload = {"detail": "Token is invalid or expired"}

        with aioresponses() as mocked:
            mocked.post(base_url, status=401, payload=payload)

            result = await m.request_new_access_token(refresh)
            assert result == {"status": 401, "json": payload}


class TestAuthUser:
    @pytest.mark.asyncio
    async def test_auth_success(self, monkeypatch):
        base_url = "http://auth/api/token/"
        monkeypatch.setattr(m, "API_TOKENS_URL", base_url)

        username = "john"
        password = "secret"
        payload = {"access": "acc", "refresh": "ref"}
        expected_headers = {"Content-Type": "application/json"}
        expected_data = json.dumps({"username": username, "password": password})

        with aioresponses() as mocked:
            mocked.post(base_url, status=200, payload=payload)

            result = await m.auth_user(username, password)
            assert result == {"status": 200, "json": payload}

            assert ("POST", URL(base_url)) in mocked.requests
            req_call = mocked.requests[("POST", URL(base_url))][0]
            assert req_call.kwargs["headers"] == expected_headers
            assert req_call.kwargs["data"] == expected_data

    @pytest.mark.asyncio
    async def test_auth_invalid_credentials(self, monkeypatch):
        base_url = "http://auth/api/token/"
        monkeypatch.setattr(m, "API_TOKENS_URL", base_url)

        username = "john"
        password = "wrong"
        payload = {"detail": "No active account found"}

        with aioresponses() as mocked:
            mocked.post(base_url, status=401, payload=payload)

            result = await m.auth_user(username, password)
            assert result == {"status": 401, "json": payload}
