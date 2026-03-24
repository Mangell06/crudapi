from django.contrib.auth import authenticate as django_authenticate
from ninja.security import HttpBasicAuth, HttpBearer
from datetime import date
from typing import List, Optional
from ninja import NinjaAPI, Schema
from django.shortcuts import get_object_or_404
from employees.models import Employee, Usuari
import secrets


api = NinjaAPI()

class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        user = django_authenticate(username=username, password=password)
        if user:
            token = secrets.token_hex(16)
            user.auth_token = token
            user.save()
            return token
        return None

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            user = Usuari.objects.get(auth_token=token)
            return user
        except Usuari.DoesNotExist:
            return None

# Serializers
class EmployeeIn(Schema):
    first_name: str
    last_name: str
    department_id: int = None
    birthdate: date = None


class EmployeeOut(Schema):
    id: int
    first_name: str
    last_name: str
    department_id: int = None
    birthdate: Optional[date] = None


# Apis
@api.get("/token", auth=BasicAuth())
@api.get("/token/", auth=BasicAuth())
def obtenir_token(request):
    return {"token": request.auth}

@api.post("/employees", auth=AuthBearer())
def create_employee(request, payload: EmployeeIn):
    employee = Employee.objects.create(**payload.dict())
    return {"id": employee.id}


@api.get("/employee/{employee_id}", response=EmployeeOut, auth=AuthBearer())
def get_employee(request, employee_id: int):
    employee = get_object_or_404(Employee, id=employee_id)
    return employee


@api.get("/employees", response=List[EmployeeOut], auth=AuthBearer())
def list_employees(request):
    qs = Employee.objects.all()
    return qs


@api.put("/employee/{employee_id}", auth=AuthBearer())
def update_employee(request, employee_id: int, payload: EmployeeIn):
    employee = get_object_or_404(Employee, id=employee_id)
    for attr, value in payload.dict().items():
        setattr(employee, attr, value)
    employee.save()
    return {"success": True}


@api.delete("/employee/{employee_id}", auth=AuthBearer())
def delete_employee(request, employee_id: int):
    employee = get_object_or_404(Employee, id=employee_id)
    employee.delete()
    return {"success": True}