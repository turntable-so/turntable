from functools import reduce
from api.serializers import ColumnSerializer
from app.models import Column
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.core.cache import caches
from rest_framework.decorators import action
from django.views.decorators.cache import cache_page
from math import ceil
from django.utils.decorators import method_decorator

from django.db.models import Count, Q

cache = caches["default"]


class ColumnPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "total_pages": ceil(self.page.paginator.count / self.page_size),
                "results": data,
            }
        )


class ColumnViewSet(viewsets.ModelViewSet):
    queryset = Column.objects.all()
    pagination_class = ColumnPagination

    @method_decorator(cache_page(60))  # Cache the response for 60 seconds
    def list(self, request):
        query = request.query_params.get("q", None)
        workspace = request.user.current_workspace()
        if not workspace:
            return Response(
                {"detail": "Workspace not found."}, status=status.HTTP_403_FORBIDDEN
            )

        base_queryset = Column.objects.filter(asset__workspace=workspace).order_by(
            "name"
        )

        if query and len(query) > 0:
            filtered_columns = base_queryset.filter(name__icontains=query)
        else:
            filtered_columns = base_queryset

        page = self.paginate_queryset(filtered_columns)
        if page is not None:
            serializer = ColumnSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        print(len(page), flush=True)
        serializer = ColumnSerializer(
            filtered_columns, many=True, context={"request": request}
        )
        return Response(serializer.data)
