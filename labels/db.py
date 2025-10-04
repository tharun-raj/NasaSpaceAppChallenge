import psycopg2
import json

DB_CONFIG = {
    "dbname": "nasa_app",
    "user": "nasa_user",
    "password": "Root123",
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

        query = "SELECT id, user_id, celestial_object, title, description, coordinates, created_at,updated_at FROM public.labels WHERE user_id = %s"
        values = [user_id]

        if id is not None:
            query += " AND id = %s"
            values.append(id)
        if title is not None:
            query += " AND title = %s"
            values.append(title)
        if celestial_object is not None:
            query += " AND celestial_object = %s"
            values.append(celestial_object)

        cur.execute(query, tuple(values))
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
                "created_at" : row[6],
                "updated_at": row[7]
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

def update_coordinates(label_id: int, title: str, description: str):
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

        # Always update the updated_at timestamp
        updates.append("updated_at = CURRENT_TIMESTAMP")

        if not updates:
            raise ValueError("No fields provided to update.")

        # Add WHERE clause values
        values.extend([label_id])

        query = f"""
            UPDATE public.labels
            SET {', '.join(updates)}
            WHERE id = %s
        """

        cur.execute(query, values)
        conn.commit()

        return cur.rowcount > 0

    except Exception as e:
        print("❌ SQL Error in update_coordinates:", e, flush=True)
        raise e
    finally:
        cur.close()
        conn.close()
