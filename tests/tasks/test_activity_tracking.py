from app.models import Project, Activity


def test_generating_activities(user, db):
    project = Project.manager(db).create(
        name="projjj",
        owner=user,
    )

    assert len(project.related_activities) == 1
