import pytest

from app.models import Project


@pytest.mark.xfail
def test_generating_activities(user, db):
    project = Project.manager().create(
        name="projjj",
        owner=user,
    )

    assert len(project.related_activities) == 1

    Project.manager().delete(project)
