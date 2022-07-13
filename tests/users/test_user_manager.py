from app.models import User


def test_create_user(db):
    user = User.manager(db).create(
        email="test@gfff.d",
        first_name="sss",
        last_name="ggg",
        password="12345"
    )

    assert user in User.manager(db).all()

    User.manager(db).delete(user)


def test_password_is_hashed(db):
    user = User.manager(db).create(
        email="test@gfff.d",
        first_name="sss",
        last_name="ggg",
        password="12345"
    )

    assert user.password != "12345"

    User.manager(db).delete(user)
