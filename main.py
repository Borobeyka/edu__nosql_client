import json
import random
import time
from typing import Optional

import matplotlib.pyplot as plt
import requests
from faker import Faker
from pydantic import BaseModel


class Endpoint(BaseModel):
    route: str = "/"
    method: str = "get"
    gen_params: Optional[dict] = None
    params: dict = {}
    saving_fields: list = []

    __host = "http://localhost:80"
    __methods = {
        "post": requests.post,
        "put": requests.put,
        "delete": requests.delete,
        "get": requests.get,
        "patch": requests.patch,
    }

    @property
    def url(self) -> str:
        return self.__host + self.route

    def __repr__(self) -> str:
        return f"{self.method.upper()} {self.route}"

    def __str__(self) -> str:
        return f"{self.method.upper()}\n{self.route}"

    def run(self) -> str:
        if not (method := self.__methods.get(self.method)):
            return f"{self.__repr__()} : Method not allowed"
        start_time = time.time()
        response = method(
            self.url,
            json.dumps(self.params),
            headers={"Content-Type": "application/json"},
        ).json()
        end_time = time.time()
        data = {}
        for field in self.saving_fields:
            data[field] = response.get(field)
        return (
            f"{self.__repr__()} : {response}",
            (end_time - start_time) * 1000,
            data
        )


def generate_data(data_type):
    if isinstance(data_type, str):
        if data_type == "ids_users":
            return random.choice(ids["users"])
        elif data_type == "ids_items":
            return random.choice(ids["items"])
    fake = Faker()
    match data_type.__name__:
        case "int":
            return fake.random_number(digits=3)
        case "str":
            return " ".join(fake.words(nb=2))
        case "float":
            return fake.random_number(digits=6, fix_len=True) / 100
        case _:
            return "Unsupported data type"


def plot_bar_chart(x_data, y_data, title, x_label, y_label):
    plt.bar(x_data, y_data)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True)
    plt.show()


stats = {}
ids = {"items": [None], "users": [None]}
endpoints = [
    Endpoint(
        route="/items",
        method="post",
        gen_params={"title": str, "price": float},
        saving_fields=["item_id"],
    ),
    Endpoint(route="/items", method="get"),
    Endpoint(
        route="/users",
        method="post",
        gen_params={"username": str},
        saving_fields=["user_id"],
    ),
    Endpoint(route="/users", method="get", gen_params={"username": str}),
    Endpoint(
        route="/orders",
        method="post",
        gen_params={"user_id": "ids_users", "item_id": "ids_items"},
    ),
    Endpoint(route="/orders", method="get"),
]

MAX_QUERIES = 40

for i in range(1, MAX_QUERIES + 1):
    endpoint = random.choice(endpoints)
    if endpoint.gen_params:
        for param, type in endpoint.gen_params.items():
            endpoint.params[param] = generate_data(type)
    result, elapsed, data = endpoint.run()
    try:
        stats[str(endpoint)] += elapsed
    except KeyError:
        stats[str(endpoint)] = elapsed
    if data:
        if "item_id" in data.keys():
            ids["items"].append(data["item_id"])
        elif "user_id" in data.keys():
            ids["users"].append(data["user_id"])
    # print(f"{i}: {result}: {data}")
plot_bar_chart(
    stats.keys(),
    stats.values(),
    title="Статистика",
    x_label="Запросы",
    y_label="Суммарное время выполнения запроса",
)
