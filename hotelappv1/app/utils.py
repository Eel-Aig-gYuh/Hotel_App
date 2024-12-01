from app import dao, app
import csv
import os


def export():
    products = dao.read_hotel()
    p = os.path.join(app.root_path, "data/Hotel.csv")

    with open(p, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "description", "locations"])
        writer.writeheader()
        for pro in products:
            writer.writerow(pro)

    return p
