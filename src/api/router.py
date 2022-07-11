from typing import (Any, Callable, Dict, List, Optional, Sequence, Set, Type,
                    Union)

from fastapi import APIRouter, Depends, HTTPException, params
from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi.encoders import DictIntStrAny, SetIntStr
from fastapi.routing import APIRoute
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute

from src.api.deps import get_db, get_current_active_user
from src import models
from src.core.exceptions import ImproperlyConfigured, ObjectDoesNotExists


class BaseCrudRouter(APIRouter):
    """Base router implements methods for create and remove api routes."""

    model = None
    create_schema = None
    get_schema = None

    def __init__(
        self,
        model,
        get_schema: BaseModel,
        create_schema: BaseModel,
        update_schema: BaseModel = None,
        db: Session = Depends(get_db),
        prefix: Optional[str] = None,
        tags: Optional[List] = list(),
        *args,
        **kwargs,
    ) -> None:
        if not hasattr(model, "manager"):
            raise AttributeError(
                f"Model {model.__name__} not suported, \
                    model must have a 'manager' field."
            )

        self.model = model

        self.get_schema = get_schema
        self.create_schema = create_schema
        self.update_schema = update_schema

        self.prefix = prefix
        if not prefix:
            self.prefix = "/" + self.model.__name__.lower()
        self.tags = tags

        if not all([self.model, self.create_schema, self.get_schema]):
            raise ImproperlyConfigured(
                "Please redifine fields model,\
                create_schema, get_schema in your subclass"
            )

        super().__init__(prefix=prefix, tags=tags, *args, **kwargs)

    def get(self, path, *args, **kwargs):
        self.remove_api_route(path, ["GET"])
        return super().get(path, *args, **kwargs)

    def post(self, path, *args, **kwargs):
        self.remove_api_route(path, ["POST"])
        return super().post(path, *args, **kwargs)

    def put(self, path, *args, **kwargs):
        self.remove_api_route(path, ["PUT"])
        return super().put(path, *args, **kwargs)

    def delete(self, path, *args, **kwargs):
        self.remove_api_route(path, ["DELETE"])
        return super().delete(path, *args, **kwargs)

    def api_route(self, path: str, *args, **kwargs):
        methods = kwargs["methods"] if "methods" in kwargs else ["GET"]
        self.remove_api_route(path, methods)
        return super().api_route(path, *args, **kwargs)

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        response_model: Optional[Type[Any]] = None,
        status_code: Optional[int] = None,
        response_description: Optional[str] = None,
        summary: Optional[str] = None,
        tags: Optional[List[str]] = None,
        dependencies: Optional[Sequence[params.Depends]] = None,
        description: Optional[str] = None,
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        methods: Optional[Union[Set[str], List[str]]] = None,
        operation_id: Optional[str] = None,
        response_model_include: Optional[
            Union[SetIntStr, DictIntStrAny]
        ] = None,  # noqa
        response_model_exclude: Optional[
            Union[SetIntStr, DictIntStrAny]
        ] = None,  # noqa
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False,
        include_in_schema: bool = True,
        response_class: Union[Type[Response], DefaultPlaceholder] = Default(
            JSONResponse
        ),
        name: Optional[str] = None,
        route_class_override: Optional[Type[APIRoute]] = None,
        callbacks: Optional[List[BaseRoute]] = None,
    ) -> None:
        if path in self.routes:
            self.remove_api_route(path, methods)

        if not summary:
            _endpoint_name = endpoint.__name__.strip("_").replace("_", " ").capitalize()
            if self.model.__name__.lower() in _endpoint_name:
                summary = _endpoint_name
            else:
                summary = _endpoint_name + " " + self.model.__name__

        if not response_description:
            response_description = f"{self.model.__name__} Successful Response"

        if not status_code:
            status_code = 200
            if methods:
                if len(methods) == 1 and methods[0].upper() == "POST":
                    status_code = 201

        return super().add_api_route(
            path,
            endpoint,
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            dependencies=dependencies,
            summary=summary,
            description=description,
            response_description=response_description,
            responses=responses,
            deprecated=deprecated,
            methods=methods,
            operation_id=operation_id,
            response_model_include=response_model_include,
            response_model_exclude=response_model_exclude,
            response_model_by_alias=response_model_by_alias,
            response_model_exclude_unset=response_model_exclude_unset,
            response_model_exclude_defaults=response_model_exclude_defaults,
            response_model_exclude_none=response_model_exclude_none,
            include_in_schema=include_in_schema,
            response_class=response_class,
            name=name,
            route_class_override=route_class_override,
            callbacks=callbacks,
        )

    def remove_api_route(self, path: str, methods: List[str]):
        methods = set(methods)

        for r in self.routes:
            if path in r.path and r.methods == methods:
                self.routes.remove(r)

    def get_routes(self) -> list:
        return self.routes


