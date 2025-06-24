import psycopg2
import bcrypt 
from datetime import datetime   
import calendar

class UserConnection():
    def __init__(self):
        try:
            self.conn = psycopg2.connect(dbname="untilwefindyou", user="atziripg", password="1234", host="localhost", port="5432")
        except psycopg2.OperationalError as err:
            print(err)

    def create_user(self, data):
        if not self.conn:
            raise Exception("No database connection.")
        try: 
            hashed_pw = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt())
            data["password"] = hashed_pw.decode("utf-8")

            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO "users"(name, email, role, password_hash) 
                    VALUES 
                    (%(name)s, %(email)s, %(role)s, %(password)s)
                    returning id;"""
                    , data)
                user_id = cur.fetchone()[0]
                self.conn.commit()
                return user_id
        except (Exception, psycopg2.DatabaseError) as e:
            self.conn.rollback()
            print(e)
            return None
    
    def login_ong(self, email, password):
        if not self.conn:
            raise Exception("No database connection.")

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, email, password_hash 
                FROM users 
                WHERE email = %s AND role = 'ong'
            """, (email,))
            result = cur.fetchone()

        if result is None:
            return None  # User not found

        user_id, name, email, password_hash = result
        if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return {
                "id": user_id,
                "name": name,
                "email": email,
                "role": "ong"
            }
        else:
            return None  # Password mismatch
        
    def create_case(self, data):
        if not self.conn:
            raise Exception("No database connection.")
        try: 
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO cases (
                        "name", 
                        photo_url, 
                        age,
                        date_birth, 
                        place_birth, 
                        gender, 
                        distinctive_features, 
                        eyes_color, 
                        hair_description, 
                        complexion, 
                        weight, 
                        height,
                        date_missing, 
                        last_seen_location, 
                        forced_dissapearence, 
                        description, 
                        status, 
                        reporting_entity_contact, 
                        relatives_contact, 
                        help_files,
                        reported_by
                    )
                    VALUES (
                        %(name)s, 
                        %(photo_url)s, 
                        %(age)s, 
                        %(date_birth)s,
                        %(place_birth)s, 
                        %(gender)s, 
                        %(distinctive_features)s, 
                        %(eyes_color)s, 
                        %(hair_description)s, 
                        %(complexion)s, 
                        %(weight)s, 
                        %(height)s, 
                        %(date_missing)s, 
                        %(last_seen_location)s, 
                        %(forced_dissapearence)s, 
                        %(description)s, 
                        %(status)s, 
                        %(reporting_entity_contact)s,
                        %(relatives_contact)s,
                        %(help_files)s,
                        %(reported_by)s)
                    returning id;"""
                    , data)
                user_id = cur.fetchone()[0]
                self.conn.commit()
                return user_id
        except (Exception, psycopg2.DatabaseError) as e:
            self.conn.rollback()
            print(e)
            return None
        
    def get_case_by_id(self, case_id: str):
        if not self.conn:
            raise Exception("No database connection.")

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        id,
                        name,
                        photo_url,
                        age integer,
                        date_birth,
                        place_birth,
                        gender,
                        distinctive_features,
                        eyes_color,
                        hair_description,
                        complexion,
                        weight,
                        height,
                        date_missing,
                        last_seen_location,
                        forced_dissapearence,
                        description,
                        status,
                        reporting_entity_contact,
                        relatives_contact,
                        help_files,
                        reported_by,
                        created_at
                    FROM cases
                    WHERE id = %s;
                """, (case_id,))
                row = cur.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "photo_url": row[2],
                        "age integer": row[3],
                        "date_birth": row[4],
                        "place_birth": row[5],
                        "gender": row[6],
                        "distinctive_features": row[7],
                        "eyes_color": row[8],
                        "hair_description": row[9],
                        "complexion": row[10],
                        "weight": row[11],
                        "height": row[12],
                        "date_missing": row[13],
                        "last_seen_location": row[14],
                        "forced_dissapearence": row[15],
                        "description": row[16],
                        "status": row[17],
                        "reporting_entity_contact": row[18],
                        "relatives_contact": row[19],
                        "help_files": row[20],
                        "reported_by": row[21],
                        "created_at": row[22],
                    }
                else:
                    return None

        except Exception as e:
            print("Error fetching case:", e)
            return None
        

    def get_all_cases_with_filter(self, gender=None, status=None, reported_by=None, created_at=None, date_missing=None):
        if not self.conn:
            raise Exception("No database connection.")

        try:
            query ="""
                SELECT * FROM cases
                WHERE 1=1
            """
            params = {}

            if gender:
                query += "AND gender = %(gender)s"
                params["gender"] = gender
            if status:
                query += "AND status = %(status)s"
                params["status"] = status
            if reported_by:
                query += "AND reported_by = %(reported_by)s"
                params["reported_by"] = reported_by
            if created_at:
                query += "AND created_at = %(created_at)s"
                params["created_at"] = created_at
            if date_missing:
                query += "AND date_missing = %(date_missing)s"
                params["date_missing"] = date_missing

            query += " ORDER BY created_at DESC;"
            
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

                cases = []
                for row in rows:
                    case = {
                        "id": row[0],
                        "name": row[1],
                        "photo_url": row[2],
                        "age integer": row[3],
                        "date_birth": row[4],
                        "place_birth": row[5],
                        "gender": row[6],
                        "distinctive_features": row[7],
                        "eyes_color": row[8],
                        "hair_description": row[9],
                        "complexion": row[10],
                        "weight": row[11],
                        "height": row[12],
                        "date_missing": row[13],
                        "last_seen_location": row[14],
                        "forced_dissapearence": row[15],
                        "description": row[16],
                        "status": row[17],
                        "reporting_entity_contact": row[18],
                        "relatives_contact": row[19],
                        "help_files": row[20],
                        "created_at": row[21],
                        "updated_at": row[22],
                        "reported_by": row[23],
                    }
                    cases.append(case)
                return cases

        except Exception as e:
            print("Error fetching case:", e)
            return None

    def update_case_by_id(self, case_id:str, data:dict):
        if not self.conn:
            raise Exception("No database connection.")
        try: 
            with self.conn.cursor() as cur:
                cur.execute("""
                    UPDATE cases SET 
                        name = %(name)s, 
                        photo_url = %(photo_url)s,
                        age = %(age)s,
                        date_birth = %(date_birth)s, 
                        place_birth = %(place_birth)s,
                        gender = %(gender)s,
                        distinctive_features = %(distinctive_features)s, 
                        eyes_color = %(eyes_color)s, 
                        hair_description = %(hair_description)s, 
                        complexion = %(complexion)s, 
                        weight = %(weight)s, 
                        height = %(height)s,
                        date_missing = %(date_missing)s,
                        last_seen_location = %(last_seen_location)s, 
                        forced_dissapearence = %(forced_dissapearence)s, 
                        description = %(description)s, 
                        status = %(status)s,
                        reporting_entity_contact = %(reporting_entity_contact)s, 
                        relatives_contact = %(relatives_contact)s, 
                        help_files = %(help_files)s,
                        reported_by = %(reported_by)s
                    WHERE id = %(case_id)s
                """, {
                    "case_id": case_id,
                    "name": data.get("name"),
                    "photo_url": data.get("photo_url"),
                    "age": data.get("age"),
                    "date_birth": data.get("date_birth"),
                    "place_birth": data.get("place_birth"),
                    "gender": data.get("gender"),
                    "distinctive_features": data.get("distinctive_features"),
                    "eyes_color": data.get("eyes_color"),
                    "hair_description": data.get("hair_description"),
                    "complexion": data.get("complexion"),
                    "weight": data.get("weight"),
                    "height": data.get("height"),
                    "date_missing": data.get("date_missing"),
                    "last_seen_location": data.get("last_seen_location"),
                    "forced_dissapearence": data.get("forced_dissapearence"),
                    "description": data.get("description"),
                    "status": data.get("status"),
                    "reporting_entity_contact": data.get("reporting_entity_contact"),
                    "relatives_contact": data.get("relatives_contact"),
                    "help_files": data.get("help_files"),
                    "reported_by": data.get("reported_by")
                })
                self.conn.commit()
                if cur.rowcount == 0:
                    return None # No cases to update
                return case_id
        except (Exception, psycopg2.DatabaseError) as e:
            self.conn.rollback()
            print(e)
            return None
        
    def get_risk_data_by_id(self, case_id: str):
        if not self.conn:
            raise Exception("No database connection.")

        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        id,
                        name,
                        age,
                        gender,
                        date_missing,
                        last_seen_location,
                        created_at
                    FROM cases
                    WHERE id = %s;
                """, (case_id,))
                row = cur.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "age": row[2],
                        "gender": row[3],
                        "date_missing": row[4],
                        "last_seen_location": row[5],
                        "created_at": row[6],
                    }
                else:
                    return None

        except Exception as e:
            print("Error fetching case:", e)
            return None
        
    def insert_risk_level(self,case_id:str, risk_level: str):
        if not self.conn:
            raise Exception("No database connection.")
        try: 
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO risk_assessments
                        (case_id, risk_level, confidence_score, model_version)
                    VALUES
                        ( %(case_id)s, %(risk_level)s, 1.0, 'XGBoost 1.0')
                    ON CONFLICT (case_id)
                    DO UPDATE SET risk_level = EXCLUDED.risk_level
                    returning id
                """, {
                    "case_id": case_id,
                    "risk_level": risk_level.lower()
                })
                risk_id = cur.fetchone()[0]
                self.conn.commit()
                return risk_id
        except (Exception, psycopg2.DatabaseError) as e:
            self.conn.rollback()
            print(e)
            return None
        
    def insert_text_prediction(self,data:dict, case_id:str):
        if not self.conn:
            raise Exception("No database connection.")
        try: 
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO public.text_analysis_assessments
                    (case_id, toxic, severe_toxic, obscene, threat, insult, identity_hate, confidence_score, model_version)
                    VALUES
                        (%(case_id)s, %(toxic)s, %(severe_toxic)s, %(obscene)s, %(threat)s, %(insult)s, %(identity_hate)s, 1.0, 'RNN 1.0')
                    ON CONFLICT (case_id)
                    DO UPDATE SET toxic = EXCLUDED.toxic,
                    severe_toxic = EXCLUDED.severe_toxic,
                    obscene = EXCLUDED.obscene,
                    threat = EXCLUDED.threat,
                    insult = EXCLUDED.insult,
                    identity_hate = EXCLUDED.identity_hate
                    returning id
                """, {
                    "case_id": case_id,
                    "toxic": data.get("toxic"), 
                    "severe_toxic": data.get("severe_toxic"), 
                    "obscene": data.get("obscene"), 
                    "threat": data.get("threat"), 
                    "insult": data.get("insult"), 
                    "identity_hate": data.get("identity_hate")
                })
                text_id = cur.fetchone()[0]
                self.conn.commit()
                return text_id
        except (Exception, psycopg2.DatabaseError) as e:
            self.conn.rollback()
            print(e)
            return None
        

    def get_metrics(self):
        current_year = datetime.now().year
        if not self.conn:
            raise Exception("No database connection.")

        try:
            with self.conn.cursor() as cur:
            # 1. Total de casos
                cur.execute("SELECT COUNT(*) FROM cases;")
                total_cases = cur.fetchone()[0]

                # 2. Casos con perspectiva de género
                cur.execute("SELECT COUNT(*) FROM cases WHERE gender = 'female';")
                gender_cases = cur.fetchone()[0]

                # 3. Casos de riesgo
                cur.execute("SELECT COUNT(*) FROM risk_assessments WHERE risk_level = 'high';")
                high_risk_cases = cur.fetchone()[0]

                # 4. Casos activos
                cur.execute("SELECT COUNT(*) FROM cases WHERE status = 'open';")
                active_cases = cur.fetchone()[0]

                # 5. Casos de desaparición forzada
                cur.execute("SELECT COUNT(*) FROM cases WHERE forced_dissapearence = TRUE;")
                forced_disappearance_cases = cur.fetchone()[0]

                # 6. Casos de mujeres con texto tóxico en la descripción
                cur.execute("""
                    SELECT COUNT(*)
                    FROM cases c
                    JOIN text_analysis_assessments t ON c.id = t.case_id
                    WHERE c.gender = 'mujer'
                    AND (
                        t.toxic = TRUE OR
                        t.severe_toxic = TRUE OR
                        t.obscene = TRUE OR
                        t.threat = TRUE OR
                        t.insult = TRUE OR
                        t.identity_hate = TRUE
                    );
                """)
                toxic_women_cases = cur.fetchone()[0]

                # 7. Casos reportados por mes este año
                cur.execute("""
                    SELECT EXTRACT(MONTH FROM created_at)::int AS month, COUNT(*)
                    FROM cases
                    WHERE EXTRACT(YEAR FROM created_at) = %s
                    GROUP BY month
                    ORDER BY month;
                """, (current_year,))
                monthly_data = cur.fetchall()
                monthly_counts = {calendar.month_name[month]: count for month, count in monthly_data}

                # 8. Tiempo promedio de reporte (en horas)
                cur.execute("""
                    SELECT AVG(EXTRACT(EPOCH FROM (created_at - date_missing))/3600)
                    FROM cases
                    WHERE created_at IS NOT NULL AND date_missing IS NOT NULL;
                """)
                avg_hours_to_report = cur.fetchone()[0]

                # 9. Casos por mes y estado
                cur.execute("""
                    SELECT 
                        EXTRACT(MONTH FROM created_at)::int AS month,
                        SPLIT_PART(last_seen_location, '-', 2) AS estado,
                        COUNT(*) 
                    FROM cases
                    WHERE EXTRACT(YEAR FROM created_at) = %s
                    GROUP BY month, estado
                    ORDER BY estado, month;
                """, (current_year,))
                rows = cur.fetchall()
                cases_by_state_month = {}
                for month, estado, count in rows:
                    estado = estado.strip().title()
                    mes = calendar.month_name[month]
                    if estado not in cases_by_state_month:
                        cases_by_state_month[estado] = {}
                    cases_by_state_month[estado][mes] = count

                 # Porcentajes de texto tóxico por categoría
                cur.execute("SELECT COUNT(*) FROM text_analysis_assessments")
                total_texts = cur.fetchone()[0] or 1  # evitar división por cero

                toxicity_metrics = {}
                for field in ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]:
                    cur.execute(f"SELECT COUNT(*) FROM text_analysis_assessments WHERE {field} = TRUE")
                    count = cur.fetchone()[0]
                    toxicity_metrics[field] = round((count / total_texts) * 100, 2)

                cur.close()

                return {
                    "total_cases": total_cases,
                    "gender_perspective_cases": gender_cases,
                    "high_risk_cases": high_risk_cases,
                    "active_cases": active_cases,
                    "forced_disappearance_cases": forced_disappearance_cases,
                    "toxic_description_women_cases": toxic_women_cases,
                    "cases_reported_by_month": monthly_counts,
                    "cases_by_state_month": cases_by_state_month,
                    "avg_hours_to_report": round(avg_hours_to_report, 2) if avg_hours_to_report else None,
                    "text_toxicity_percentages": toxicity_metrics
                }
        except Exception as e:
            print("Error fetching case:", e)
            return None
        
    def __del__(self):
        self.conn.close()