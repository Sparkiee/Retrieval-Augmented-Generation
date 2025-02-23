import spacy
from spacy import displacy
import mysql.connector
import re
from openai import OpenAI

# load env api keys
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("No API key found")


class QueryParser:
    def __init__(self, text):
        res = re.findall(r"\b\d+k\b", text.lower())
        for match in res:
            text = text.replace(match, f"${int(match[:-1]) * 1000}")
        self.text = text
        self.nlp = spacy.load("en_core_web_sm")
        self.doc = self.nlp(text)
        self.car_brands = [
            "Abarth",
            "Alfa Romeo",
            "Aston Martin",
            "Audi",
            "Bentley",
            "BMW",
            "Bugatti",
            "Cadillac",
            "Chevrolet",
            "Chrysler",
            "Citroën",
            "Dacia",
            "Daewoo",
            "Daihatsu",
            "Dodge",
            "Donkervoort",
            "DS",
            "Ferrari",
            "Fiat",
            "Fisker",
            "Ford",
            "Honda",
            "Hummer",
            "Hyundai",
            "Infiniti",
            "Iveco",
            "Jaguar",
            "Jeep",
            "Kia",
            "KTM",
            "Lada",
            "Lamborghini",
            "Lancia",
            "Land Rover",
            "Landwind",
            "Lexus",
            "Lotus",
            "Maserati",
            "Maybach",
            "Mazda",
            "McLaren",
            "Mercedes-Benz",
            "Mercedes",
            "MG",
            "Mini",
            "Mitsubishi",
            "Morgan",
            "Nissan",
            "Opel",
            "Peugeot",
            "Porsche",
            "Renault",
            "Rolls-Royce",
            "Rover",
            "Saab",
            "Seat",
            "Skoda",
            "Smart",
            "SsangYong",
            "Subaru",
            "Suzuki",
            "Tesla",
            "Toyota",
            "Volkswagen",
            "Volvo",
        ]
        self.fuel_types = ["Petrol", "Diesel", "Electric", "Hybrid", "EV", "PULP 95"]
        self.negation = ["not", "no", "without", "exclude", "excluding"]
        self.greater = [
            "above",
            "more than",
            "greater than",
            "higher than",
            "over",
            "exceeding",
        ]
        self.lesser = [
            "below",
            "less than",
            "lower than",
            "under",
            "beneath",
            "not exceeding",
        ]
        self.equal = [
            "equal to",
            "same as",
            "equal",
            "same",
            "around",
            "approximately",
            "about",
            "near",
            "nearly",
            "close to",
            "just over",
            "just under",
            "just above",
            "just below",
        ]
        self.query_information = {
            "brand": None,
            "model": None,
            "production_year": None,
            "price_min": None,
            "price_max": None,
            "price_avg": None,
            "fuel_type": None,
            "gear_type": None,
            "excluded_brands": [],
            "excluded_fuel_types": [],
            "excluded_gear_types": [],
        }
        self.money_signs = ["$", "€", "£", "₪"]
        self.money_names = ["dollar", "euro", "pound", "shekel"]
        self.gears = ["manual", "automatic", "dual-clutch", "CVT", "DSG", "SMG", "AMT"]
        self.parse_query()

    def price_parser(self, token):
        return int(token.text.replace(",", ""))

    def parse_query(self):
        for sent in self.doc.sents:
            for token in sent:
                if token.text.lower() in self.negation:
                    context = self.doc[
                        token.i : min(len(self.doc), token.i + 5)
                    ].text.lower()
                    for brand in self.car_brands:
                        if brand.lower() in context:
                            self.query_information["excluded_brands"].append(brand)
                    for fuel in self.fuel_types:
                        if fuel.lower() in context:
                            self.query_information["excluded_fuel_types"].append(fuel)
                    for gear in self.gears:
                        if gear.lower() in context:
                            self.query_information["excluded_gear_types"].append(gear)

                if token.text.lower() in [brand.lower() for brand in self.car_brands]:
                    if token.text.lower() not in [
                        excluded.lower()
                        for excluded in self.query_information["excluded_brands"]
                    ]:
                        self.query_information["brand"] = token.text
                        next_token = token.nbor()
                        if next_token.is_alpha or (
                            not next_token.is_alpha and not next_token.like_num
                        ):
                            self.query_information["model"] = next_token.text
                            if (
                                next_token.nbor().like_num
                                and len(next_token.nbor().text) == 4
                            ):
                                self.query_information["production_year"] = (
                                    next_token.nbor().text
                                )
                        elif next_token.like_num and len(next_token.text) == 4:
                            self.query_information["production_year"] = next_token.text
                        else:
                            self.query_information["model"] = None

                if token.text.lower() in [
                    fuel.lower() for fuel in self.fuel_types
                ] and token.text.lower() not in [
                    excluded.lower()
                    for excluded in self.query_information["excluded_fuel_types"]
                ]:
                    self.query_information["fuel_type"] = token.text

                if token.text.lower() in [
                    gear.lower() for gear in self.gears
                ] and token.text.lower() not in [
                    excluded.lower()
                    for excluded in self.query_information["excluded_gear_types"]
                ]:
                    self.query_information["gear_type"] = token.text

                if token.like_num:
                    context = self.doc[max(0, token.i - 5) : token.i].text.lower()
                    for keyword in self.greater:
                        if keyword in context:
                            self.query_information["price_min"] = self.price_parser(
                                token
                            )
                    for keyword in self.lesser:
                        if keyword in context:
                            self.query_information["price_max"] = self.price_parser(
                                token
                            )
                    for keyword in self.equal:
                        if keyword in context:
                            self.query_information["price_avg"] = self.price_parser(
                                token
                            )

    def get_query_information(self):
        return self.query_information

    def process_query(self):
        db_config = {
            "host": os.getenv("MYSQL_HOST"),
            "user": os.getenv("MYSQL_USER"),
            "password": os.getenv("MYSQL_PASSWORD"),
            "database": os.getenv("MYSQL_DATABASE"),
        }
        
        print("DB Config: ", db_config)
        cursor = None
        result = []

        try:
            # connecting to database using config
            conn = mysql.connector.connect(**db_config)
            print("Connected to MySQL Database")
            # creating a cursor object using the cursor() method, which is used to execute SQL queries
            cursor = conn.cursor()

            info = self.get_query_information()
            # building the query
            query = "SELECT * FROM vehicles WHERE "
            if info["brand"]:
                query += f"brand = '{info['brand']}'"
            if info["model"]:
                query += f" AND model = '{info['model']}'"
            if info["production_year"]:
                query += f" AND prodyear = '{info['production_year']}'"
            if info["fuel_type"]:
                query += f" AND fuel = '{info['fuel_type']}'"
            if info["price_avg"]:
                query += f" AND price BETWEEN {info['price_avg'] - 2000} AND {info['price_avg'] + 2000}"
            else:
                if info["price_min"]:
                    query += f" AND price > {info['price_min']}"
                if info["price_max"]:
                    query += f" AND price < {info['price_max']}"
            query += "LIMIT 5"        
            cursor.execute(query)
            result = cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL Platform: {e}")
            
        finally:  # closing database connection & cursor
            cursor.close()
            conn.close()

        prompt = "I have the following vehicular options for you: \n"

        for option in result:
            prompt += f"{option}\n"
        prompt += "Which one of those would you say is the best option wise? Fuel economy, price, comfort and etc with all factors considered?"
        prompt += " I need you to write me a simple single line of response which only includes the vehicle and it's details. For example: 'Hyundai i20 2012'. Make sure you include the year of the model in your response"
        if len(result) == 0:
            prompt += "There were no vehicular options found from our database. Recommend me something based on the original request instead which is: " + self.text

        client = OpenAI()

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a vehicle recommendation assistant. Respond concisely and provide only the vehicle information per the user's request.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        return completion.choices[0].message.content
