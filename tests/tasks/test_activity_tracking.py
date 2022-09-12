import pytest

from app.models import Project


@pytest.mark.xfail
def test_generating_activities(user, db):
    project = Project.manager(db).create(
        name="projjj",
        owner=user,
    )

    assert len(project.related_activities) == 1

    Project.manager(db).delete(project)
