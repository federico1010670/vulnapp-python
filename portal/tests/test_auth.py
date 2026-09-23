from portal.routers.auth import generate_token_pair, hash_password, RESET_PASSWORD_TOKEN_TTL

TEST_USER = {"email": "daniel.okafor@aquilax.io", "password": "Tr0ub4dor&3xk"}


def test_hash_is_stable():
    assert hash_password(TEST_USER["password"]) == hash_password(TEST_USER["password"])


def test_reset_tokens_are_unique():
    first, _ = generate_token_pair(RESET_PASSWORD_TOKEN_TTL)
    second, _ = generate_token_pair(RESET_PASSWORD_TOKEN_TTL)
    assert first != second
