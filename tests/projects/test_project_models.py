import jwt
import pytest
from fastapi import HTTPException

from app.core.config import settings


def test_generate_project_invitation_code(project_manager, project):
    code = project_manager.generate_invitaion_code(id=project.id)

    assert isinstance(code, bytes)


def test_validate_invitation_code(project_manager, project):
    code = project_manager.generate_invitaion_code(id=project.id)

    validated_project = project_manager.validate_invitation_code(code.decode("utf-8"))

    assert validated_project is not None
    assert project.id == validated_project.id


def test_generated_code_contains_project_id(project_manager, project):
    code = project_manager.generate_invitaion_code(id=project.id)

    payload = jwt.decode(code, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert int(payload["sub"]) == project.id


def test_test_validate_wrong_code(project_manager):
    with pytest.raises(HTTPException):
        project_manager.validate_invitation_code("WRONG CODE")


@pytest.mark.freeze_time("2022-02-02")
def test_validate_expired_code(project_manager, project, freezer):
    code = project_manager.generate_invitaion_code(id=project.id)

    freezer.move_to("2022-02-04")

    with pytest.raises(HTTPException):
        project_manager.validate_invitation_code(code.decode("utf-8"))