class CrudRouter(BaseCrudRouter):
    """Base router that implements basic CRUD operations
    (.get(), .get_all(), .create(), .delete())"""

    def __init__(
        self,
        model,
        get_schema: BaseModel,
        create_schema: BaseModel,
        update_schema: BaseModel = None,
        db: Session = Depends(get_db),
        prefix: Optional[str] = None,
        tags: Optional[List] = [],
        add_create_route: bool = True,
        override_routes: bool = False,
        *args,
        **kwargs,
    ) -> None:
        if not override_routes:
            super().__init__(
                model=model,
                get_schema=get_schema,
                create_schema=create_schema,
                update_schema=update_schema,
                prefix=prefix,
                tags=tags,
                *args,
                **kwargs,
            )

            super().add_api_route(
                "/",
                self._get_all,
                response_model=List[self.get_schema],
                dependencies=[Depends(get_db)],
                summary=f"Get all {self.model.__name__}`s",
            )

            if add_create_route:
                super().add_api_route(
                    "/",
                    self._create(),
                    methods=["POST"],
                    response_model=self.get_schema,
                    dependencies=[Depends(get_db)],
                    summary=f"Create {self.model.__name__}",
                    status_code=201,
                )
            super().add_api_route(
                "/{pk}",
                self._get(),
                methods=["GET"],
                response_model=self.get_schema,
                dependencies=[Depends(get_db)],
                summary=f"Get {self.model.__name__}",
            )
            super().add_api_route(
                "/{pk}",
                self._update(),
                methods=["PATCH"],
                response_model=self.get_schema,
                dependencies=[Depends(get_db)],
                summary=f"Patch {self.model.__name__}",
            )
            super().add_api_route(
                "/{pk}",
                self._delete(),
                methods=["DELETE"],
                response_model=self.get_schema,
                dependencies=[Depends(get_db)],
                summary=f"Delete {self.model.__name__}",
            )

    async def _get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created",
        desc: bool = False,
        db: Session = Depends(get_db),
    ) -> Callable:
        @self.get("/", response_model=List[self.get_schema])
        async def _get_all(
            skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
        ):
            return self.model.manager(db).all(skip, limit, order_by, desc)

        return await _get_all(skip, limit, db)

    def _create(self) -> Callable:
        async def route(
            instance_create_schema: self.create_schema, db: Session = Depends(get_db)
        ):
            return self.model.manager(db).create(instance_create_schema)

        return route

    def _get(self) -> Callable:
        async def route(pk: int, db: Session = Depends(get_db)):
            try:
                return self.model.manager(db).get(pk=pk)
            except ObjectDoesNotExists:
                raise HTTPException(
                    status_code=400, detail=f"{self.model.__name__} does not exists"
                )

        return route

    def _update(self) -> Callable:
        async def route(
            pk, update_schema: self.update_schema, db: Session = Depends(get_db)
        ):
            return self.model.manager(db).update(
                pk, **update_schema.dict(exclude_unset=True)
            )

        return route

    def _delete(self) -> Callable:
        async def route(pk, db: Session = Depends(get_db)):
            return self.model.manager(db).delete(self.model.manager(db).get(pk=pk))

        return route


class AuthenticatedCrudRouter(CrudRouter):
    """Crud router with authentication"""

    def __init__(
        self,
        model,
        get_schema: BaseModel,
        create_schema: BaseModel,
        update_schema: BaseModel = None,
        db: Session = Depends(get_db),
        prefix: Optional[str] = None,
        tags: Optional[List] = [],
        add_create_route: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            model,
            get_schema,
            create_schema,
            update_schema=update_schema,
            db=db,
            prefix=prefix,
            tags=tags,
            add_create_route=add_create_route,
            *args,
            **kwargs,
        )

        super().add_api_route(
            "/",
            self._create(),
            methods=["POST"],
            response_model=self.get_schema,
            dependencies=[Depends(get_db)],
            summary=f"Create {self.model.__name__}",
            status_code=201,
        )

    def _create(self) -> Callable:
        async def route(
            instance_create_schema: self.create_schema,
            db: Session = Depends(get_db),
            user: models.User = Depends(get_current_active_user)
        ):
            return self.model.manager(db).create(instance_create_schema, user=user)

        return route
