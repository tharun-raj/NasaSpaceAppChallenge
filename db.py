import psycopg2
import bcrypt
import json
import os

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

        # Labels table
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

        # Forum Posts table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                topic TEXT,
                content TEXT NOT NULL,
                coordinates JSONB ,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Forum Comments table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL,
                comment TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        #user table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        print("✅ Tables created.")
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

        query = "DELETE FROM public.labels WHERE id = %s "
        values = [id]

        if user_id is not None:
            query += "AND user_id = %s "
            values.append(user_id)
        if celestial_object is not None:
            query += "AND celestial_object = %s"
            values.append(celestial_object)

        cur.execute(query,tuple(values))
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
        raise e
    finally:
        cur.close()
        conn.close()

#forum

def insert_post(user_id: int, title: str, topic: str, content: str, coordinates: list[float]):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        import json

        cur.execute(
            "INSERT INTO posts (user_id, title, topic, content, coordinates) VALUES (%s, %s, %s, %s, %s)",
            (user_id, title, topic, content, json.dumps(coordinates))
        )

        conn.commit()
        print("✅ Post inserted.")
    except Exception as e:
        print("❌ Failed to insert post:", e)
        raise e
    finally:
        cur.close()
        conn.close()

def insert_comment(post_id: int, user_id: int, comment: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO comments (post_id, user_id, comment) VALUES (%s, %s, %s)",
            (post_id, user_id, comment)
        )
        conn.commit()
        print("✅ Comment inserted.")
    except Exception as e:
        print("❌ Failed to insert comment:", e)
        raise e
    finally:
        cur.close()
        conn.close()

def get_posts_with_comments(post_id: int):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Fetch the main post
        cur.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
        post = cur.fetchone()

        if not post:
            return None

        # Fetch comments for the post
        cur.execute("SELECT * FROM comments WHERE post_id = %s ORDER BY created_at", (post_id,))
        comments = cur.fetchall()

        return {
            "post": {
                "id": post[0],
                "user_id": post[1],
                "title":post[2],
                "content": post[3],
                "topic": post[4],
                "coordinates": post[5],
                "created_at": post[6]
            },
            "comments": [
                {
                    "id": c[0],
                    "post_id": c[1],
                    "user_id": c[2],
                    "comment": c[3],
                    "created_at": c[4]
                } for c in comments
            ]
        }
    except Exception as e:
        print("❌ Failed to fetch thread:", e)
        raise e
    finally:
        cur.close()
        conn.close()

#user portal

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(username: str, email: str, password: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        hashed_pw = hash_password(password)
        cur.execute("""
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
            RETURNING id;
        """, (username, email, hashed_pw))
        conn.commit()
        return cur.fetchone()[0]
    except Exception as e:
        print("❌ Registration error:", e)
        raise
    finally:
        cur.close()
        conn.close()

def authenticate_user(username: str, password: str) -> int | None:
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Fetch id and password hash
        cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

        if not user:
            return None  # No such user

        user_id, hashed_password = user

        if check_password(password, hashed_password):
            return user_id
        else:
            return None  # Password mismatch

    except Exception as e:
        print("❌ Login error:", e)
        raise
    finally:
        cur.close()
        conn.close()
