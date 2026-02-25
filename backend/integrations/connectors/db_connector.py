from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///../../data/test.db")


def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                status TEXT
            )
        """))
        conn.execute(text("""
            INSERT INTO subscriptions (user_id, status)
            VALUES (123, 'ACTIVE')
        """))


def get_user_subscriptions(user_id):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM subscriptions WHERE user_id = :uid"),
            {"uid": user_id}
        )
        return [dict(row) for row in result]