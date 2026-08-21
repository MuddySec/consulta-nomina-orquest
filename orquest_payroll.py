import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv


BASE_URL = "https://wfm.mcdonalds.es/importer"
BUSINESS_ID = "MCDONALDS_ES"


def resource_path(relative_path: str) -> Path:
    """
    Devuelve la ruta correcta tanto en desarrollo como dentro de PyInstaller.
    """
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path

    return Path(__file__).resolve().parent / relative_path


load_dotenv(resource_path(".env"))

def get_orquest_api_key():
    try:
        import streamlit as st
        if "ORQUEST_API_KEY" in st.secrets:
            return st.secrets["ORQUEST_API_KEY"]
    except Exception:
        pass

    return os.getenv("ORQUEST_API_KEY")

def get_headers():
    api_key = get_orquest_api_key()

    if not api_key:
        raise RuntimeError(
            "No se ha encontrado ORQUEST_API_KEY. "
            "Configúrala en .env local o en Secrets de Streamlit Cloud."
        )

    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }


def get_restaurants():
    url = f"{BASE_URL}/api/v2/businesses/{BUSINESS_ID}/services"

    response = requests.get(url, headers=get_headers(), timeout=30)

    if response.status_code >= 400:
        raise RuntimeError(
            f"Error Orquest HTTP {response.status_code}: {response.text}"
        )

    data = response.json() if response.content else []

    if not isinstance(data, list):
        raise RuntimeError("La respuesta de restaurantes no tiene el formato esperado.")

    restaurants = []

    for restaurant in data:
        restaurant_id = restaurant.get("id")
        restaurant_name = restaurant.get("name", "Sin nombre")

        if restaurant_id:
            restaurants.append({
                "id": restaurant_id,
                "name": restaurant_name,
                "label": f"{restaurant_name} ({restaurant_id})",
            })

    return restaurants


def get_payroll(service_id: str, from_date: str, to_date: str):
    url = (
        f"{BASE_URL}/api/v1/business/{BUSINESS_ID}"
        f"/service/{service_id}"
        f"/payroll/from/{from_date}/to/{to_date}"
    )

    response = requests.get(url, headers=get_headers(), timeout=30)

    if response.status_code >= 400:
        raise RuntimeError(
            f"Error Orquest HTTP {response.status_code}: {response.text}"
        )

    return response.json() if response.content else []


def get_employees(service_id: str):
    url = (
        f"{BASE_URL}/api/v2/businesses/{BUSINESS_ID}"
        f"/services/{service_id}/employees"
    )

    response = requests.get(url, headers=get_headers(), timeout=30)

    if response.status_code >= 400:
        raise RuntimeError(
            f"Error Orquest HTTP {response.status_code}: {response.text}"
        )

    return response.json() if response.content else []


def enrich_payroll_with_employees(payroll_data: list, employees_data: list):
    employees_by_id = {
        employee["employeeId"]: employee
        for employee in employees_data
        if employee.get("employeeId")
    }

    enriched_payroll = []

    for payroll_item in payroll_data:
        employee_id = payroll_item.get("employeeId")
        employee = employees_by_id.get(employee_id)

        enriched_item = {
            "employeeId": employee_id,
            "name": employee.get("name") if employee else None,
            "surname": employee.get("surname") if employee else None,
        }

        for key, value in payroll_item.items():
            if key != "employeeId":
                enriched_item[key] = value

        enriched_payroll.append(enriched_item)

    return enriched_payroll


def get_enriched_payroll(service_id: str, from_date: str, to_date: str):
    payroll_data = get_payroll(service_id, from_date, to_date)
    employees_data = get_employees(service_id)

    return enrich_payroll_with_employees(payroll_data, employees_data)
