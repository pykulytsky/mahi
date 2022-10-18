def test_global_error_handling(auth_client):
    res = auth_client.post("/tasks/9999")

    assert res.status_code == 404
