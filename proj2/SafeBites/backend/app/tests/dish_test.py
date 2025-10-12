import pytest
from bson import ObjectId

@pytest.mark.asyncio
async def test_create_list_update_delete_dish(client):
    # create restaurant for dish reference
    r_rest = await client.post("/restaurants/", json={"name":"Test R", "address":"X", "cuisine":["italian"]})
    assert r_rest.status_code == 201
    rest = r_rest.json()
    # create dish
    r = await client.post("/dishes/", json={
        "name":"Pasta Primavera",
        "description":"Veg pasta",
        "ingredients":["wheat","tomato"],
        "restaurant":"Test R",
        "price":9.5,
        "explicit_allergens":["wheat"]
    })
    assert r.status_code == 201
    dish = r.json()
    dish_id = dish["_id"]
    # get dish
    g = await client.get(f"/dishes/{dish_id}")
    assert g.status_code == 200
    assert g.json()["name"] == "Pasta Primavera"
    # list dishes by restaurant
    ls = await client.get("/dishes/", params={"restaurant":"Test R"})
    assert ls.status_code == 200
    assert any(d["name"]=="Pasta Primavera" for d in ls.json())
    # update dish
    up = await client.put(f"/dishes/{dish_id}", json={"price":10.0, "availability": False})
    assert up.status_code == 200
    assert up.json()["price"] == 10.0
    assert up.json()["availability"] is False
    # delete dish
    dd = await client.delete(f"/dishes/{dish_id}")
    assert dd.status_code == 200
