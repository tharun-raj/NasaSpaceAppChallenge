import psycopg2
import json

DB_CONFIG = {
    "dbname": "nasa_app",
    "user": "nasa_user",
    "password": "Root123",  # replace with actual password
    "host": "localhost",
    "port": "5432"
}

def create_table():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS labels (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                celestial_object TEXT NOT NULL,
                title TEXT,
                description TEXT,
                coordinates JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        print("✅ Table created.")
    except Exception as e:
        print("❌ Table creation failed:", e)
    finally:
        cur.close()
        conn.close()

def insert_coordinates(user_id: int, celestial_object: str, title: str, description: str, coordinates: list[float]):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO public.labels (user_id, celestial_object, title, description, coordinates) VALUES (%s, %s, %s, %s, %s)",
            (user_id, celestial_object, title, description, json.dumps(coordinates))
        )
        conn.commit()
        print("✅ Coordinates inserted successfully.")
    except Exception as e:
        print("❌ Failed to insert coordinates:", e)
        raise e
    finally:
        cur.close()
        conn.close()


def get_coordinates(user_id: int,id: int,title: str,celestial_object: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("SELECT * FROM public.labels WHERE id = %s AND title = %s AND user_id = %s AND celestial_object = %s",(id,title,user_id,celestial_object))
        rows = cur.fetchall()

        results = []
        
        for row in rows:
            print("Row:", row, flush=True)
            print("Length:", len(row), flush=True)
            results.append({
                "id" : row[0],
                "user_id": row[1],
                "celestial_object": row[2],
                "title": row[3],
                "description": row[4],
                "coordinates": row[5],
                # "created_at" : row[6]
            })

        return results
    except Exception as e:
        raise e
    finally:
        cur.close()
        conn.close()


def delete_coordinates(id: int,user_id: int,celestial_object: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("DELETE FROM public.labels WHERE id = %s AND user_id = %s AND celestial_object = %s",(id,user_id,celestial_object))
        conn.commit()
    
        return cur.rowcount > 0
    except Exception as e:
        raise e
    finally:
        cur.close()
        conn.close()

def update_coordinates(label_id: int, user_id: int, celestial_object: str, title: str, description: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        updates = []
        values = []

        if title:
            updates.append("title = %s")
            values.append(title)
        if description:
            updates.append("description = %s")
            values.append(description)

        if not updates:
            raise ValueError("No fields provided to update.")

        values.extend([label_id, user_id, celestial_object])

        query = f"""
            UPDATE public.labels
            SET {', '.join(updates)}
            WHERE id = %s AND user_id = %s AND celestial_object = %s
        """

        cur.execute(query, values)
        conn.commit()

        return cur.rowcount > 0  # True if a row was updated

    except Exception as e:
        raise e
    finally:
        cur.close()
        conn.close()
